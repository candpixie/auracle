"""
Day 9: harmonic-percussive separation, and the two assumptions it is built on.

Fitzgerald (2010) in one sentence: in a spectrogram, held notes are horizontal
lines and drum hits are vertical lines, so median-filter along time to keep the
horizontal and along frequency to keep the vertical, and you have separated
them. No training data, no model, about ten lines of code, and it works.

It works because of two assumptions that are never stated as assumptions:

  1. the harmonic source holds still in pitch
  2. the percussive source stops immediately

This sweeps both and scores against the sources that actually went in.

Run:  python labs/day-09-separation/hpss.py
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from auracle.style import ACCENT, BAD, DIM, GOOD, WARM, apply, display, text
import synth

apply()
OUT = Path(__file__).parent / "out"

N_FFT = 2048
HOP = 512
VIBRATOS = [0.0, 0.25, 0.5, 1.0, 2.0]       # semitones of bend, peak to centre
DECAYS = [0.005, 0.02, 0.08, 0.30]          # seconds, click to cymbal wash


def separate(m, margin=1.0, kernel_size=31):
    D = librosa.stft(m, n_fft=N_FFT, hop_length=HOP)
    H, P = librosa.decompose.hpss(D, kernel_size=kernel_size, margin=margin)
    h = librosa.istft(H, hop_length=HOP, length=m.size)
    p = librosa.istft(P, hop_length=HOP, length=m.size)
    return h, p


def score(vib, decay, margin=1.0):
    h, p, m = synth.mix(synth.harmonic(vib), synth.percussive(decay))
    h_est, p_est = separate(m, margin=margin)
    return (synth.si_sdr(h_est, h), synth.si_sdr(p_est, p), m, h, p, h_est, p_est)


def main():
    OUT.mkdir(exist_ok=True)

    print("How well HPSS does on a mixture it was designed for")
    print("(vibrato 0, hits that stop dead), scored against the true stems:\n")
    hs, ps, m0, h0, p0, he0, pe0 = score(0.0, 0.02)
    print(f"  harmonic stem    {hs:6.1f} dB SI-SDR")
    print(f"  percussive stem  {ps:6.1f} dB SI-SDR")
    for name, sig in (("mixture", m0), ("true_harmonic", h0), ("true_percussive", p0),
                      ("hpss_harmonic", he0), ("hpss_percussive", pe0)):
        sf.write(OUT / f"{name}.wav", sig, synth.SR)

    print("\n--- knob 1: the singer moves ---")
    print("vibrato (semitones) | harmonic dB | percussive dB")
    vib_rows = []
    for v in VIBRATOS:
        a, b, *_ = score(v, 0.02)
        vib_rows.append((v, a, b))
        print(f"{v:19.2f} | {a:11.1f} | {b:13.1f}")

    print("\n--- knob 2: the hit rings on ---")
    print("decay (ms) | harmonic dB | percussive dB")
    dec_rows = []
    for d in DECAYS:
        a, b, *_ = score(0.0, d)
        dec_rows.append((d, a, b))
        print(f"{d * 1000:10.0f} | {a:11.1f} | {b:13.1f}")

    # the escape hatch: margin > 1 sends anything ambiguous to a residual
    print("\n--- the third bin ---")
    print("On the 2-semitone-vibrato mixture, raising the margin lets HPSS")
    print("refuse to classify. Energy it refuses lands in neither stem.")
    print("margin | harmonic dB | percussive dB | energy kept")
    marg_rows = []
    hv, pv, mv = synth.mix(synth.harmonic(2.0), synth.percussive(0.02))
    for g in (1.0, 2.0, 4.0, 8.0):
        he, pe = separate(mv, margin=g)
        kept = (np.sum(he ** 2) + np.sum(pe ** 2)) / np.sum(mv ** 2)
        a, b = synth.si_sdr(he, hv), synth.si_sdr(pe, pv)
        marg_rows.append((g, a, b, kept))
        print(f"{g:6.1f} | {a:11.1f} | {b:13.1f} | {kept * 100:10.1f}%")

    figure(vib_rows, dec_rows, mv)
    print(f"\nwrote {OUT / 'hpss.png'}")


def figure(vib_rows, dec_rows, mix_vibrato):
    fig = plt.figure(figsize=(13, 9))

    ax = fig.add_subplot(2, 2, 1)
    v = [r[0] for r in vib_rows]
    ax.plot(v, [r[1] for r in vib_rows], "o-", color=ACCENT, lw=2.2, label="harmonic stem")
    ax.plot(v, [r[2] for r in vib_rows], "o-", color=WARM, lw=2.2, label="percussive stem")
    ax.set_xlabel("vibrato depth (semitones)")
    ax.set_ylabel("SI-SDR (dB)")
    ax.set_title("Separation vs how much the singer moves", **display(19))
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(2, 2, 2)
    d = [r[0] * 1000 for r in dec_rows]
    ax.plot(d, [r[1] for r in dec_rows], "o-", color=ACCENT, lw=2.2, label="harmonic stem")
    ax.plot(d, [r[2] for r in dec_rows], "o-", color=WARM, lw=2.2, label="percussive stem")
    ax.set_xscale("log")
    ax.set_xlabel("percussive decay (ms)")
    ax.set_ylabel("SI-SDR (dB)")
    ax.set_title("Separation vs how long the hit rings", **display(19))
    ax.legend()
    ax.grid(True)

    D = librosa.amplitude_to_db(np.abs(librosa.stft(mix_vibrato, n_fft=N_FFT,
                                                    hop_length=HOP)), ref=np.max)
    he, pe = separate(mix_vibrato)
    for i, (sig, title) in enumerate([(he, "what HPSS calls harmonic"),
                                      (pe, "what HPSS calls percussive")]):
        ax = fig.add_subplot(2, 2, 3 + i)
        S = librosa.amplitude_to_db(np.abs(librosa.stft(sig, n_fft=N_FFT,
                                                        hop_length=HOP)), ref=np.max)
        librosa.display.specshow(S, sr=synth.SR, hop_length=HOP, x_axis="time",
                                 y_axis="linear", ax=ax, cmap="magma", vmin=-60, vmax=0)
        ax.set_ylim(0, 2600)
        ax.set_title(f"{title}, 2-semitone vibrato", **display(17))
        if i:
            ax.set_ylabel("")

    fig.suptitle("HPSS assumes the music holds still", **display(26))
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT / "hpss.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
