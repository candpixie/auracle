"""
Day 5: MFCCs throw pitch away on purpose. Measure it.

The claim everyone repeats is "MFCCs capture timbre." The sharper version, and
the one that matters for music, is that they were DESIGNED to discard pitch,
because they come from speech recognition where the speaker's pitch is a nuisance
variable.

The test: six clips, three instruments crossed with two melodies. Then ask two
questions of each feature.

  1. how far apart are two clips that share a melody but differ in instrument?
  2. how far apart are two clips that share an instrument but differ in melody?

A pure timbre feature should answer big for (1) and near-zero for (2). A pure
pitch feature should do the reverse. The ratio between the two is the number.

Run:  python labs/day-05-timbre/mfcc_vs_chroma.py   (run instruments.py first)
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

from instruments import INSTRUMENTS, MELODIES, SR

apply()
OUT = Path(__file__).parent / "out"

N_MFCC = 13


def features(path):
    y, sr = librosa.load(path, sr=SR)

    # MFCCs. Drop coefficient 0: it is overall energy, not spectral shape, and
    # leaving it in makes loudness look like timbre.
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)[1:]

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    return {
        "mfcc": mfcc.mean(axis=1),
        "chroma": chroma.mean(axis=1),
        "centroid": np.array([librosa.feature.spectral_centroid(y=y, sr=sr).mean()]),
        "rolloff": np.array([librosa.feature.spectral_rolloff(y=y, sr=sr).mean()]),
        "zcr": np.array([librosa.feature.zero_crossing_rate(y).mean()]),
    }


def distance(a, b):
    """
    Cosine distance for vectors, relative difference for scalars.

    Cosine on a 1-D feature is always exactly 0, because any two positive scalars
    point the same direction. The first version of this script reported 0.0000
    for spectral centroid on every pair and dutifully labelled it "pitch", which
    is nonsense: it was measuring nothing at all.
    """
    if a.size == 1:
        return float(abs(a[0] - b[0]) / (abs(a[0]) + abs(b[0]) + 1e-12))
    return 1 - float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main():
    OUT.mkdir(exist_ok=True)
    clips = {}
    for inst in INSTRUMENTS:
        for mel in MELODIES:
            path = OUT / f"{inst}_{mel}.wav"
            if not path.exists():
                sys.exit("run instruments.py first")
            clips[(inst, mel)] = features(path)

    keys = list(clips)
    same_melody = [(a, b) for a, b in itertools.combinations(keys, 2)
                   if a[1] == b[1] and a[0] != b[0]]      # instrument differs
    same_inst = [(a, b) for a, b in itertools.combinations(keys, 2)
                 if a[0] == b[0] and a[1] != b[1]]        # melody differs

    print("distance between clips, averaged over every pair\n")
    print(f"{'feature':<12} {'inst differs':>13} {'melody differs':>15} {'ratio':>8}   reads as")

    results = {}
    for feat in ("mfcc", "chroma", "centroid", "rolloff", "zcr"):
        d_inst = np.mean([distance(clips[a][feat], clips[b][feat]) for a, b in same_melody])
        d_mel = np.mean([distance(clips[a][feat], clips[b][feat]) for a, b in same_inst])
        ratio = d_inst / (d_mel + 1e-12)
        reads = ("timbre only" if ratio > 3 else
                 "pitch only" if ratio < 0.33 else "both")
        results[feat] = (d_inst, d_mel, ratio)
        print(f"{feat:<12} {d_inst:>13.4f} {d_mel:>15.4f} {ratio:>8.1f}x   {reads}")

    print()
    print("MFCCs move a lot when the instrument changes and barely move when the")
    print("melody changes. chroma does the opposite. neither is a bug: they are")
    print("two answers to two different questions, and only one of them is 'what")
    print("note is this'.")

    # ---- the picture ----
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))
    for col, inst in enumerate(INSTRUMENTS):
        y, sr = librosa.load(OUT / f"{inst}_tune_A.wav", sr=SR)
        m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)[1:]
        c = librosa.feature.chroma_cqt(y=y, sr=sr)

        axes[0, col].imshow(m, aspect="auto", origin="lower", cmap="magma")
        axes[0, col].set_title(inst, **display(19), color=FG)
        axes[0, col].set_xticks([]); axes[0, col].set_yticks([])

        axes[1, col].imshow(c, aspect="auto", origin="lower", cmap="magma")
        axes[1, col].set_xticks([]); axes[1, col].set_yticks([])

    axes[0, 0].set_ylabel("MFCC", **text(17), color=FG)
    axes[1, 0].set_ylabel("chroma", **text(17), color=FG)
    fig.suptitle("same six notes, three instruments\n"
                 "top row changes across columns. bottom row does not.",
                 **display(20), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "mfcc_vs_chroma.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'mfcc_vs_chroma.png'}")
    return results


if __name__ == "__main__":
    main()
