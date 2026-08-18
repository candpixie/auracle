"""
Day 2: what "breaking it into chunks" actually looks like.

For the explanation lines, before any results appear. One real waveform, sliced
into chunks, with the chunk width growing from ~6 ms to ~370 ms and back. The
striped background is the chunk grid; the bright band is the chunk the computer
is currently looking at.

Run:  python labs/day-02-fft/video_chunking.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from uncertainty import FS, CLICK_TIMES, build_signal

OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_chunk"

T0, T1 = 0.40, 0.90          # the window we show, containing both clicks
N_MIN, N_MAX = 256, 16384
STEPS = 60
FPS = 30

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
WAVE = "#e8e3f5"
HILITE = "#6ee7a8"


def render(x, n, idx, sweep):
    dt = n / FS
    t = np.arange(len(x)) / FS
    sel = (t >= T0) & (t <= T1)
    tv, xv = t[sel], x[sel]

    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG,
                         "text.color": FG, "axes.edgecolor": "#3a3350"}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("the computer can't\nhear all of it at once.", fontsize=33,
                     color=FG, y=0.975, va="top", linespacing=1.35)

        ax = fig.add_axes([0.09, 0.30, 0.86, 0.50])

        # chunk grid, drawn as an image so the count doesn't matter for speed
        grid = (np.floor(tv / dt) % 2).reshape(1, -1)
        ax.imshow(grid, aspect="auto", cmap="Greys", alpha=0.10,
                  extent=[T0, T1, -1.15, 1.15], origin="lower", zorder=0)

        # the chunk currently being looked at
        edges = np.arange(np.floor(T0 / dt), np.ceil(T1 / dt) + 1) * dt
        edges = edges[(edges >= T0 - dt) & (edges <= T1 + dt)]
        # only sweep over chunks that actually START inside the window, or the
        # highlight walks off the right edge and disappears
        inside = edges[(edges >= T0) & (edges < T1)]
        if len(inside):
            k = min(int(sweep * len(inside)), len(inside) - 1)
            ax.axvspan(inside[k], min(inside[k] + dt, T1), color=HILITE,
                       alpha=0.30, zorder=1)
            ax.axvline(inside[k], color=HILITE, lw=2.5, zorder=4)
            ax.axvline(min(inside[k] + dt, T1), color=HILITE, lw=2.5, zorder=4)
        for e in edges:
            ax.axvline(e, color="#4a4266", lw=1.2, zorder=2)

        ax.plot(tv, xv, lw=1.1, color=WAVE, zorder=3)
        for ct in CLICK_TIMES:
            ax.plot(ct, 1.02, "v", ms=13, color=ACCENT, zorder=4)

        ax.set_xlim(T0, T1)
        ax.set_ylim(-1.15, 1.15)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel("half a second of sound", fontsize=21, color=FG, labelpad=16)

        n_chunks = max(1, int(round((T1 - T0) / dt)))
        fig.text(0.5, 0.235, f"chunk = {dt * 1000:.0f} ms", ha="center", va="top",
                 fontsize=34, color=FG, weight="bold")
        fig.text(0.5, 0.180, f"{n_chunks} chunk{'s' if n_chunks != 1 else ''} "
                             f"in half a second", ha="center", va="top",
                 fontsize=25, color=ACCENT)
        fig.text(0.5, 0.085, "it looks at one chunk at a time.\nthat's the whole problem.",
                 ha="center", va="top", fontsize=28, color=FG, linespacing=1.45)

        fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
        plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    x, _ = build_signal()
    up = np.unique(np.round(np.logspace(np.log2(N_MIN), np.log2(N_MAX),
                                        STEPS, base=2)).astype(int))
    sizes = np.concatenate([up, up[::-1][1:-1]])

    for i, n in enumerate(sizes):
        render(x, int(n), i, (i % 12) / 11.0)      # the highlight sweeps as we go
        if i % 20 == 0:
            print(f"  frame {i}/{len(sizes)}")

    mp4 = OUT / "day02_chunking.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({len(sizes) / FPS:.1f} s, 1080x1920, loops)")


if __name__ == "__main__":
    main()
