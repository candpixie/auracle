"""
Day 2: you cannot know when and what at the same time.

The FFT tells you which frequencies are present. To find out WHEN they were
present you chop the signal into short chunks and transform each one, which is
the STFT, and that is where the trap is.

  short chunks -> you know WHEN precisely, and WHAT vaguely
  long chunks  -> you know WHAT precisely, and WHEN vaguely

There is no window length that gives you both, and it is not an engineering
limitation anyone will fix. It falls out of the maths.

The test signal is built so the tradeoff is unmissable. It contains:

  - two steady tones 20 Hz apart (440 and 460 Hz). Separating them needs a window
    LONGER than 1/20 Hz = 50 ms.
  - two clicks 20 ms apart. Separating those needs a window SHORTER than 20 ms.

Those two requirements contradict each other. Whatever window you pick, the figure
loses one of them, and you can watch it happen.

Run:  python labs/day-02-fft/uncertainty.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT = Path(__file__).parent / "out"

FS = 44_100
DURATION = 1.5

TONE_A, TONE_B = 440.0, 460.0      # 20 Hz apart
CLICK_TIMES = (0.60, 0.62)         # 20 ms apart

WINDOWS = [128, 1024, 8192]        # samples
DB_RANGE = 70                      # same fixed-range habit as day 1. see the note
                                   # in day 1's README about why autoscaling hides bugs.


def build_signal():
    t = np.arange(int(FS * DURATION)) / FS

    # the two close tones, running the whole time
    x = 0.3 * np.sin(2 * np.pi * TONE_A * t) + 0.3 * np.sin(2 * np.pi * TONE_B * t)

    # two sharp clicks. broadband, so they show up at every frequency at once.
    for ct in CLICK_TIMES:
        i = int(ct * FS)
        x[i:i + 8] += 0.9

    return x, t


def main():
    OUT.mkdir(exist_ok=True)
    x, t = build_signal()
    sf.write(OUT / "uncertainty_signal.wav", x, FS)

    fig, axes = plt.subplots(2, len(WINDOWS), figsize=(15, 7.5),
                             gridspec_kw={"height_ratios": [1, 2]})

    for col, n in enumerate(WINDOWS):
        # resolution this window buys you, in each dimension
        dt_ms = n / FS * 1000
        df_hz = FS / n

        # top row: zoomed on the clicks, to see time resolution
        ax = axes[0, col]
        *_, im = ax.specgram(x, NFFT=n, Fs=FS, noverlap=n * 3 // 4, cmap="magma")
        top = im.get_clim()[1]
        im.set_clim(top - DB_RANGE, top)
        ax.set_xlim(0.55, 0.68)
        ax.set_ylim(2000, 12000)
        ax.set_title(f"window = {n} samples ({dt_ms:.1f} ms)\n"
                     f"time res {dt_ms:.1f} ms  ·  freq res {df_hz:.0f} Hz",
                     fontsize=10)
        ax.set_ylabel("the two CLICKS\n(20 ms apart)", fontsize=9)
        for ct in CLICK_TIMES:
            ax.axvline(ct, color="cyan", ls=":", lw=0.8, alpha=0.7)

        # bottom row: the spectrum of ONE window taken from the steady part, away
        # from the clicks. a spectrogram is the wrong plot here: the two tones beat
        # against each other at 20 Hz, and the beating dominates the picture. a
        # single slice answers the actual question, which is just "one peak or two".
        ax = axes[1, col]
        start = int(0.10 * FS)
        chunk = x[start:start + n] * np.hanning(n)
        mag = np.abs(np.fft.rfft(chunk))
        db = 20 * np.log10(mag / mag.max() + 1e-12)
        freqs = np.fft.rfftfreq(n, 1 / FS)

        ax.plot(freqs, db, lw=1.3, color="#7c5cff")
        ax.plot(freqs, db, "o", ms=3, color="#ff5c8a", label="FFT bins")
        for f in (TONE_A, TONE_B):
            ax.axvline(f, color="cyan", ls=":", lw=0.9, alpha=0.8)
        ax.set_xlim(360, 540)
        ax.set_ylim(-60, 5)
        ax.set_ylabel("the two TONES\n(20 Hz apart), dB", fontsize=9)
        ax.set_xlabel("frequency (Hz)")
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(alpha=0.15)

        n_peaks = "TWO peaks" if df_hz < 20 else "ONE blob"
        ax.text(0.03, 0.92, n_peaks, transform=ax.transAxes, fontsize=11,
                color="#7c5cff", weight="bold", va="top")

    fig.suptitle("you cannot know WHEN and WHAT at the same time\n"
                 "left: clicks resolved, tones merged.   right: tones resolved, clicks merged.",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "uncertainty.png", dpi=150)

    print("what each window buys you:\n")
    print(f"{'window':>8}  {'time res':>10}  {'freq res':>10}   {'product':>9}")
    for n in WINDOWS:
        dt_ms = n / FS * 1000
        df_hz = FS / n
        print(f"{n:>8}  {dt_ms:>8.1f} ms  {df_hz:>8.0f} Hz   {dt_ms * df_hz:>9.0f}")
    print()
    print("the product column never changes, and it is important to be honest about")
    print("why: it CANNOT change. time res is n/fs and freq res is fs/n, so the")
    print("product is 1 second-hertz no matter what n you pick. it is algebra, not")
    print("a measurement.")
    print()
    print("that is exactly what makes it a wall instead of an engineering problem.")
    print("you are never gaining resolution by choosing a better window. you are only")
    print("choosing which axis to spend a fixed budget on.")
    print()
    print(f"wrote {OUT / 'uncertainty.png'}")
    print("top row: can you count TWO clicks?   bottom row: can you count TWO lines?")
    print("no column manages both.")


if __name__ == "__main__":
    main()
