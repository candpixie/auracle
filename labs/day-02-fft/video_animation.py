"""
Day 2: the tradeoff, animated.

A still figure shows two chunk sizes. This slides continuously between them so you
can watch the clicks sharpen while the notes blur, and then the reverse. Same
signal throughout, only the chunk size changes.

Everything on screen is computed from the real signal. Renders frames, then calls
ffmpeg. Output is 1080x1920 mp4, loopable.

Run:  python labs/day-02-fft/video_animation.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from uncertainty import (FS, TONE_A, TONE_B, build_signal,
                         resolves_clicks, resolves_notes)

OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames"

N_MIN, N_MAX = 64, 16384
STEPS = 90          # frames on the way up; the animation ping-pongs, so 180 total
FPS = 30

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
GOOD = "#6ee7a8"
BAD = "#ff6b8a"
DB_RANGE = 70


DARK = {
    "figure.facecolor": BG, "axes.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG,
    "xtick.color": FG, "ytick.color": FG,
    "axes.edgecolor": "#3a3350", "savefig.facecolor": BG,
}


def render_frame(x, n, idx):
    dt_ms = n / FS * 1000
    df_hz = FS / n

    with plt.rc_context(DARK):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("one sound.\nsliding the chunk size.", fontsize=32, color=FG,
                     y=0.985, va="top", linespacing=1.35)

        # explicit positions. gridspec + a readout between panels is not worth
        # the arithmetic, and the last version silently overlapped two labels.
        ax_top = fig.add_axes([0.14, 0.575, 0.79, 0.285])
        ax_bot = fig.add_axes([0.14, 0.235, 0.79, 0.285])
        ax_bar = fig.add_axes([0.14, 0.095, 0.79, 0.010])

        # ---- WHEN: the two clicks, 20 ms apart ----
        spec, sfreqs, stimes, im = ax_top.specgram(
            x, NFFT=n, Fs=FS, noverlap=n * 3 // 4, cmap="magma")
        top = im.get_clim()[1]
        im.set_clim(top - DB_RANGE, top)
        clicks_ok = resolves_clicks(spec, sfreqs, stimes)
        ax_top.set_xlim(0.56, 0.67)
        ax_top.set_ylim(2000, 12000)
        ax_top.set_xticks([]); ax_top.set_yticks([])
        ax_top.set_ylabel("WHEN did it happen?", fontsize=22, labelpad=16)
        fig.text(0.535, 0.545, "2 CLICKS \u2713" if clicks_ok else "1 SMEAR \u2717",
                 ha="center", va="top", fontsize=27,
                 color=GOOD if clicks_ok else BAD, weight="bold")

        # ---- WHAT: the two notes, 20 Hz apart ----
        start = int(0.10 * FS)
        chunk = x[start:start + n] * np.hanning(n)
        mag = np.abs(np.fft.rfft(chunk))
        db = 20 * np.log10(mag / mag.max() + 1e-12)
        freqs = np.fft.rfftfreq(n, 1 / FS)
        notes_ok = resolves_notes(x, n)
        ax_bot.plot(freqs, db, lw=3.5, color=ACCENT)
        for f in (TONE_A, TONE_B):
            ax_bot.axvline(f, color="#5a5175", ls=":", lw=1.6)
        ax_bot.set_xlim(370, 530)
        ax_bot.set_ylim(-55, 8)
        ax_bot.set_xticks([]); ax_bot.set_yticks([])
        ax_bot.set_ylabel("WHAT were the notes?", fontsize=22, labelpad=16)
        fig.text(0.535, 0.205, "2 NOTES \u2713" if notes_ok else "1 BLOB \u2717",
                 ha="center", va="top", fontsize=27,
                 color=GOOD if notes_ok else BAD, weight="bold")

        # ---- readout and slider ----
        fig.text(0.535, 0.150, f"chunk = {dt_ms:.1f} ms", ha="center", va="top",
                 fontsize=30, color=FG, weight="bold")

        ax_bar.set_xlim(np.log2(N_MIN), np.log2(N_MAX))
        ax_bar.set_ylim(0, 1)
        ax_bar.axhline(0.5, color="#3a3350", lw=6, solid_capstyle="round")
        ax_bar.plot(np.log2(n), 0.5, "o", ms=22, color=ACCENT, zorder=5, clip_on=False)
        ax_bar.set_xticks([]); ax_bar.set_yticks([])
        for spine in ax_bar.spines.values():
            spine.set_visible(False)
        fig.text(0.14, 0.068, "tiny chunks", fontsize=18, color="#7a7196")
        fig.text(0.93, 0.068, "big chunks", fontsize=18, color="#7a7196", ha="right")

        fig.text(0.5, 0.026, "no chunk size gets both.", ha="center",
                 fontsize=29, color=FG, weight="bold")

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

    # log-spaced window sizes, then back again so the clip loops seamlessly
    up = np.unique(np.round(np.logspace(np.log2(N_MIN), np.log2(N_MAX),
                                        STEPS, base=2)).astype(int))
    sizes = np.concatenate([up, up[::-1][1:-1]])

    for i, n in enumerate(sizes):
        render_frame(x, int(n), i)
        if i % 20 == 0:
            print(f"  frame {i}/{len(sizes)}  (chunk {n} samples)")

    mp4 = OUT / "day02_tradeoff.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920", str(mp4),
    ], check=True)
    shutil.rmtree(FRAMES)

    secs = len(sizes) / FPS
    print(f"\nwrote {mp4}  ({secs:.1f} s, 1080x1920, loops)")


if __name__ == "__main__":
    main()
