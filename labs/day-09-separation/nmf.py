"""
Day 9: NMF finds the parts, and cannot tell you which part is the singer.

Lee and Seung (1999) factor a non-negative magnitude spectrogram V into W @ H:
W is a dictionary of K spectral templates, H is when each one is active. On
music this genuinely works. The templates come out looking like notes and like
drum hits, with no supervision and no labels.

No labels is the problem. A separation needs two stems, so somebody has to say
which of the K components belong to the singer. NMF does not say. This lab
scores two ways of deciding:

  oracle      use the true stems to assign each component. Cheating, and an
              upper bound on what the factorisation itself can support.
  flatness    assign by how noise-like the template is. A real rule, usable
              on real music, no ground truth required.

Run:  python labs/day-09-separation/nmf.py
"""

import sys
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import NMF

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from auracle.style import ACCENT, BAD, DIM, GOOD, WARM, apply, display, text
import synth

apply()
OUT = Path(__file__).parent / "out"

N_FFT = 2048
HOP = 512
KS = [2, 4, 8, 16, 32]
EPS = 1e-10


def components(mix, k, seed=0):
    """Factor the mixture, then turn each component back into a waveform."""
    D = librosa.stft(mix, n_fft=N_FFT, hop_length=HOP)
    V = np.abs(D)
    model = NMF(n_components=k, init="nndsvda", solver="mu", beta_loss="kullback-leibler",
                max_iter=400, random_state=seed)
    W = model.fit_transform(V)
    H = model.components_
    total = W @ H + EPS
    waves, flatness = [], []
    for i in range(k):
        mask = np.outer(W[:, i], H[i]) / total
        waves.append(librosa.istft(mask * D, hop_length=HOP, length=mix.size))
        col = W[:, i] + EPS
        # spectral flatness: geometric mean over arithmetic mean. 1 is white
        # noise, near 0 is a handful of sharp partials.
        flatness.append(np.exp(np.mean(np.log(col))) / np.mean(col))
    return np.array(waves), np.array(flatness)


def group(waves, picks):
    chosen = waves[picks] if np.any(picks) else np.zeros((1, waves.shape[1]))
    return chosen.sum(axis=0)


def main():
    OUT.mkdir(exist_ok=True)
    h, p, m = synth.mix(synth.harmonic(0.5), synth.percussive(0.02))

    print("NMF on the mixture, then two ways to decide which components")
    print("are the singer. Scored against the stems that went in.\n")
    print(f"{'K':>3} | {'oracle h':>8} {'oracle p':>8} | {'flatness h':>10} {'flatness p':>10}"
          f" | {'drums':>7}")
    print("-" * 68)

    rows = []
    for k in KS:
        waves, flat = components(m, k)
        # oracle: whichever true stem this component resembles more
        is_perc_oracle = np.array([synth.si_sdr(w, p) > synth.si_sdr(w, h) for w in waves])
        # flatness: noise-like templates are the drums. split at the median so
        # the rule cannot win by putting everything in one bin.
        is_perc_flat = flat > np.median(flat)

        oh = synth.si_sdr(group(waves, ~is_perc_oracle), h)
        op = synth.si_sdr(group(waves, is_perc_oracle), p)
        fh = synth.si_sdr(group(waves, ~is_perc_flat), h)
        fp = synth.si_sdr(group(waves, is_perc_flat), p)
        rows.append((k, oh, op, fh, fp, flat, is_perc_oracle))
        print(f"{k:>3} | {oh:8.1f} {op:8.1f} | {fh:10.1f} {fp:10.1f}"
              f" | {is_perc_oracle.sum():2d}/{k:<2d} vs {is_perc_flat.sum():2d}")

    print("\nThe last column is how many of the K components really are drums,")
    print("against how many the flatness rule puts there. The rule splits at the")
    print("median, so it always says half, and the truth is only half at small K.")

    best_oracle = max(rows, key=lambda r: r[1] + r[2])
    best_flat = max(rows, key=lambda r: r[3] + r[4])
    print(f"\nBest K if you already know the answer : {best_oracle[0]}")
    print(f"Best K if you do not                  : {best_flat[0]}")
    print("Neither K is discoverable from the mixture, and they disagree."
          if best_oracle[0] != best_flat[0] else
          "They agree on K here, which is luck, not a method.")

    figure(rows)
    print(f"\nwrote {OUT / 'nmf.png'}")


def figure(rows):
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6))

    ks = [r[0] for r in rows]
    ax = axes[0]
    ax.plot(ks, [r[1] for r in rows], "o-", color=ACCENT, lw=2.2, label="oracle, harmonic")
    ax.plot(ks, [r[2] for r in rows], "o--", color=ACCENT, lw=2.2, label="oracle, percussive")
    ax.plot(ks, [r[3] for r in rows], "s-", color=BAD, lw=2.2, label="flatness, harmonic")
    ax.plot(ks, [r[4] for r in rows], "s--", color=BAD, lw=2.2, label="flatness, percussive")
    ax.set_xscale("log", base=2)
    ax.set_xticks(ks)
    ax.set_xticklabels(ks)
    ax.set_xlabel("number of components K")
    ax.set_ylabel("SI-SDR (dB)")
    ax.set_title("The gap is the labelling, not the factorisation", **display(19))
    ax.legend(fontsize=13)
    ax.grid(True)

    k, *_, flat, is_perc = rows[KS.index(8)]
    ax = axes[1]
    order = np.argsort(flat)
    colours = [WARM if is_perc[i] else ACCENT for i in order]
    ax.bar(range(len(flat)), flat[order], color=colours)
    ax.axhline(np.median(flat), color=DIM, ls="--", lw=1.6)
    ax.set_xlabel(f"the {k} components, sorted by how noise-like they are")
    ax.set_ylabel("spectral flatness")
    ax.set_title("Violet is really the singer, orange really the drums", **display(19))
    ax.text(0.03, 0.93, "dashed line: where the flatness rule splits them",
            transform=ax.transAxes, color=DIM, **text(14))
    ax.grid(True, axis="y")

    fig.suptitle("NMF finds the parts and will not name them", **display(26))
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUT / "nmf.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
