"""
Day 4: the mel scale is literally straight below 1000 Hz.

For the lines about librosa's default mel being linear in the register where
melodies live. The Slaney curve draws in, the straight portion below 1 kHz gets
called out, then the range of real instruments is overlaid on top of it.

Run:  python labs/day-04-scales/video_linear_region.py [seconds]
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

from scales import hz_to_mel_htk, hz_to_mel_slaney

apply()
OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_lin"
FPS = 30

F_MAX = 4000.0
BREAK = 1000.0          # where Slaney mel stops being linear, by definition

# lowest fundamental to highest, for instruments people actually write melodies on
RANGES = [("bass voice", 82, 350),
          ("guitar", 82, 660),
          ("soprano", 260, 1050),
          ("violin", 196, 2100)]


def render(idx, draw_frac, show_linear, show_ranges):
    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG,
                         "text.color": FG, "axes.edgecolor": "#3a3350",
                         "xtick.color": FG, "ytick.color": FG}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("the mel scale is supposed\nto bend like your ear.",
                     **display(32, "bold"), color=FG, y=0.978, va="top",
                     linespacing=1.35)

        ax = fig.add_axes([0.15, 0.500, 0.79, 0.320])
        f = np.linspace(1, F_MAX, 1600)
        y = hz_to_mel_slaney(f) / hz_to_mel_slaney(F_MAX)
        n = max(2, int(draw_frac * len(f)))

        if show_linear:
            ax.axvspan(0, BREAK, color=BAD, alpha=0.14)
            # a dead-straight reference through the linear stretch
            m = f <= BREAK
            ax.plot(f[m], y[m], lw=2.0, ls="--", color=FG, alpha=0.55)

        ax.plot(f[:n], y[:n], lw=5, color=ACCENT, solid_capstyle="round")
        ax.plot(f, y, lw=1.2, color="#2a2440", zorder=0)

        ax.set_xlim(0, F_MAX)
        ax.set_ylim(0, 1.02)
        ax.set_xticks([0, 1000, 2000, 3000, 4000])
        ax.set_xticklabels(["0", "1000", "2000", "3000", "4000"], **text(19))
        ax.set_yticks([])
        ax.set_xlabel("frequency (Hz)", **text(20), labelpad=10)
        ax.grid(axis="x", alpha=0.12)

        if show_linear:
            ax.annotate("perfectly straight", xy=(520, 0.30),
                        xytext=(1500, 0.17), **text(20), color=BAD,
                        arrowprops=dict(arrowstyle="->", color=BAD, lw=2.4))

        if show_ranges:
            ax2 = fig.add_axes([0.15, 0.238, 0.79, 0.150])
            for k, (name, lo, hi) in enumerate(RANGES):
                yk = len(RANGES) - k
                ax2.plot([lo, hi], [yk, yk], lw=13, color=GOOD,
                         solid_capstyle="round", alpha=0.85)
                ax2.text(hi + 110, yk, name, **text(18), color=FG, va="center")
            ax2.axvspan(0, BREAK, color=BAD, alpha=0.14)
            ax2.axvline(BREAK, color=BAD, lw=2, ls="--")
            ax2.set_xlim(0, F_MAX)
            ax2.set_ylim(0.3, len(RANGES) + 0.7)
            ax2.set_xticks([]); ax2.set_yticks([])
            for sp in ax2.spines.values():
                sp.set_visible(False)
            fig.text(0.15, 0.408, "where melodies actually sit",
                     **text(20), color=GOOD, va="top")

        if show_linear:
            fig.text(0.5, 0.178, "below 1000 Hz it doesn't bend", ha="center",
                     va="top", **display(29, "bold"), color=FG)
            fig.text(0.5, 0.128, "at all.", ha="center", va="top",
                     **display(29, "bold"), color=BAD)

        if show_ranges:
            fig.text(0.5, 0.058,
                     "so in the register music lives in,\nthe perceptual scale isn't perceptual.",
                     ha="center", va="top", **text(21), color=DIM, linespacing=1.45)

        fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
        plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
    n = int(total * FPS)
    for i in range(n):
        t = i / n
        render(i, min(1.0, t / 0.34), show_linear=t > 0.30, show_ranges=t > 0.58)
        if i % 40 == 0:
            print(f"  frame {i}/{n}")

    mp4 = OUT / "day04_linear_region.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({n / FPS:.1f} s, 1080x1920)")

    print("\nsanity check, Slaney mel spacing:")
    from scales import hz_to_mel_slaney as mel
    for a, b in ((100, 200), (400, 500), (900, 1000), (2000, 2100), (3000, 3100)):
        print(f"  {a:>5}->{b:<5} Hz   mel step {mel(float(b)) - mel(float(a)):6.2f}"
              f"   {'linear region' if b <= 1000 else ''}")


if __name__ == "__main__":
    main()
