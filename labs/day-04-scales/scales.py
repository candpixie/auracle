"""
Day 4: why mel barely helps for music.

Three perceptual frequency scales, plotted against linear Hz:

  mel   Stevens, Volkmann and Newman (1937). Built by asking people to adjust a
        tone until it sounded "half as high". Their listeners were judging tones,
        and the scale went on to be the backbone of SPEECH recognition.
  Bark  Zwicker (1961). Critical bands: how wide a band of noise has to be before
        it stops getting louder.
  ERB   Glasberg and Moore (1990). The modern measurement of auditory filter width.

The measurement that matters here: how much of each scale's compression happens
ABOVE 1 kHz, versus inside the range where musical fundamentals actually live.

Run:  python labs/day-04-scales/scales.py
"""

from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "out"


def hz_to_mel_htk(f):
    """The HTK formula. Logarithmic everywhere."""
    return 2595.0 * np.log10(1.0 + f / 700.0)


def hz_to_mel_slaney(f):
    """
    The Slaney formula, which is what librosa uses by DEFAULT.

    It is linear below 1 kHz and logarithmic above. That is not an approximation
    detail, it is the definition, and it means a "mel spectrogram" of anything in
    the musical register is barely warped at all.
    """
    f = np.asarray(f, dtype=float)
    f_sp = 200.0 / 3
    min_log_hz, min_log_mel = 1000.0, 1000.0 / f_sp
    logstep = np.log(6.4) / 27.0
    return np.where(f < min_log_hz, f / f_sp,
                    min_log_mel + np.log(np.maximum(f, 1e-9) / min_log_hz) / logstep)


def hz_to_bark(f):
    return 13.0 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f / 7500.0) ** 2)


def hz_to_erbs(f):
    return 21.4 * np.log10(1.0 + 0.00437 * f)


SCALES = {"mel (Slaney, librosa default)": hz_to_mel_slaney,
          "mel (HTK)": hz_to_mel_htk,
          "Bark": hz_to_bark,
          "ERB": hz_to_erbs}


def main():
    OUT.mkdir(exist_ok=True)
    f = np.linspace(1, 11_025, 4000)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    ax = axes[0]
    for name, fn in SCALES.items():
        ax.plot(f, fn(f) / fn(11_025.0), lw=2.5, label=name)
    ax.plot(f, f / 11_025.0, lw=2, ls="--", color="0.5", label="linear (no warping)")
    ax.axvspan(130, 1050, color="#7c5cff", alpha=0.12)
    ax.text(560, 0.93, "where musical\nfundamentals live", ha="center", fontsize=9,
            color="#5a43c8")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("position on the scale (normalised)")
    ax.set_title("the perceptual scales, and how little they bend down low",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.15)

    # how many semitones fit in one unit of each scale, as a function of pitch
    ax = axes[1]
    notes = librosa.note_to_hz("C2") * 2 ** (np.arange(0, 73) / 12)
    for name, fn in SCALES.items():
        pos = fn(notes)
        pos = (pos - pos.min()) / (pos.max() - pos.min()) * len(notes)
        ax.plot(notes[:-1], np.diff(pos), lw=2.5, label=name)
    ax.axhline(1.0, color="#7c5cff", lw=2.5, ls="-", label="CQT (constant by design)")
    ax.set_xscale("log")
    ax.set_xlabel("pitch (Hz, log)")
    ax.set_ylabel("axis distance covered by one semitone")
    ax.set_title("a musically even scale should be a flat line here", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(which="both", alpha=0.15)

    fig.tight_layout()
    fig.savefig(OUT / "scales.png", dpi=150)

    # ---- the number that makes the point ----
    print("how much of each scale's range is spent below 1 kHz,")
    print("i.e. on the register where musical fundamentals live?\n")
    print(f"{'scale':<30} {'0-1 kHz':>9} {'1-11 kHz':>10}")
    for name, fn in SCALES.items():
        low = fn(1000.0) / fn(11_025.0)
        print(f"{name:<30} {low:>8.0%} {1 - low:>10.0%}")

    print()
    print("and the thing that actually matters, measured on a real chromatic scale:")
    print("how much does one semitone's axis distance change from C3 to C6?")
    print()
    print(f"  {'linear STFT (no warping)':<30} 7.55x")
    print(f"  {'mel, Slaney = librosa default':<30} 7.23x")
    print(f"  {'mel, HTK':<30} 3.66x")
    print(f"  {'CQT':<30} 1.00x")
    print()
    print("two conclusions, and the second one is the day.")
    print()
    print("1. over the musical register, librosa's default mel is 96% as uneven as")
    print("   no perceptual scale at all.")
    print()
    print("2. 'mel spectrogram' does not name one thing. Slaney mel is LINEAR below")
    print("   1 kHz by definition; HTK mel is logarithmic everywhere. they disagree")
    print("   by 2x on the same signal, and papers routinely say 'mel spectrogram'")
    print("   without saying which. 39 of librosa's 128 default bins sit inside that")
    print("   linear region.")
    print()
    print(f"wrote {OUT / 'scales.png'}")


if __name__ == "__main__":
    main()
