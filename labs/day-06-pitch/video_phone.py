"""
Day 6: why a phone can play a bass line it cannot physically produce.

A square 1080x1080 animation, meant to sit in half the frame over the face-cam
rather than replace it. Three beats:

  1. the note tries to come out of a small speaker, and does not
  2. its harmonics do
  3. your brain puts the note back

One honesty note about the shaded region: this is schematic. Small speakers roll
off in the low hundreds of Hz, with the corner depending on the driver and the
enclosure, and I have not measured a specific phone. The claim being made is
"phone speakers cannot move enough air down here", which is true and which the
figure marks as approximate.

Run:  python labs/day-06-pitch/video_phone.py [seconds]
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

from missing_fundamental import F0

apply()
OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_phone"
FPS = 30

ROLLOFF = 380.0          # schematic: roughly where a small speaker gives up
HARMONICS = [2, 3, 4, 5]
HEIGHTS = {2: 0.88, 3: 0.70, 4: 0.55, 5: 0.44}


def render(idx, stage, pulse):
    fig = plt.figure(figsize=(10.8, 10.8), facecolor=BG)
    ax = fig.add_axes([0.11, 0.255, 0.82, 0.545])

    # the region a small speaker cannot reach
    ax.axvspan(0, ROLLOFF, color=BAD, alpha=0.16)
    ax.text(ROLLOFF / 2, 1.30, "a phone speaker\ncan't move air here",
            ha="center", va="center", **text(18), color=BAD, linespacing=1.3)

    # the note itself
    blocked = stage >= 1
    if not blocked:
        ax.plot([F0, F0], [0, 1.0], lw=9, color=DIM, alpha=0.8,
                solid_capstyle="round")
    else:
        # what actually gets out of the speaker: almost nothing
        ax.plot([F0, F0], [0, 0.07], lw=9, color=BAD, solid_capstyle="round")
        ax.plot(F0, 0.20, marker="x", ms=26, mew=5, color=BAD)

    # the harmonics, which do get out
    if stage >= 2:
        for h in HARMONICS:
            f = F0 * h
            ax.plot([f, f], [0, HEIGHTS[h]], lw=9, color=GOOD,
                    solid_capstyle="round")
            ax.text(f, HEIGHTS[h] + 0.07, f"{h}x", ha="center",
                    **text(18), color=GOOD)

    # your brain putting the note back
    if stage >= 3:
        a = 0.22 + 0.30 * pulse
        ax.plot([F0, F0], [0.10, 1.0], lw=20, color=ACCENT, alpha=a,
                solid_capstyle="round", zorder=0)
        ax.plot([F0, F0], [0.10, 1.0], lw=5, color=ACCENT, alpha=0.95,
                ls=(0, (6, 5)), solid_capstyle="butt", zorder=4)
        ax.text(F0, 1.06, "your brain", ha="center", **text(18), color=ACCENT)

    ax.set_xlim(0, 1180)
    ax.set_ylim(0, 1.52)
    ax.set_xticks([200, 400, 600, 800, 1000])
    ax.set_xticklabels(["200", "400", "600", "800", "1000"], **text(17))
    ax.set_yticks([])
    ax.set_xlabel("frequency (Hz)", **text(18), color=DIM, labelpad=8)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)

    lines = [
        ("your phone can't make this note", DIM),
        ("but it CAN make the harmonics", GOOD),
        ("so your brain puts the note back", ACCENT),
    ]
    label, colour = lines[min(stage, 2)] if stage else lines[0]
    fig.text(0.5, 0.125, label, ha="center", va="center",
             **display(30, "bold"), color=colour)
    fig.text(0.5, 0.052, "the bass you hear was never played",
             ha="center", va="center", **text(20), color=DIM)

    fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
    plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0
    n = int(total * FPS)
    for i in range(n):
        t = i / n
        stage = 0 if t < 0.16 else 1 if t < 0.40 else 2 if t < 0.66 else 3
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * (i / FPS) * 0.9)
        render(i, stage, pulse)
        if i % 50 == 0:
            print(f"  frame {i}/{n}")

    mp4 = OUT / "day06_phone.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1080", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({n / FPS:.1f} s, 1080x1080 square)")
    print("place it in half the frame, over the face-cam. it is square so it")
    print("works in the top half or the bottom half without cropping.")


if __name__ == "__main__":
    main()
