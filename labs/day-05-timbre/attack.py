"""
Day 5: what the attack carries, and a negative result about measuring it.

Saldanha and Corso (1964) cut the attack off recorded instrument notes and asked
people to name the instrument. Identification collapsed. Grey (1977) later found
attack time to be one of the main perceptual axes of timbre. The onset nobody
consciously listens to turns out to carry much of the identity.

I tried to reproduce that here and FAILED, three times, in an instructive way.
The sustain of these synthetic instruments separates them better than the attack
does, and the reason is a flaw in the stimulus rather than in the analysis. See
"the negative result" printed at the bottom.

What does work: reversing a note leaves the long-run spectrum untouched, so the
MFCCs barely move, while your ear stops recognising the instrument entirely.

Run:  python labs/day-05-timbre/attack.py   (run instruments.py first)
"""

import itertools
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

from instruments import INSTRUMENTS, SR, note

apply()
OUT = Path(__file__).parent / "out"

ATTACK_MS = 50


def mfcc_mean(y, sr=SR):
    """
    MFCCs averaged over time.

    n_fft has to shrink for short segments. librosa's 2048 default is 93 ms at
    this rate, which is longer than the 50 ms attack we want to analyse, so the
    default silently zero-pads and the "attack" MFCCs end up describing mostly
    silence.
    """
    n_fft = 1 << int(np.floor(np.log2(max(len(y) // 4, 64))))
    # n_mels must also come down with n_fft, or the upper mel filters end up
    # empty and those coefficients are noise
    n_mels = min(40, max(13, n_fft // 16))
    return librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=n_fft,
                                hop_length=n_fft // 4,
                                n_mels=n_mels)[1:].mean(axis=1)


def cos(a, b):
    return 1 - float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main():
    OUT.mkdir(exist_ok=True)
    n_att = int(SR * ATTACK_MS / 1000)

    notes = {inst: note(inst, 440.0) for inst in INSTRUMENTS}

    segments = {
        "whole note": {i: y for i, y in notes.items()},
        f"attack only ({ATTACK_MS} ms)": {i: y[:n_att] for i, y in notes.items()},
        "sustain only (attack cut)": {i: y[n_att:] for i, y in notes.items()},
    }

    print(f"how far apart are the three instruments, by MFCC distance?\n")
    print(f"{'segment':<30} {'mean distance':>14}  {'vs whole note':>14}")

    scores = {}
    for label, segs in segments.items():
        feats = {i: mfcc_mean(y) for i, y in segs.items()}
        d = np.mean([cos(feats[a], feats[b])
                     for a, b in itertools.combinations(INSTRUMENTS, 2)])
        scores[label] = d
        rel = d / scores["whole note"]
        print(f"{label:<30} {d:>14.4f}  {rel:>13.0%}")

    att = scores[f"attack only ({ATTACK_MS} ms)"]
    sus = scores["sustain only (attack cut)"]

    print()
    print("THE NEGATIVE RESULT")
    print("-" * 62)
    print(f"the attack separates these instruments {att / sus:.2f}x as well as the")
    print("sustain does. the literature says the attack should dominate, so either")
    print("the literature is wrong or my stimulus is. it is my stimulus.")
    print()
    print("a real flute, clarinet and guitar holding the same note produce fairly")
    print("SIMILAR steady spectra: all harmonic, comparable rolloff. that similarity")
    print("is exactly why cutting the attack wrecks human identification.")
    print()
    print("mine are not similar at all. one is nearly a sine wave, one suppresses")
    print("every even harmonic, one has nine strong partials. the sustains are")
    print("cartoonishly distinct, so of course the sustain separates them.")
    print()
    print("i built a dataset where the effect i was looking for could not appear,")
    print("and only noticed because the number came out backwards. tuning the")
    print("synthesis until it agreed with the textbook would have been the easy")
    print("move and would have proved nothing.")
    print("-" * 62)

    # ---- reversed notes: same spectrum, different envelope ----
    for inst in INSTRUMENTS:
        sf.write(OUT / f"{inst}_A4_reversed.wav", notes[inst][::-1], SR)

    fwd = mfcc_mean(notes["plucked"])
    rev = mfcc_mean(notes["plucked"][::-1])
    within = np.mean([cos(mfcc_mean(notes[a]), mfcc_mean(notes[b]))
                      for a, b in itertools.combinations(INSTRUMENTS, 2)])
    print()
    print("WHAT DOES WORK: reverse a note")
    print("-" * 62)
    d_rev = cos(fwd, rev)
    print(f"reversing the plucked note moves its MFCCs by {d_rev:.6f}.")
    print(f"the distance between two different INSTRUMENTS is {within:.4f}, so the")
    print(f"reversal registers as {d_rev / within:.2%} of an instrument change.")
    print()
    print("and that is not a coincidence, it is guaranteed by the maths. for a real")
    print("signal, |DFT| is exactly invariant under time reversal:")
    seg = notes["plucked"][5000:7048]
    inv = np.abs(np.abs(np.fft.rfft(seg)) - np.abs(np.fft.rfft(seg[::-1]))).max()
    print(f"    max |DFT| difference between a frame and its reverse: {inv:.1e}")
    print()
    print("so every analysis frame keeps its magnitude spectrum, only the ORDER of")
    print("the frames flips, and mean-pooling throws order away. mean-pooled MFCCs")
    print("are therefore blind to time reversal by construction. the residual above")
    print("is just window alignment at the edges.")
    print()
    print("play the reversed pluck. it is not a pluck any more, it is an organ")
    print("swell. your ear reclassifies it instantly and the feature cannot.")
    print()
    print("so there is a whole dimension of timbre these features barely encode,")
    print("and it is one your ear treats as decisive.")
    print("-" * 62)

    # ---- the picture ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    t = np.arange(len(notes["flute"])) / SR * 1000
    for ax, inst in zip(axes, INSTRUMENTS):
        y = notes[inst]
        ax.plot(t, y, lw=0.7, color=ACCENT)
        ax.axvspan(0, ATTACK_MS, color=GOOD, alpha=0.18)
        ax.set_title(inst, **display(19), color=FG)
        ax.set_xlim(0, 250)
        ax.set_xlabel("ms", **text(15), color=FG)
        ax.set_yticks([])
    axes[0].set_ylabel("the green sliver is the attack", **text(15), color=FG)
    fig.suptitle(f"the first {ATTACK_MS} ms carries the identity",
                 **display(21), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "attack.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'attack.png'} and three reversed notes")


if __name__ == "__main__":
    main()
