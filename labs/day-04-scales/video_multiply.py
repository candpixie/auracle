"""
Day 4: "multiplying, not adding", animated.

For the lines about why an even-sounding scale curves on a computer. Notes appear
one at a time on a linear frequency axis, and the gaps visibly grow. Then the same
notes on a log axis, where they are evenly spaced.

Nothing here is stylised: the note frequencies are 12-tone equal temperament, and
the gap labels are the real differences in Hz.

Run:  python labs/day-04-scales/video_multiply.py [seconds]
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

apply()
OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_mult"
FPS = 30

C3 = 130.81
N = 37                                   # C3 to C6
FREQS = C3 * 2 ** (np.arange(N) / 12)
OCTAVES = [0, 12, 24, 36]


def render(idx, shown, show_gaps):
    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("going up one note\nMULTIPLIES the frequency.",
                     **display(33, "bold"), color=FG, y=0.978, va="top",
                     linespacing=1.35)
        fig.text(0.5, 0.878, "it doesn't add to it.", ha="center", va="top",
                 **text(24), color=DIM)

        # ---- linear axis: the gaps grow ----
        ax = fig.add_axes([0.21, 0.470, 0.68, 0.350])
        for i in range(shown):
            ax.plot([0, 1], [FREQS[i]] * 2, lw=2.5,
                    color=ACCENT if i not in OCTAVES else FG,
                    alpha=0.35 if i not in OCTAVES else 1.0)
        ax.set_ylim(100, 1120)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([FREQS[o] for o in OCTAVES if o < max(shown, 1)])
        ax.set_yticklabels([f"{FREQS[o]:.0f} Hz" for o in OCTAVES
                            if o < max(shown, 1)], **text(19))
        ax.set_ylabel("what the computer sees", **text(20), color=ACCENT, labelpad=14)
        for sp in ax.spines.values():
            sp.set_visible(False)

        if show_gaps:
            for a, b in zip(OCTAVES, OCTAVES[1:]):
                if b >= shown:
                    break
                gap = FREQS[b] - FREQS[a]
                ax.annotate("", xy=(0.62, FREQS[b]), xytext=(0.62, FREQS[a]),
                            xycoords=ax.get_yaxis_transform(),
                            arrowprops=dict(arrowstyle="<->", color=BAD, lw=2.4))
                ax.text(0.66, np.sqrt(FREQS[a] * FREQS[b]), f"+{gap:.0f} Hz",
                        transform=ax.get_yaxis_transform(), va="center",
                        **display(23, "bold"), color=BAD)

        # ---- log axis: the same notes, evenly spaced ----
        ax2 = fig.add_axes([0.21, 0.165, 0.68, 0.215])
        for i in range(shown):
            ax2.plot([0, 1], [FREQS[i]] * 2, lw=2.5,
                     color=GOOD if i not in OCTAVES else FG,
                     alpha=0.35 if i not in OCTAVES else 1.0)
        ax2.set_yscale("log")
        ax2.set_ylim(100, 1120)
        ax2.set_xlim(0, 1)
        ax2.set_xticks([])
        ax2.set_yticks([FREQS[o] for o in OCTAVES])
        ax2.set_yticklabels([f"{FREQS[o]:.0f}" for o in OCTAVES], **text(17))
        ax2.set_ylabel("what you hear", **text(20), color=GOOD, labelpad=14)
        for sp in ax2.spines.values():
            sp.set_visible(False)

        if show_gaps:
            fig.text(0.5, 0.115, "same notes. now they're even.", ha="center",
                     va="top", **display(27), color=GOOD)
            fig.text(0.5, 0.035, "each octave DOUBLES.", ha="center",
                     **display(31, "bold"), color=FG)

        fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
        plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 11.0
    n_frames = int(total * FPS)
    build_until = 0.62                      # fraction of the clip spent adding notes

    for i in range(n_frames):
        t = i / n_frames
        shown = min(N, int(np.ceil(N * min(1.0, t / build_until))))
        render(i, shown, show_gaps=t > build_until * 0.55)
        if i % 50 == 0:
            print(f"  frame {i}/{n_frames}")

    mp4 = OUT / "day04_multiply.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)

    print(f"\nwrote {mp4}  ({n_frames / FPS:.1f} s, 1080x1920)")
    print("\noctave gaps on a linear axis, which is the whole point:")
    for a, b in zip(OCTAVES, OCTAVES[1:]):
        print(f"  {FREQS[a]:>7.1f} -> {FREQS[b]:>7.1f} Hz   gap +{FREQS[b] - FREQS[a]:.0f}")


if __name__ == "__main__":
    main()
