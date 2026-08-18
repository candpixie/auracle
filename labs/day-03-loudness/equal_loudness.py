"""
Day 3: five tones with identical measurements that are not equally loud.

Amplitude is a fact about the air. Loudness is a fact about you. They are not the
same quantity, and the gap between them is frequency-dependent: your ear is most
sensitive around 3 to 4 kHz and falls off badly at the bottom and top.

This makes five tones with EXACTLY the same RMS amplitude. A meter says they are
identical. Play them and they are obviously not.

Run:  python labs/day-03-loudness/equal_loudness.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT = Path(__file__).parent / "out"

FS = 48_000
DURATION = 2.0
RMS = 0.1                       # every tone gets this exact RMS. no exceptions.
FREQS = [63, 250, 1000, 4000, 12500]


def a_weight_db(f):
    """
    A-weighting, IEC 61672. A closed-form curve that approximates the inverse of
    the 40-phon equal-loudness contour, which is to say: the standard's guess at
    how sensitive your ear is at each frequency.

    It is defined to be exactly 0 dB at 1 kHz, which is a useful thing to assert
    against.
    """
    f = np.asarray(f, dtype=float)
    num = (12194.0 ** 2) * f ** 4
    den = ((f ** 2 + 20.6 ** 2)
           * np.sqrt((f ** 2 + 107.7 ** 2) * (f ** 2 + 737.9 ** 2))
           * (f ** 2 + 12194.0 ** 2))
    return 20 * np.log10(num / den) + 2.00


def tone(freq, fs=FS, dur=DURATION, rms=RMS):
    t = np.arange(int(fs * dur)) / fs
    x = np.sin(2 * np.pi * freq * t)
    x *= rms / np.sqrt(np.mean(x ** 2))     # force the exact RMS
    n = int(fs * 0.02)
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def main():
    OUT.mkdir(exist_ok=True)

    # the curve is defined to be 0 dB at 1 kHz. check, don't trust.
    assert abs(a_weight_db(1000.0)) < 0.05, "A-weighting should be 0 dB at 1 kHz"

    sequence = []
    print(f"{'freq':>8}  {'RMS':>10}  {'A-weight':>10}  {'so it sounds':>14}")
    for f in FREQS:
        x = tone(f)
        sf.write(OUT / f"tone_{f}Hz.wav", x, FS)
        sequence.append(x)
        sequence.append(np.zeros(int(FS * 0.4)))     # gap between tones

        aw = a_weight_db(f)
        verdict = "about right" if aw > -3 else ("quieter" if aw > -20 else "MUCH quieter")
        print(f"{f:>7} Hz  {np.sqrt(np.mean(x ** 2)):>10.4f}  {aw:>+9.1f} dB  {verdict:>14}")

    sf.write(OUT / "all_five_tones.wav", np.concatenate(sequence), FS)

    # the curve, with our five tones marked on it
    f = np.logspace(np.log10(20), np.log10(20000), 800)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.semilogx(f, a_weight_db(f), lw=2, color="#7c5cff",
                label="A-weighting (the standard's model of your ear)")
    ax.axhline(0, color="k", lw=0.8, alpha=0.3)
    for tf in FREQS:
        aw = a_weight_db(float(tf))
        ax.plot(tf, aw, "o", ms=9, color="#ff5c8a", zorder=5)
        ax.annotate(f"{tf} Hz\n{aw:+.0f} dB", (tf, aw), textcoords="offset points",
                    xytext=(0, -34), ha="center", fontsize=9)
    ax.set_xlim(20, 20000)
    ax.set_ylim(-60, 10)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("how much your ear discounts it (dB)")
    ax.set_title("all five tones have identical RMS.\nyour ear applies this curve to them anyway.",
                 fontsize=12)
    ax.grid(which="both", alpha=0.15)
    ax.legend(loc="lower center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "a_weighting.png", dpi=150)

    print()
    print("every one of those has the same RMS to 4 decimal places.")
    print("play all_five_tones.wav. the 63 Hz one is nearly inaudible and the")
    print("4 kHz one is piercing, and no meter reading distinguishes them.")


if __name__ == "__main__":
    main()
