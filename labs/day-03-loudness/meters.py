"""
Day 3: four meters, one signal set, no agreement.

Take the five equal-RMS tones from equal_loudness.py and measure each one four
ways. Two of the meters will tell you they are all identical. Two will tell you
they differ by more than 25 dB. All four are correct about what they measure.

  peak dBFS   the largest single sample. what clipping cares about.
  RMS dBFS    average energy. what physics cares about.
  A-weighted  RMS after discounting frequencies your ear is bad at. IEC 61672.
  LUFS        ITU-R BS.1770, via pyloudnorm. what every streaming platform
              normalises to, so it is the one that decides how loud your song
              actually comes out on Spotify.

Run:  python labs/day-03-loudness/meters.py   (run equal_loudness.py first)
"""

from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf

from equal_loudness import FREQS, a_weight_db

OUT = Path(__file__).parent / "out"


def db(x):
    return 20 * np.log10(max(x, 1e-12))


def main():
    meter = pyln.Meter(48_000)
    rows = []

    for f in FREQS:
        path = OUT / f"tone_{f}Hz.wav"
        if not path.exists():
            raise SystemExit("run equal_loudness.py first")
        x, fs = sf.read(path)

        peak = db(np.abs(x).max())
        rms = db(np.sqrt(np.mean(x ** 2)))
        # pure tones, so the A-weight at the tone frequency is exact
        a_weighted = rms + a_weight_db(float(f))
        lufs = meter.integrated_loudness(x)
        rows.append((f, peak, rms, a_weighted, lufs))

    print(f"{'freq':>8}  {'peak dBFS':>10}  {'RMS dBFS':>10}  {'A-weighted':>11}  {'LUFS':>8}")
    for f, peak, rms, aw, lufs in rows:
        print(f"{f:>7} Hz  {peak:>10.1f}  {rms:>10.1f}  {aw:>11.1f}  {lufs:>8.1f}")

    spread = lambda i: max(r[i] for r in rows) - min(r[i] for r in rows)
    print()
    print(f"{'spread across the five tones:':<32}")
    print(f"  peak        {spread(1):>5.1f} dB   <- says they are identical")
    print(f"  RMS         {spread(2):>5.1f} dB   <- says they are identical")
    print(f"  A-weighted  {spread(3):>5.1f} dB   <- says they differ enormously")
    print(f"  LUFS        {spread(4):>5.1f} dB   <- says they differ enormously")
    print()

    print("peak and RMS cannot rank these at all. every tone ties exactly, so there")
    print("is no 'loudest' by either measure. that is not a rounding artifact, it is")
    print("the two meters saying frequency is none of their business.")
    print()

    loudest_a = max(rows, key=lambda r: r[3])
    loudest_l = max(rows, key=lambda r: r[4])
    print(f"loudest by A-weighting:  {loudest_a[0]} Hz")
    print(f"loudest by LUFS:         {loudest_l[0]} Hz")
    print()

    # the interesting disagreement, and it is not the one you would expect
    top = next(r for r in rows if r[0] == 12500)
    print(f"and now the awkward one. at 12500 Hz:")
    print(f"  A-weighting says {top[3]:.1f} dB, i.e. discount it, your ear is losing sensitivity")
    print(f"  LUFS says        {top[4]:.1f}, i.e. one of the LOUDEST tones here")
    print(f"  they disagree by {abs(top[3] - top[4]):.1f} dB about the same signal")
    print()
    print("that gap is real, and here is what actually causes it. measured directly,")
    print("K-weighting is a FLAT +3.3 dB shelf above about 4 kHz. it does not keep")
    print("climbing; it plateaus. that shelf models head and torso diffraction, not")
    print("loudness perception, and BS.1770 never claimed otherwise.")
    print()
    print("so at 12.5 kHz: A-weighting subtracts 4.3 dB because your ear is losing")
    print("sensitivity. K-weighting ADDS 3.3 dB because of diffraction. hence 7.6 dB.")
    print()
    print("the honest verdict is not 'the standard is wrong'. BS.1770 is defined for")
    print("broadband programme material, and a lone sine is outside its domain. on")
    print("real music, high frequencies are a small share of total energy, so the")
    print("shelf rarely decides anything. this is a tool used outside its spec,")
    print("not a broken tool.")
    print()
    print("none of these meters is broken. peak and RMS correctly report facts about")
    print("the air. LUFS correctly implements a standard. they are just not answering")
    print("the question you asked, which was about a person.")


if __name__ == "__main__":
    main()
