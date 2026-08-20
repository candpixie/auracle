"""
Day 5: phone-shaped cards, built from the real measurements.

  video_timbre.png    MFCC vs chroma: 36.7x one way, 0.03x the other
  video_reversal.png  the reversal blindness, with the mechanism
  video_wrong.png     the negative result

Run:  python labs/day-05-timbre/video_cards.py
"""

import itertools
import sys
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

from attack import cos, mfcc_mean
from instruments import INSTRUMENTS, MELODIES, SR, note
from mfcc_vs_chroma import distance, features

apply()
OUT = Path(__file__).parent / "out"


def measure():
    clips = {(i, m): features(OUT / f"{i}_{m}.wav")
             for i in INSTRUMENTS for m in MELODIES}
    keys = list(clips)
    pairs_inst = [(a, b) for a, b in itertools.combinations(keys, 2)
                  if a[1] == b[1] and a[0] != b[0]]
    pairs_mel = [(a, b) for a, b in itertools.combinations(keys, 2)
                 if a[0] == b[0] and a[1] != b[1]]

    out = {}
    for feat in ("mfcc", "chroma"):
        di = np.mean([distance(clips[a][feat], clips[b][feat]) for a, b in pairs_inst])
        dm = np.mean([distance(clips[a][feat], clips[b][feat]) for a, b in pairs_mel])
        out[feat] = (di, dm, di / dm)

    notes = {i: note(i, 440.0) for i in INSTRUMENTS}
    within = np.mean([cos(mfcc_mean(notes[a]), mfcc_mean(notes[b]))
                      for a, b in itertools.combinations(INSTRUMENTS, 2)])
    rev = cos(mfcc_mean(notes["plucked"]), mfcc_mean(notes["plucked"][::-1]))
    out["reversal"] = (rev, within, rev / within)
    return out


def card_timbre(m):
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.955, "the standard tool", ha="center", va="top",
             **display(40, "bold"), color=FG)
    fig.text(0.5, 0.905, "for analysing music", ha="center", va="top",
             **display(40, "bold"), color=FG)
    fig.text(0.5, 0.845, "was built to ignore music.", ha="center", va="top",
             **display(33), color=ACCENT)

    fig.text(0.5, 0.755, "same six notes. three instruments.", ha="center",
             va="top", **text(24), color=DIM)

    rows = [("MFCC", m["mfcc"], "hears the INSTRUMENT", GOOD),
            ("chroma", m["chroma"], "hears the NOTES", ACCENT)]
    for k, (name, (di, dm, ratio), verdict, colour) in enumerate(rows):
        y0 = 0.660 - k * 0.215
        fig.patches.append(plt.Rectangle((0.07, y0 - 0.135), 0.86, 0.175,
                                         transform=fig.transFigure,
                                         facecolor="#171326", edgecolor=colour, lw=2.5))
        fig.text(0.11, y0 + 0.012, name, **display(30, "bold"), color=colour, va="top")
        fig.text(0.11, y0 - 0.035, verdict, **text(20), color=FG, va="top")
        fig.text(0.11, y0 - 0.078, f"change the instrument   {di:.3f}",
                 **text(19), color=DIM, va="top")
        fig.text(0.11, y0 - 0.112, f"change the melody       {dm:.3f}",
                 **text(19), color=DIM, va="top")
        fig.text(0.90, y0 - 0.055, f"{ratio:.0f}x" if ratio >= 1 else f"{ratio:.2f}x",
                 **display(44, "bold"), color=colour, ha="right", va="center")

    fig.text(0.5, 0.205, "MFCCs come from speech recognition,",
             ha="center", va="top", **text(23), color=DIM)
    fig.text(0.5, 0.162, "where your pitch is the thing\nthey wanted to delete.",
             ha="center", va="top", **text(23), color=DIM, linespacing=1.45)
    fig.text(0.5, 0.062, "music borrowed them anyway.", ha="center",
             **display(31, "bold"), color=FG)
    fig.savefig(OUT / "video_timbre.png", dpi=100, facecolor=BG)
    plt.close(fig)


