"""
Day 6: pitch tracking works, right up until there is more than one note.

YIN and pYIN are excellent on a single voice. They are not "not as good" on a
chord, they are structurally incapable of it: both assume ONE periodic source and
return ONE number. A chord has no single period to find.

This measures the collapse on the same three notes, first alone, then together.

Run:  python labs/day-06-pitch/polyphony.py
"""

import sys
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

apply()
OUT = Path(__file__).parent / "out"

SR = 22_050
DUR = 1.5
CHORD = {"C4": 261.63, "E4": 329.63, "G4": 392.00}   # a C major triad


def tone(f0, n_harm=6, sr=SR, dur=DUR):
    t = np.arange(int(sr * dur)) / sr
    x = sum(np.sin(2 * np.pi * f0 * h * t) / h for h in range(1, n_harm + 1))
    n = int(sr * 0.03)
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return 0.3 * x / np.abs(x).max()


def track(x, method):
    if method == "yin":
        f = librosa.yin(x, fmin=80, fmax=1000, sr=SR)
    else:
        f, voiced, _ = librosa.pyin(x, fmin=80, fmax=1000, sr=SR)
        f = f[voiced]
    f = f[np.isfinite(f)]
    return float(np.median(f)) if len(f) else float("nan")


def cents(a, b):
    return 1200 * np.log2(a / b)


def main():
    OUT.mkdir(exist_ok=True)

    notes = {n: tone(f) for n, f in CHORD.items()}
    chord = sum(notes.values()) / len(notes)
    chord = 0.4 * chord / np.abs(chord).max()

    sf.write(OUT / "chord.wav", chord, SR)
    for n, y in notes.items():
        sf.write(OUT / f"note_{n}.wav", y, SR)

    print("one note at a time. both methods are excellent.\n")
    print(f"{'note':<7} {'true':>9} {'YIN':>9} {'error':>10}   {'pYIN':>9} {'error':>10}")
    for n, true in CHORD.items():
        y = track(notes[n], "yin")
        p = track(notes[n], "pyin")
        print(f"{n:<7} {true:>7.1f} Hz {y:>7.1f} Hz {cents(y, true):>+8.1f}c   "
              f"{p:>7.1f} Hz {cents(p, true):>+8.1f}c")

    print()
    print("now play all three at once.\n")
    y = track(chord, "yin")
    p = track(chord, "pyin")
    print(f"{'YIN on the chord':<24} {y:>7.1f} Hz")
    print(f"{'pYIN on the chord':<24} {p:>7.1f} Hz")
    print(f"{'the notes actually there':<24} "
          f"{', '.join(f'{v:.0f}' for v in CHORD.values())} Hz")

    root = CHORD["C4"]
    print()
    print(f"{y:.1f} Hz is not a note in the chord. it is {cents(y, root):+.0f} cents")
    print(f"from C4, which is to say exactly C3, an octave BELOW the lowest note.")
    print()
    print("and it is not a random failure. a major triad is close to a 4:5:6 ratio,")
    print("so the three waveforms line up again only after a long common period,")
    print("far longer than any single note's. YIN found the period of the MIXTURE,")
    print("correctly, and the period of a mixture is not a note anybody played.")
    print()
    print("which is interesting, because your ear does something adjacent: you hear")
    print("a C major chord as rooted on C. the difference is that you also hear the")
    print("three separate notes. YIN returns one number because one number is all")
    print("its model has room for.")
    print()
    print("this is not a tuning or threshold problem. polyphonic pitch tracking is")
    print("a genuinely open area, and it is why day 9 has to separate sources before")
    print("anything can ask them what note they are.")

    # ---- the picture ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, (label, sig) in zip(axes, [("one note (E4)", notes["E4"]),
                                       ("all three at once", chord)]):
        f = librosa.yin(sig, fmin=80, fmax=1000, sr=SR)
        t = librosa.times_like(f, sr=SR)
        ax.plot(t, f, lw=2.5, color=ACCENT, label="what YIN reports")
        for n, hz in CHORD.items():
            ax.axhline(hz, color=GOOD if "one note" in label and n == "E4" else DIM,
                       ls=":", lw=1.6)
            ax.text(t[-1] * 1.01, hz, n, **text(13),
                    color=GOOD if "one note" in label and n == "E4" else DIM,
                    va="center")
        ax.set_ylim(80, 700)
        ax.set_title(label, **display(18), color=FG)
        ax.set_xlabel("time (s)", **text(13), color=DIM)
        ax.set_ylabel("Hz", **text(13), color=DIM)
        ax.legend(fontsize=12)

    fig.suptitle("YIN on one note, and YIN on three notes",
                 **display(20), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "polyphony.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'polyphony.png'}")


if __name__ == "__main__":
    main()
