"""
Day 2, the payoff: why your ear is not stuck with the tradeoff.

The STFT picks ONE window length and uses it at every frequency. Your cochlea does
not. It behaves like a bank of filters whose bandwidth grows with centre frequency,
which is measured as the ERB (equivalent rectangular bandwidth):

    ERB(f) = 24.7 * (0.00437 * f + 1)        Glasberg and Moore, 1990

A wide filter settles fast, so its effective time resolution is roughly 1/ERB. Up
high the ear's filters are wide, so it gets millisecond timing. Down low they are
narrow, so it gets fine pitch discrimination. It spends its budget differently in
different places.

The STFT spends the same budget everywhere, and that is the whole limitation.

Run:  python labs/day-02-fft/cochlea_vs_stft.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "out"

FS = 44_100
STFT_N = 2048                      # one representative window choice

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
EAR = "#6ee7a8"
MACHINE = "#ff6b8a"


def erb(f):
    """Glasberg and Moore (1990) equivalent rectangular bandwidth, in Hz."""
    return 24.7 * (0.00437 * f + 1.0)


def main():
    OUT.mkdir(exist_ok=True)
    f = np.logspace(np.log10(50), np.log10(16000), 600)

    ear_ms = 1000.0 / erb(f)                      # wide filter settles fast
    stft_ms = np.full_like(f, STFT_N / FS * 1000)  # same window at every frequency

    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "text.color": FG,
        "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
        "axes.edgecolor": "#3a3350", "font.size": 17,
    })

    fig = plt.figure(figsize=(10.8, 19.2))
    fig.suptitle("your ear doesn't pick\none chunk size.", fontsize=34, color=FG,
                 y=0.982, va="top", linespacing=1.35)

    ax = fig.add_axes([0.17, 0.285, 0.76, 0.565])
    ax.loglog(f, stft_ms, lw=5, color=MACHINE, label="the machine (one window)")
    ax.loglog(f, ear_ms, lw=5, color=EAR, label="your ear (ERB filter bank)")
    ax.fill_between(f, ear_ms, stft_ms, where=ear_ms < stft_ms,
                    color=EAR, alpha=0.10)

    for hz, txt in ((100, "100 Hz"), (1000, "1 kHz"), (8000, "8 kHz")):
        y = 1000.0 / erb(hz)
        ax.plot(hz, y, "o", ms=15, color=EAR, zorder=6)
        ax.annotate(f"{txt}\n{y:.0f} ms", (hz, y), textcoords="offset points",
                    xytext=(0, -78), ha="center", fontsize=17, color=EAR,
                    linespacing=1.3)

    ax.set_xlim(50, 16000)
    ax.set_ylim(0.5, 200)
    ax.set_xlabel("frequency", fontsize=21, labelpad=14)
    ax.set_ylabel("how sharply it can time an event  (ms)", fontsize=20, labelpad=14)
    ax.grid(which="both", alpha=0.12)
    ax.legend(loc="upper right", fontsize=18, facecolor=BG, edgecolor="#3a3350",
              labelcolor=FG)

    fig.text(0.5, 0.225,
             f"the machine: {STFT_N / FS * 1000:.0f} ms everywhere.",
             ha="center", fontsize=25, color=MACHINE, weight="bold")
    fig.text(0.5, 0.175,
             "your ear: 30 ms down low, 1 ms up high.",
             ha="center", fontsize=25, color=EAR, weight="bold")
    fig.text(0.5, 0.095,
             "sharp pitch where pitch lives.\nsharp timing where clicks live.",
             ha="center", fontsize=27, color=FG, linespacing=1.4)
    fig.text(0.5, 0.030, "it cheats. the STFT can't.",
             ha="center", fontsize=31, color=FG, weight="bold")

    fig.savefig(OUT / "video_cochlea.png", dpi=100, facecolor=BG)

    print(f"{'freq':>8}  {'ear (ms)':>10}  {'machine (ms)':>13}  {'ear is better by':>17}")
    for hz in (100, 250, 1000, 4000, 8000, 12000):
        e = 1000.0 / erb(hz)
        m = STFT_N / FS * 1000
        print(f"{hz:>7} Hz  {e:>10.1f}  {m:>13.1f}  {m / e:>16.1f}x")
    print()
    print(f"wrote {OUT / 'video_cochlea.png'}  (1080 x 1920)")


if __name__ == "__main__":
    main()