def card_reversal(m):
    rev, within, frac = m["reversal"]
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.955, "play a note backwards.", ha="center", va="top",
             **display(38, "bold"), color=FG)

    y = note("plucked", 440.0)
    t = np.arange(len(y)) / SR * 1000
    for k, (lab, sig, colour) in enumerate([("forwards", y, ACCENT),
                                            ("backwards", y[::-1], BAD)]):
        ax = fig.add_axes([0.10, 0.700 - k * 0.185, 0.80, 0.135])
        ax.plot(t, sig, lw=0.8, color=colour)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        fig.text(0.10, 0.848 - k * 0.185, lab, **text(22), color=colour, va="top")

    fig.text(0.5, 0.478, "your ear: a different instrument.", ha="center",
             va="top", **display(29), color=FG)
    fig.text(0.5, 0.425, "a pluck becomes an organ swell.", ha="center",
             va="top", **text(23), color=DIM)

    fig.text(0.5, 0.340, "the feature moved by", ha="center", va="top",
             **text(23), color=DIM)
    fig.text(0.5, 0.295, f"{frac:.3%}", ha="center", va="top",
             **display(58, "bold"), color=BAD)
    fig.text(0.5, 0.222, "of one instrument change.", ha="center", va="top",
             **text(23), color=DIM)

    fig.text(0.5, 0.150, "and it always will.", ha="center", va="top",
             **display(30, "bold"), color=FG)
    fig.text(0.5, 0.104,
             "reversing a sound leaves its spectrum\nidentical. averaging throws away order.",
             ha="center", va="top", **text(21), color=DIM, linespacing=1.5)
    fig.text(0.5, 0.022, "it is blind by construction.", ha="center",
             **display(29, "bold"), color=ACCENT)
    fig.savefig(OUT / "video_reversal.png", dpi=100, facecolor=BG)
    plt.close(fig)


def card_wrong():
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.950, "i tried to reproduce", ha="center", va="top",
             **display(36, "bold"), color=FG)
    fig.text(0.5, 0.898, "a 1964 experiment.", ha="center", va="top",
             **display(36, "bold"), color=FG)
    fig.text(0.5, 0.838, "i got the opposite answer.", ha="center", va="top",
             **display(31), color=BAD)

    fig.text(0.5, 0.745, "cut the attack off a note and people\ncan't name the instrument.",
             ha="center", va="top", **text(23), color=DIM, linespacing=1.5)

    rows = [("whole note", 0.324, ACCENT),
            ("attack only", 0.177, BAD),
            ("sustain only", 0.317, ACCENT)]
    for k, (lab, val, colour) in enumerate(rows):
        y0 = 0.630 - k * 0.070
        fig.text(0.14, y0, lab, **text(25), color=FG, va="center")
        fig.text(0.62, y0, f"{val:.3f}", **display(30, "bold"), color=colour,
                 ha="right", va="center")
        ax = fig.add_axes([0.66, y0 - 0.011, 0.22 * val / 0.324, 0.022])
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_facecolor(colour)
        for sp in ax.spines.values():
            sp.set_visible(False)

    fig.text(0.5, 0.375, "the attack should have won.", ha="center", va="top",
             **display(28), color=DIM)

    fig.text(0.5, 0.300, "the paper isn't wrong.", ha="center", va="top",
             **display(33, "bold"), color=FG)
    fig.text(0.5, 0.248, "my fake instruments were.", ha="center", va="top",
             **display(33, "bold"), color=ACCENT)

    fig.text(0.5, 0.185,
             "real instruments sound similar when\nthey hold a note. that's WHY the attack\nmatters. mine sounded nothing alike.",
             ha="center", va="top", **text(21), color=DIM, linespacing=1.5)

    fig.text(0.5, 0.078, "i built a test that couldn't\nfind what i was looking for.",
             ha="center", va="top", **display(28, "bold"), color=FG, linespacing=1.4)
    fig.savefig(OUT / "video_wrong.png", dpi=100, facecolor=BG)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    m = measure()
    card_timbre(m)
    card_reversal(m)
    card_wrong()
    print("wrote video_timbre.png, video_reversal.png, video_wrong.png")
    for k, (a, b, r) in m.items():
        print(f"  {k:<10} {a:.6f}  {b:.4f}  ratio {r:.4f}")


if __name__ == "__main__":
    main()
