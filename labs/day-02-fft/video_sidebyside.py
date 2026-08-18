"""
Day 2: the side-by-side, animated, for the "this side / while this side" line.

video_animation.py slides one chunk size at a time. That is the wrong shape for a
sentence that compares two things at once. This holds both columns on screen and
moves the attention: left half lights up while the right dims, then the reverse.

Panels are computed once and reused, so the render is quick.

Run:  python labs/day-02-fft/video_sidebyside.py [seconds]
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from uncertainty import (FS, TONE_A, TONE_B, build_signal,
                         resolves_clicks, resolves_notes)

OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_sbs"

COLS = [128, 8192]
HEAD = ["TINY CHUNKS\n2.9 ms", "BIG CHUNKS\n186 ms"]
FPS = 30
DB_RANGE = 70

BG = "#0d0b14"
FG = "#f2eef7"
ACCENT = "#b39cff"
GOOD = "#6ee7a8"
BAD = "#ff6b8a"


def precompute(x):
    """Everything each column needs, computed once."""
    panels = []
    for n in COLS:
        fig, ax = plt.subplots()
        spec, sfreqs, stimes, _ = ax.specgram(x, NFFT=n, Fs=FS, noverlap=n * 3 // 4)
        plt.close(fig)

        fsel = (sfreqs >= 2000) & (sfreqs <= 12000)
        tsel = (stimes >= 0.56) & (stimes <= 0.67)
        img = 10 * np.log10(spec[np.ix_(fsel, tsel)] + 1e-20)

        chunk = x[int(0.10 * FS):int(0.10 * FS) + n] * np.hanning(n)
        mag = np.abs(np.fft.rfft(chunk))
        db = 20 * np.log10(mag / mag.max() + 1e-12)
        freqs = np.fft.rfftfreq(n, 1 / FS)

        panels.append({
            "img": img,
            "extent": [0.56, 0.67, 2000, 12000],
            "freqs": freqs, "db": db,
            "clicks": resolves_clicks(spec, sfreqs, stimes),
            "notes": resolves_notes(x, n),
        })
    return panels


def render(panels, idx, active):
    """active: 0 = left lit, 1 = right lit, None = both."""
    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG,
                         "text.color": FG, "axes.edgecolor": "#3a3350"}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("same sound.\ntwo different chunk sizes.", fontsize=32,
                     color=FG, y=0.985, va="top", linespacing=1.35)

        for col, p in enumerate(panels):
            x0 = 0.10 + col * 0.455
            ax_t = fig.add_axes([x0, 0.575, 0.395, 0.245])
            ax_b = fig.add_axes([x0, 0.255, 0.395, 0.245])

            top = p["img"].max()
            ax_t.imshow(p["img"], aspect="auto", origin="lower", cmap="magma",
                        extent=p["extent"], vmin=top - DB_RANGE, vmax=top)
            ax_t.set_xticks([]); ax_t.set_yticks([])

            ax_b.plot(p["freqs"], p["db"], lw=3.2, color=ACCENT)
            for f in (TONE_A, TONE_B):
                ax_b.axvline(f, color="#5a5175", ls=":", lw=1.5)
            ax_b.set_xlim(370, 530); ax_b.set_ylim(-55, 8)
            ax_b.set_xticks([]); ax_b.set_yticks([])

            cx = x0 + 0.1975
            fig.text(cx, 0.868, HEAD[col], ha="center", va="top", fontsize=23,
                     color=ACCENT, linespacing=1.25)
            fig.text(cx, 0.548, "2 CLICKS ✓" if p["clicks"] else "1 SMEAR ✗",
                     ha="center", va="top", fontsize=25,
                     color=GOOD if p["clicks"] else BAD, weight="bold")
            fig.text(cx, 0.228, "2 NOTES ✓" if p["notes"] else "1 BLOB ✗",
                     ha="center", va="top", fontsize=25,
                     color=GOOD if p["notes"] else BAD, weight="bold")

        fig.text(0.055, 0.697, "WHEN", rotation=90, va="center", fontsize=21, color=FG)
        fig.text(0.055, 0.377, "WHAT", rotation=90, va="center", fontsize=21, color=FG)

        # dim the column that isn't being talked about
        if active is not None:
            dim_x = 0.53 if active == 0 else 0.02
            fig.patches.append(Rectangle((dim_x, 0.19), 0.45, 0.71,
                                         transform=fig.transFigure,
                                         facecolor=BG, alpha=0.78, zorder=20))
            lit_x = 0.06 if active == 0 else 0.515
            fig.patches.append(Rectangle((lit_x, 0.19), 0.45, 0.71,
                                         transform=fig.transFigure, fill=False,
                                         edgecolor=ACCENT, lw=3, zorder=21))
            caption = ("catches the clicks.\nloses the notes." if active == 0
                       else "catches the notes.\nloses the clicks.")
            fig.text(0.5, 0.145, caption, ha="center", va="top", fontsize=31,
                     color=FG, linespacing=1.45, zorder=22)

        fig.text(0.5, 0.030, "no chunk size gets both.", ha="center",
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

    total = float(sys.argv[1]) if len(sys.argv) > 1 else 11.0
    panels = precompute(build_signal()[0])

    # both -> left -> both -> right -> both, as fractions of the clip
    plan = [(0.08, None), (0.34, 0), (0.08, None), (0.34, 1), (0.16, None)]
    schedule = []
    for frac, active in plan:
        schedule += [active] * max(1, round(frac * total * FPS))

    for i, active in enumerate(schedule):
        render(panels, i, active)
        if i % 40 == 0:
            print(f"  frame {i}/{len(schedule)}")

    mp4 = OUT / "day02_sidebyside.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)
    print(f"\nwrote {mp4}  ({len(schedule) / FPS:.1f} s, 1080x1920)")


if __name__ == "__main__":
    main()
