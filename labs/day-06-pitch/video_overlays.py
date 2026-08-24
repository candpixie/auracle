"""
Day 6: small transparent overlays, for moments that should sit ON the face-cam
rather than replace it.

Full-frame cards cut away from the person talking, which is right for a big
reveal and wrong for a number mentioned in passing. These are PNGs with an alpha
channel, sized to drop into a third of the frame.

  overlay_zero.png     no energy at 200 Hz
  overlay_yin.png      the two algorithms disagreeing
  overlay_0001.png     0.9989 vs 0.9990

All are 1080 wide so they line up with a 1080x1920 timeline without scaling.
Place them inside the safe area: roughly y 300-800 px for an upper third, or
y 1000-1450 px for a lower third.

Run:  python labs/day-06-pitch/video_overlays.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, DIM, FG, GOOD, apply, display, text

apply()
OUT = Path(__file__).parent / "out"

PANEL = "#12101c"          # near-opaque so text stays readable over any footage
EDGE = "#3a3350"


def card(name, height_px, draw):
    """A transparent-background PNG, 1080 wide, with one rounded panel on it."""
    fig = plt.figure(figsize=(10.8, height_px / 100), facecolor="none")
    fig.patches.append(FancyBboxPatch(
        (0.035, 0.06), 0.93, 0.88, transform=fig.transFigure,
        boxstyle="round,pad=0.012,rounding_size=0.022",
        facecolor=PANEL, edgecolor=EDGE, lw=2.5, alpha=0.94))
    draw(fig)
    fig.savefig(OUT / name, dpi=100, transparent=True)
    plt.close(fig)
    print(f"  {name}  (1080 x {height_px})")


def zero(fig):
    fig.text(0.5, 0.80, "energy at 200 Hz", ha="center", va="top",
             **text(26), color=DIM)
    fig.text(0.5, 0.60, "0.000000", ha="center", va="center",
             **display(72, "bold"), color=BAD)
    fig.text(0.5, 0.20, "not small. zero.", ha="center", va="center",
             **display(30), color=FG)


def yin(fig):
    rows = [("what your ear says", "200 Hz", GOOD),
            ("YIN", "200 Hz", GOOD),
            ("the simple version", "100 Hz", BAD)]
    for i, (label, value, colour) in enumerate(rows):
        y = 0.76 - i * 0.235
        fig.text(0.10, y, label, **text(25), color=DIM, va="center")
        fig.text(0.90, y, value, **display(34, "bold"), color=colour,
                 ha="right", va="center")


def one_ten_thousandth(fig):
    fig.text(0.5, 0.88, "how close was it?", ha="center", va="top",
             **text(24), color=DIM)
    rows = [("200 Hz", "0.9989", "correct", GOOD),
            ("100 Hz", "0.9990", "what it picked", BAD)]
    for i, (hz, score, note, colour) in enumerate(rows):
        y = 0.60 - i * 0.235
        fig.text(0.10, y, hz, **text(27), color=FG, va="center")
        fig.text(0.585, y, score, **display(40, "bold"), color=colour,
                 ha="right", va="center")
        fig.text(0.63, y, note, **text(21), color=DIM, va="center")
    fig.text(0.5, 0.10, "it lost by 0.0001", ha="center", va="center",
             **display(32, "bold"), color=ACCENT)


def main():
    OUT.mkdir(exist_ok=True)
    print("transparent overlays, 1080 wide:")
    card("overlay_zero.png", 460, zero)
    card("overlay_yin.png", 520, yin)
    card("overlay_0001.png", 620, one_ten_thousandth)
    print()
    print("drop these on a layer ABOVE the face-cam. keep them inside")
    print("y 300-800 px (upper third) or y 1000-1450 px (lower third).")


if __name__ == "__main__":
    main()
