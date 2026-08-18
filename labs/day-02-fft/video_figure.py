"""
Day 2: the phone-shaped version of the uncertainty figure.

uncertainty.py makes the honest 6-panel figure for the repo. On a phone it is
unreadable. This drops the middle window entirely and keeps only the two extremes,
big, vertical, and labelled with the verdict so nobody has to interpret an axis.

Run:  python labs/day-02-fft/video_figure.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from uncertainty import (FS, TONE_A, TONE_B, build_signal,
                         resolves_clicks, resolves_notes)

OUT = Path(__file__).parent / "out"

SHOW = [128, 8192]
LABELS = ["TINY CHUNKS\n2.9 ms", "BIG CHUNKS\n186 ms"]
DB_RANGE = 70

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
GOOD = "#6ee7a8"
BAD = "#ff6b8a"


def main():
    OUT.mkdir(exist_ok=True)
    x, _ = build_signal()

    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG,
        "text.color": FG, "axes.labelcolor": FG,
        "xtick.color": FG, "ytick.color": FG,
        "axes.edgecolor": "#3a3350", "font.size": 15,
    })

    # 1080 x 1920 at 100 dpi
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 19.2))
    fig.suptitle("same sound.\ntwo different chunk sizes.",
                 fontsize=32, color=FG, y=0.985, va="top", linespacing=1.35)

    for col, n in enumerate(SHOW):
        # --- the two clicks, 20 ms apart ---
        ax = axes[0, col]
        spec, sfreqs, stimes, im = ax.specgram(
            x, NFFT=n, Fs=FS, noverlap=n * 3 // 4, cmap="magma")
        top = im.get_clim()[1]
        im.set_clim(top - DB_RANGE, top)
        ax.set_xlim(0.56, 0.67)
        ax.set_ylim(2000, 12000)
        ax.set_title(LABELS[col], fontsize=24, color=ACCENT, pad=14, linespacing=1.25)
        ax.set_xticks([])
        ax.set_yticks([])
        good = resolves_clicks(spec, sfreqs, stimes)
        ax.text(0.5, -0.09, "2 CLICKS ✓" if good else "1 SMEAR ✗",
                transform=ax.transAxes, ha="center", fontsize=27,
                color=GOOD if good else BAD, weight="bold")

        # --- the two notes, 20 Hz apart ---
        ax = axes[1, col]
        chunk = x[int(0.10 * FS):int(0.10 * FS) + n] * np.hanning(n)
        mag = np.abs(np.fft.rfft(chunk))
        db = 20 * np.log10(mag / mag.max() + 1e-12)
        freqs = np.fft.rfftfreq(n, 1 / FS)
        ax.plot(freqs, db, lw=3.5, color=ACCENT)
        for f in (TONE_A, TONE_B):
            ax.axvline(f, color="#5a5175", ls=":", lw=1.6)
        ax.set_xlim(370, 530)
        ax.set_ylim(-55, 8)
        ax.set_xticks([])
        ax.set_yticks([])
        good = resolves_notes(x, n)
        if not good:
            ax.text(0.5, 0.45, "only ~1 data point\nin this whole range",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=17, color="#7a7196", style="italic", linespacing=1.4)
        ax.text(0.5, -0.09, "2 NOTES ✓" if good else "1 BLOB ✗",
                transform=ax.transAxes, ha="center", fontsize=27,
                color=GOOD if good else BAD, weight="bold")

    axes[0, 0].set_ylabel("WHEN did it happen?", fontsize=23, color=FG, labelpad=18)
    axes[1, 0].set_ylabel("WHAT were the notes?", fontsize=23, color=FG, labelpad=18)

    fig.text(0.5, 0.026, "no chunk size gets both.", ha="center",
             fontsize=30, color=FG, weight="bold")

    fig.subplots_adjust(top=0.845, bottom=0.105, hspace=0.22, wspace=0.09)
    fig.savefig(OUT / "video_uncertainty.png", dpi=100, facecolor=BG)
    print(f"wrote {OUT / 'video_uncertainty.png'}  (1080 x 1920)")


if __name__ == "__main__":
    main()
