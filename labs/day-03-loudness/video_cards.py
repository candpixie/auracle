"""
Day 3: the phone-shaped cards.

Two 1080x1920 stills built from the real measurements in meters.py, so the cards
cannot drift away from the lab.

  video_meters.png    all four meters on the five tones. peak and RMS say
                      "identical"; the two perceptual ones do not.
  video_spotify.png   the 12.5 kHz disagreement on its own.

Run:  python labs/day-03-loudness/video_cards.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD as DIFF, BG, DIM as SAME, FG, GOOD, apply, display, text

from equal_loudness import FREQS, a_weight_db

OUT = Path(__file__).parent / "out"

apply()


def measure():
    meter = pyln.Meter(48_000)
    rows = []
    for f in FREQS:
        x, _ = sf.read(OUT / f"tone_{f}Hz.wav")
        rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)))
        rows.append({
            "f": f,
            "peak": 20 * np.log10(np.abs(x).max()),
            "rms": rms,
            "a": rms + a_weight_db(float(f)),
            "lufs": meter.integrated_loudness(x),
        })
    return rows


def card_meters(rows):
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.955, "five sounds.", ha="center", va="top",
             **display(42), color=FG, weight="bold")
    fig.text(0.5, 0.905, "identical on the meter.", ha="center", va="top",
             **display(30), color=SAME)

    cols = [(0.28, "peak"), (0.46, "rms"), (0.66, "a"), (0.86, "lufs")]
    heads = ["PEAK", "RMS", "A-WEIGHT", "LUFS"]
    subs = ["the air", "the air", "your ear", "spotify"]

    y = 0.815
    fig.text(0.045, y, "tone", **text(20), color=SAME, va="center")
    for (x, _), h, sub in zip(cols, heads, subs):
        fig.text(x, y + 0.012, h, **text(20), color=FG, ha="center", weight="bold")
        fig.text(x, y - 0.020, sub, **text(15), color=SAME, ha="center")
    fig.add_artist(plt.Line2D([0.035, 0.965], [y - 0.042, y - 0.042],
                              color="#3a3350", lw=2))

    for i, r in enumerate(rows):
        row = y - 0.098 - i * 0.058
        label = f"{r['f'] / 1000:g}k" if r["f"] >= 1000 else f"{r['f']}"
        fig.text(0.045, row, f"{label} Hz", **text(22), color=FG, va="center")
        for (x, key), in_air in zip(cols, [True, True, False, False]):
            fig.text(x, row, f"{r[key]:.1f}", **text(23), va="center", ha="center",
                     color=SAME if in_air else FG,
                     weight="normal" if in_air else "bold")

    spread = lambda k: max(r[k] for r in rows) - min(r[k] for r in rows)
    row = y - 0.098 - len(rows) * 0.058 - 0.030
    fig.add_artist(plt.Line2D([0.035, 0.965], [row + 0.030, row + 0.030],
                              color="#3a3350", lw=2))
    fig.text(0.045, row, "spread", **text(20), color=ACCENT, va="center")
    for (x, key) in cols:
        s = spread(key)
        fig.text(x, row, f"{s:.1f}", **text(25), va="center", ha="center",
                 color=SAME if s < 0.05 else DIFF, weight="bold")

    fig.text(0.5, 0.335, "the first two can't tell them apart at all.",
             ha="center", va="top", **text(26), color=SAME)
    fig.text(0.5, 0.275, "0.0 dB. every tone ties exactly.",
             ha="center", va="top", **text(29), color=FG, weight="bold")
    fig.text(0.5, 0.175, "but you can hear the difference\nimmediately.",
             ha="center", va="top", **display(32), color=FG, linespacing=1.4)
    fig.text(0.5, 0.045, "loudness isn't in the sound.", ha="center",
             **display(33), color=ACCENT, weight="bold")

    fig.savefig(OUT / "video_meters.png", dpi=100, facecolor=BG)
    plt.close(fig)


def card_spotify(rows):
    top = next(r for r in rows if r["f"] == 12500)
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)

    fig.text(0.5, 0.955, "the 12,500 Hz tone", ha="center", va="top",
             **display(38), color=FG, weight="bold")
    fig.text(0.5, 0.902, "two meters. same file.", ha="center", va="top",
             **text(27), color=SAME)

    box_y = [0.700, 0.505]
    data = [
        ("YOUR EAR", "A-weighting", f"{top['a']:.1f}", "quiet.\nyou lose sensitivity up here", GOOD),
        ("SPOTIFY", "LUFS / BS.1770", f"{top['lufs']:.1f}", "one of the LOUDEST\nin the set", DIFF),
    ]
    for y0, (who, what, val, verdict, colour) in zip(box_y, data):
        fig.patches.append(plt.Rectangle((0.07, y0 - 0.005), 0.86, 0.155,
                                         transform=fig.transFigure,
                                         facecolor="#171326", edgecolor=colour, lw=2.5))
        fig.text(0.11, y0 + 0.122, who, **text(24), color=colour, weight="bold", va="top")
        fig.text(0.11, y0 + 0.086, what, **text(17), color=SAME, va="top")
        fig.text(0.11, y0 + 0.045, val, **display(40), color=FG, weight="bold", va="top")
        fig.text(0.50, y0 + 0.095, verdict, **text(20), color=FG, va="top",
                 linespacing=1.45)

    gap = abs(top["a"] - top["lufs"])
    fig.text(0.5, 0.435, f"{gap:.1f} dB apart", ha="center", va="top",
             **display(44), color=ACCENT, weight="bold")

    fig.text(0.5, 0.345,
             "neither one is broken.",
             ha="center", va="top", **display(31), color=FG, weight="bold")
    fig.text(0.5, 0.285,
             "spotify's meter isn't measuring\nwhat you hear. it corrects for how\n"
             "sound bends around your head.",
             ha="center", va="top", **text(24), color=SAME, linespacing=1.5)

    fig.text(0.5, 0.140, "they're answering\ndifferent questions.", ha="center",
             va="top", **display(33), color=FG, weight="bold", linespacing=1.4)
    fig.text(0.5, 0.032, "and only one of them is yours.", ha="center",
             **text(27), color=ACCENT)

    fig.savefig(OUT / "video_spotify.png", dpi=100, facecolor=BG)
    plt.close(fig)


def main():
    rows = measure()
    card_meters(rows)
    card_spotify(rows)
    print("wrote video_meters.png and video_spotify.png  (1080 x 1920 each)")
    for r in rows:
        print(f"  {r['f']:>6} Hz   peak {r['peak']:6.1f}   rms {r['rms']:6.1f}"
              f"   A {r['a']:6.1f}   LUFS {r['lufs']:6.1f}")


if __name__ == "__main__":
    main()
