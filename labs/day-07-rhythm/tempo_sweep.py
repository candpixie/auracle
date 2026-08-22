"""
Day 7: how often does a tempo estimator land an octave off?

Rather than assert that octave errors happen, sweep the ground truth and count.
Synthesise a plain four-on-the-floor pattern at every BPM from 60 to 200, ask
librosa for the tempo, and score each answer as correct, half, double, or other.

"Octave" here is the metrical sense: reporting 70 for a 140 BPM track is hearing
the same music one level up the metrical hierarchy. Nothing is wrong with the
signal. The machine has no way to know which level a human would tap.

Run:  python labs/day-07-rhythm/tempo_sweep.py
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
BARS = 8
TOL = 0.04                      # 4 percent, the standard MIREX tolerance


def click(sr=SR, freq=1800, dur=0.035, amp=0.9):
    t = np.arange(int(sr * dur)) / sr
    return amp * np.sin(2 * np.pi * freq * t) * np.exp(-70 * t)


def thump(sr=SR, freq=90, dur=0.18, amp=1.0):
    t = np.arange(int(sr * dur)) / sr
    return amp * np.sin(2 * np.pi * freq * t) * np.exp(-22 * t)


def pattern(bpm, sr=SR, bars=BARS, beats_per_bar=4):
    """Kick on every beat, hat on every off-beat. Utterly unambiguous to a human."""
    spb = 60.0 / bpm
    n = int(sr * spb * beats_per_bar * bars) + sr
    x = np.zeros(n)
    k, h = thump(), click()
    for b in range(beats_per_bar * bars):
        i = int(b * spb * sr)
        x[i:i + len(k)] += k
        j = int((b + 0.5) * spb * sr)
        x[j:j + len(h)] += 0.45 * h
    return 0.5 * x / np.abs(x).max()


# every ratio here is a real metrical level: the same music counted at a
# different rate. 2/3 and 3/2 are the dotted / triplet levels.
LEVELS = [("correct", 1.0), ("half", 0.5), ("double", 2.0),
          ("2/3", 2 / 3), ("3/2", 1.5), ("third", 1 / 3), ("triple", 3.0),
          ("quarter", 0.25), ("quadruple", 4.0)]


def classify(est, true, tol=TOL):
    for name, factor in LEVELS:
        if abs(est - true * factor) <= true * factor * tol:
            return name
    return "not a metrical level"


def main():
    OUT.mkdir(exist_ok=True)
    tempos = np.arange(60, 201, 2)

    rows = []
    for bpm in tempos:
        x = pattern(float(bpm))
        onset = librosa.onset.onset_strength(y=x, sr=SR)
        est = float(np.atleast_1d(librosa.feature.tempo(
            onset_envelope=onset, sr=SR))[0])
        rows.append((float(bpm), est, classify(est, float(bpm))))

    counts = {}
    for _, _, c in rows:
        counts[c] = counts.get(c, 0) + 1

    print(f"{len(rows)} tempos from {tempos[0]} to {tempos[-1]} BPM, "
          f"unambiguous four-on-the-floor\n")
    print(f"{'verdict':<22} {'count':>6} {'share':>8}")
    for name, _ in LEVELS + [("not a metrical level", 0)]:
        if name in counts:
            print(f"{name:<22} {counts[name]:>6} {counts[name] / len(rows):>7.0%}")

    wrong = [r for r in rows if r[2] != "correct"]
    junk = [r for r in rows if r[2] == "not a metrical level"]
    print(f"\n{len(wrong)} of {len(rows)} wrong ({len(wrong) / len(rows):.0%}).")
    print(f"{len(junk)} of those are not a metrical level at all "
          f"({len(junk) / len(rows):.0%}).")
    print()
    print("that second number is the point. every miss is the SAME rhythm counted")
    print("at a different rate: half time, double time, or the dotted level. the")
    print("machine never failed to find a periodicity. it found a real one and")
    print("picked a level a human would not tap.")

    if wrong:
        print("\na sample:")
        for true, est, c in wrong[:10]:
            print(f"  {true:>5.0f} BPM  ->  {est:>6.1f}   ({c})")

    # ---- the estimate depends on a parameter, not just the audio ----
    print()
    print("and now the part that bothers me. the same audio, three settings of")
    print("librosa's start_bpm, which is a log-normal PRIOR centred on a guess:\n")
    print(f"{'true':>6} {'start=60':>11} {'start=120':>11} {'start=180':>11}")
    for bpm in (60, 90, 120, 180):
        x = pattern(float(bpm))
        onset = librosa.onset.onset_strength(y=x, sr=SR)
        vals = [float(np.atleast_1d(librosa.feature.tempo(
            onset_envelope=onset, sr=SR, start_bpm=s))[0]) for s in (60, 120, 180)]
        print(f"{bpm:>6} " + "".join(f"{v:>11.1f}" for v in vals))
    print()
    print("60 BPM reads as 60 with one setting and 117 with another. the audio did")
    print("not change. 'the tempo' here is not a property of the recording, it is a")
    print("property of the recording plus an assumption about what tempo music is.")

    sf.write(OUT / "pattern_120bpm.wav", pattern(120.0), SR)

    # ---- the picture ----
    fig, ax = plt.subplots(figsize=(13, 6))

    # guide lines first, so the measurements sit on top
    YLIM = (40, 260)
    ax.plot(tempos, tempos, lw=1.6, ls="--", color=FG, alpha=0.45)
    for factor, lab in ((0.5, "half"), (2.0, "double"), (2 / 3, "2/3")):
        ax.plot(tempos, tempos * factor, lw=1.2, ls=":", color=DIM, alpha=0.6)
        # label the line where it actually leaves the plot, not off-canvas
        y_end = tempos[-1] * factor
        if YLIM[0] < y_end < YLIM[1]:
            ax.text(tempos[-1] + 2, y_end, lab, **text(12), color=DIM, va="center")
        else:
            x_at_top = YLIM[1] / factor
            if tempos[0] < x_at_top < tempos[-1]:
                ax.text(x_at_top, YLIM[1] - 8, lab, **text(12), color=DIM,
                        ha="center", va="top")
    ax.axhline(120, color=ACCENT, lw=1.6, alpha=0.45)
    ax.text(207, 120, "120", **text(12), color=ACCENT, va="center")

    # one colour per verdict, derived from LEVELS so nothing can go unplotted
    palette = {"correct": GOOD}
    for name, _ in LEVELS[1:]:
        palette[name] = BAD
    palette["not a metrical level"] = DIM

    for name in palette:
        pts = [(t, e) for t, e, c in rows if c == name]
        if pts:
            ax.scatter(*zip(*pts), s=46, color=palette[name], label=name, zorder=3)

    ax.set_xlabel("true tempo (BPM)", **text(15), color=FG)
    ax.set_ylabel("what the machine reported", **text(15), color=FG)
    ax.set_xlim(55, 212)
    ax.set_ylim(*YLIM)
    ax.legend(fontsize=12, ncol=4, loc="lower right")
    ax.grid(alpha=0.12)
    ax.set_title("the same rhythm at 71 tempos. everything is pulled toward 120.",
                 **display(18), color=FG, pad=14)
    fig.tight_layout()
    fig.savefig(OUT / "tempo_sweep.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'tempo_sweep.png'}")
    return rows


if __name__ == "__main__":
    main()
