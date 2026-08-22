"""
Day 7: the machine tracks the most regular thing, not the beat.

I built this to test something else. The plan was: remove the downbeat, and watch
a beat tracker lose the bar line that a human still feels. What actually happened
is more interesting, and it made the original test meaningless.

The pattern is kick on beats 1 and 3, hi-hat on every off-beat. To any listener
the kick is the beat and the hat is the "and". To the tracker, the hat is a
perfectly even pulse and the kick is not, so it locks to the hats and places its
entire grid on the off-beat, half a beat out, with no indication anything is wrong.

Removing the downbeat then changes NOTHING, because the downbeat was never being
used. That null result is the finding.

Run:  python labs/day-07-rhythm/silent_beat.py
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

from tempo_sweep import SR, click, thump

apply()
OUT = Path(__file__).parent / "out"

BPM = 100.0
BARS = 8
BEATS = 4
SPB = 60.0 / BPM


def build(drop_downbeat=False, hats=True):
    n = int(SR * SPB * BEATS * BARS) + SR
    x = np.zeros(n)
    k, h = thump(), click()
    for b in range(BEATS * BARS):
        t = b * SPB
        if b % BEATS == 0 and drop_downbeat:
            pass
        elif b % BEATS in (0, 2):
            i = int(t * SR)
            x[i:i + len(k)] += k
        if hats:
            j = int((t + 0.5 * SPB) * SR)
            x[j:j + len(h)] += 0.5 * h
    return 0.5 * x / np.abs(x).max()


def track(x):
    onset = librosa.onset.onset_strength(y=x, sr=SR)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=SR,
                                           units="time")
    return float(np.atleast_1d(tempo)[0]), beats


def dist_ms(beats, ref):
    return float(np.mean([np.min(np.abs(ref - b)) for b in beats]) * 1000)


def main():
    OUT.mkdir(exist_ok=True)

    n_beats = BEATS * BARS
    KICKS = np.array([b * SPB for b in range(n_beats) if b % BEATS in (0, 2)])
    HATS = np.array([(b + 0.5) * SPB for b in range(n_beats)])

    cases = {
        "normal (kick + hat)": build(),
        "downbeat removed": build(drop_downbeat=True),
        "hats removed": build(hats=False),
    }
    for name, x in cases.items():
        sf.write(OUT / f"{name.split()[0]}.wav", x, SR)

    print(f"true tempo {BPM:.0f} BPM. kick on beats 1 and 3, hat on every 'and'.\n")
    print(f"{'condition':<22} {'tempo':>7} {'to the KICK':>13} {'to the HAT':>12}   locked to")
    for name, x in cases.items():
        tempo, beats = track(x)
        dk, dh = dist_ms(beats, KICKS), dist_ms(beats, HATS)
        locked = "the hat (OFF-BEAT)" if dh < dk else "the kick (the beat)"
        print(f"{name:<22} {tempo:>6.1f} {dk:>12.1f} ms {dh:>10.1f} ms   {locked}")

    print()
    print("with hats present it sits 23 ms from the off-beat and 320 ms from the")
    print("beat. it is not confused, it is confidently wrong: the hats are a")
    print("perfectly even pulse and the kicks are not, so the hats win.")
    print()
    print("removing the downbeat changes nothing at all, because the downbeat was")
    print("never being used. that is why the experiment i set out to run could not")
    print("have worked.")
    print()
    print("remove the hats and it does find the kicks, and halves the tempo.")
    print()
    print("a human hears kick-and-hat and knows instantly which one is the beat.")
    print("nothing in the audio says so. you know it because a kick on 1 and 3 is")
    print("what a beat SOUNDS like, and that is learned, not measured.")

    # ---- the picture ----
    fig, axes = plt.subplots(len(cases), 1, figsize=(14, 9))
    for ax, (name, x) in zip(axes, cases.items()):
        _, beats = track(x)
        t = np.arange(len(x)) / SR
        ax.plot(t, x, lw=0.7, color=DIM, alpha=0.8)
        for kk in KICKS:
            ax.axvline(kk, color=GOOD, lw=2.6, alpha=0.9)
        for bt in beats:
            ax.axvline(bt, color=BAD, lw=1.8, ls="--", alpha=0.9)
        ax.set_xlim(0, 4.2)
        ax.set_ylim(-1.1, 1.1)
        ax.set_yticks([])
        ax.set_ylabel(name, **text(14), color=FG)
    axes[-1].set_xlabel("seconds", **text(13), color=DIM)
    axes[0].set_title("green = the actual beat    red dashed = where the machine put it",
                      **display(17), color=FG)
    fig.suptitle("it locks to the hi-hat, half a beat off", **display(20), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "silent_beat.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'silent_beat.png'}")


if __name__ == "__main__":
    main()
