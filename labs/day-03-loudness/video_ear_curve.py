"""
Day 3: the ear's sensitivity curve, animated.

For the lines about the ear not being equally sensitive at every pitch. The curve
draws itself left to right, then the peak and the low-end falloff get called out.

The curve is A-weighting (IEC 61672), which approximates the inverse of the 40-phon
equal-loudness contour. Higher on this plot means your ear is MORE sensitive there.

Run:  python labs/day-03-loudness/video_ear_curve.py [seconds]
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from equal_loudness import a_weight_db

OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_ear"
FPS = 30

F_LO, F_HI = 20.0, 20_000.0

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
HOT = "#ff6b8a"
COOL = "#6ee7a8"


def render(idx, draw_frac, show_peak, show_low):
    f = np.logspace(np.log10(F_LO), np.log10(F_HI), 900)
    y = a_weight_db(f)
    n = max(2, int(draw_frac * len(f)))

    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG,
                         "text.color": FG, "axes.labelcolor": FG,
                         "xtick.color": FG, "ytick.color": FG,
                         "axes.edgecolor": "#3a3350", "font.size": 17}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("your ears aren't equally\nsensitive at every pitch.",
                     fontsize=33, color=FG, y=0.978, va="top", linespacing=1.35)

        ax = fig.add_axes([0.16, 0.325, 0.78, 0.505])

        # full curve as a faint guide, so the axes never jump
        ax.semilogx(f, y, lw=2, color="#2a2440")
        ax.semilogx(f[:n], y[:n], lw=5, color=ACCENT, solid_capstyle="round")

        peak_f = f[np.argmax(y)]
        peak_y = y.max()

        if show_peak:
            ax.plot(peak_f, peak_y, "o", ms=20, color=HOT, zorder=6)
            ax.annotate("MOST SENSITIVE\nhere", (peak_f, peak_y),
                        textcoords="offset points", xytext=(-8, -95),
                        ha="center", fontsize=21, color=HOT, weight="bold",
                        linespacing=1.35)
            ax.axvspan(2000, 5000, color=HOT, alpha=0.10)

        if show_low:
            ax.axvspan(F_LO, 200, color=COOL, alpha=0.12)
            ax.annotate("you barely\nhear it down here",
                        (48, a_weight_db(48.0)), textcoords="offset points",
                        xytext=(112, 250), ha="center", fontsize=20, color=COOL,
                        weight="bold", linespacing=1.35,
                        arrowprops=dict(arrowstyle="->", color=COOL, lw=2.5,
                                        shrinkA=14, shrinkB=6,
                                        connectionstyle="arc3,rad=0.30"))

        ax.set_xlim(F_LO, F_HI)
        ax.set_ylim(-62, 14)
        ax.set_xticks([100, 1000, 10000])
        ax.set_xticklabels(["100 Hz", "1 kHz", "10 kHz"], fontsize=19)
        ax.set_yticks([])
        ax.set_ylabel("how well you hear it", fontsize=22, labelpad=18)
        ax.grid(which="both", axis="x", alpha=0.12)

        if show_peak:
            fig.text(0.5, 0.250, f"peak: {peak_f / 1000:.1f} kHz", ha="center",
                     va="top", fontsize=30, color=HOT, weight="bold")
            fig.text(0.5, 0.196,
                     "same range as a crying baby,\nand the consonants in speech.",
                     ha="center", va="top", fontsize=23, color=FG, linespacing=1.45)

        if show_low:
            fig.text(0.5, 0.104, "the 63 Hz tone was 26 dB down\nbefore it reached you.",
                     ha="center", va="top", fontsize=25, color=COOL, linespacing=1.4)

        fig.text(0.5, 0.020, "same energy. different loudness.", ha="center",
                 fontsize=28, color=FG, weight="bold")

        fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
        plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 9.0
    n_frames = int(total * FPS)

    # phases as fractions of the clip: draw, hold, peak, low
    draw_end = 0.42
    peak_at = 0.50
    low_at = 0.74

    for i in range(n_frames):
        t = i / n_frames
        frac = min(1.0, t / draw_end)
        render(i, frac, show_peak=t >= peak_at, show_low=t >= low_at)
        if i % 40 == 0:
            print(f"  frame {i}/{n_frames}")

    mp4 = OUT / "day03_ear_curve.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({n_frames / FPS:.1f} s, 1080x1920)")
    print(f"peak sensitivity at {np.logspace(np.log10(F_LO), np.log10(F_HI), 900)[np.argmax(a_weight_db(np.logspace(np.log10(F_LO), np.log10(F_HI), 900)))]:.0f} Hz")


if __name__ == "__main__":
    main()
