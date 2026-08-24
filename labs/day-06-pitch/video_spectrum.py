"""
Day 6: the spectrum, animated, inside the Instagram safe area.

For the lines about what is actually in the file. The peaks appear one at a time
with their multiple-of-200 label, the empty 200 Hz slot gets called out, then the
waveform underneath shows the period that survives anyway.

Everything stays inside style.SAFE, because Reels overlays its own UI on the frame
and crops on some surfaces. Nothing near an edge.

Run:  python labs/day-06-pitch/video_spectrum.py [seconds]
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
from auracle.style import (ACCENT, BAD, BG, DIM, FG, GOOD, SAFE, apply,
                           display, safe_axes, safe_y, text)

from missing_fundamental import F0, SR, build

apply()
OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_spec"
FPS = 30

HARMONICS = [2, 3, 4, 5]


def render(idx, n_shown, show_empty, show_wave):
    x = build(range(2, 6))
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    mag /= mag.max()
    freqs = np.fft.rfftfreq(len(x), 1 / SR)

    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)

    fig.text(0.5, safe_y(0.995), "what's actually", ha="center", va="top",
             **display(36, "bold"), color=FG)
    fig.text(0.5, safe_y(0.945), "in the file", ha="center", va="top",
             **display(36, "bold"), color=FG)

    # ---- the spectrum ----
    ax = safe_axes(fig, 0.0, 0.46, 1.0, 0.42)
    band = freqs <= 1250
    ax.plot(freqs[band], mag[band], lw=1.4, color="#2a2440")

    for k in range(n_shown):
        h = HARMONICS[k]
        f = F0 * h
        m = (freqs >= f - 30) & (freqs <= f + 30)
        ax.plot(freqs[m], mag[m], lw=4, color=ACCENT)
        ax.text(f, mag[m].max() + 0.10, f"{h}x200", ha="center",
                **text(20), color=ACCENT)

    if show_empty:
        # label the empty slot from directly above it. an angled arrow from the
        # right crossed straight through the 400 Hz peak.
        ax.axvspan(F0 - 42, F0 + 42, color=BAD, alpha=0.22)
        ax.annotate("nothing\nhere", xy=(F0, 0.10), xytext=(F0, 0.62),
                    **text(20), color=BAD, ha="center", va="bottom",
                    linespacing=1.3,
                    arrowprops=dict(arrowstyle="->", color=BAD, lw=2.6,
                                    shrinkA=6, shrinkB=2))

    ax.set_xlim(0, 1250)
    ax.set_ylim(0, 1.30)
    ax.set_xticks([200, 400, 600, 800, 1000])
    ax.set_xticklabels(["200", "400", "600", "800", "1000"], **text(18))
    ax.set_yticks([])
    ax.set_xlabel("frequency (Hz)", **text(20), color=FG, labelpad=10)
    ax.grid(axis="x", alpha=0.10)

    # ---- the waveform, and its surviving period ----
    if show_wave:
        ax2 = safe_axes(fig, 0.0, 0.16, 1.0, 0.19)
        n = int(SR * 0.020)
        t_ms = np.arange(n) / SR * 1000
        seg = x[8000:8000 + n]
        ax2.plot(t_ms, seg, lw=2.4, color=GOOD)
        period_ms = 1000.0 / F0
        for k in range(1, 4):
            ax2.axvline(k * period_ms, color=FG, lw=1.6, ls=":", alpha=0.7)
        ax2.annotate("", xy=(2 * period_ms, 0.85), xytext=(period_ms, 0.85),
                     arrowprops=dict(arrowstyle="<->", color=FG, lw=2.2))
        ax2.text(1.5 * period_ms, 1.02, "one cycle", ha="center",
                 **text(18), color=FG)
        ax2.set_xlim(0, 20)
        ax2.set_ylim(-1.15, 1.35)
        ax2.set_xticks([]); ax2.set_yticks([])
        for sp in ax2.spines.values():
            sp.set_visible(False)
        fig.text(0.5, safe_y(0.125), "it still repeats 200 times a second",
                 ha="center", va="top", **display(25), color=GOOD)

    fig.text(0.5, safe_y(0.058), "your brain listens to the repeating,",
             ha="center", va="top", **text(21), color=DIM)
    fig.text(0.5, safe_y(0.022), "not the lowest thing present.",
             ha="center", va="top", **text(21), color=DIM)

    fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
    plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
    n = int(total * FPS)

    for i in range(n):
        t = i / n
        shown = min(len(HARMONICS), int(t / 0.34 * len(HARMONICS)) + 1)
        render(i, shown, show_empty=t > 0.40, show_wave=t > 0.62)
        if i % 50 == 0:
            print(f"  frame {i}/{n}")

    mp4 = OUT / "day06_spectrum.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({n / FPS:.1f} s, 1080x1920)")
    print(f"all text inside the safe box: "
          f"x {SAFE['left'] * 1080:.0f}-{SAFE['right'] * 1080:.0f} px, "
          f"y {(1 - SAFE['top']) * 1920:.0f}-{(1 - SAFE['bottom']) * 1920:.0f} px from top")


if __name__ == "__main__":
    main()
