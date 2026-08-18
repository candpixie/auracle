"""
Day 2: the "it's not a bug, it's math" card.

For the line in the video where you say nobody is going to fix this. The numbers
come from uncertainty.py, so the card cannot drift away from the lab.

Run:  python labs/day-02-fft/video_math_card.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from uncertainty import FS, WINDOWS

OUT = Path(__file__).parent / "out"

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
DIM = "#7a7196"


def main():
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({"figure.facecolor": BG, "text.color": FG})

    fig = plt.figure(figsize=(10.8, 19.2))
    fig.text(0.5, 0.93, "this isn't a bug.", ha="center", va="top",
             fontsize=44, color=FG, weight="bold")

    fig.text(0.5, 0.80, "time resolution", ha="center", fontsize=27, color=DIM)
    fig.text(0.5, 0.755, "×", ha="center", fontsize=34, color=ACCENT)
    fig.text(0.5, 0.715, "frequency resolution", ha="center", fontsize=27, color=DIM)
    fig.text(0.5, 0.645, "= 1", ha="center", fontsize=68, color=ACCENT, weight="bold")
    fig.text(0.5, 0.585, "always.", ha="center", fontsize=31, color=FG)

    # columns: the chunk you chose, then what it buys you on each axis.
    # (an earlier version printed the chunk in ms AND the time resolution in ms,
    # which are the same number twice.)
    y = 0.500
    fig.text(0.15, y, "chunk", fontsize=22, color=DIM)
    fig.text(0.52, y, "knows WHEN", fontsize=22, color=DIM, ha="center")
    fig.text(0.85, y, "knows WHAT", fontsize=22, color=DIM, ha="right")
    fig.add_artist(plt.Line2D([0.13, 0.87], [y - 0.020, y - 0.020],
                              color="#3a3350", lw=2))

    for i, n in enumerate(WINDOWS):
        row = y - 0.072 - i * 0.058
        fig.text(0.15, row, f"{n} samples", fontsize=27, color=FG, va="center")
        fig.text(0.52, row, f"{n / FS * 1000:.1f} ms", fontsize=28, color=FG,
                 ha="center", va="center")
        fig.text(0.85, row, f"{FS / n:.0f} Hz", fontsize=28, color=FG,
                 ha="right", va="center")

    fig.text(0.5, 0.245,
             "make one better\nand the other gets worse.\nexactly as much.",
             ha="center", va="top", fontsize=30, color=FG, linespacing=1.5)

    fig.text(0.5, 0.075, "it's algebra.", ha="center", fontsize=33, color=ACCENT,
             weight="bold")
    fig.text(0.5, 0.030, "nobody is fixing this.", ha="center", fontsize=33,
             color=FG, weight="bold")

    fig.savefig(OUT / "video_math.png", dpi=100, facecolor=BG)
    print(f"wrote {OUT / 'video_math.png'}  (1080 x 1920)")


if __name__ == "__main__":
    main()
