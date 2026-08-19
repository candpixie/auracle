"""
Day 4: the same chromatic scale, drawn three ways.

Play every semitone from C3 to C6 and look at it three ways:

  linear STFT   the notes curve away exponentially. equal musical steps are not
                equal distances, because frequency is not pitch.
  mel           compressed, and fit to SPEECH perception, not music.
  CQT           log-spaced bins, so one semitone is one bin everywhere. the
                staircase is straight.

That difference is the whole day. An octave is a doubling, so a musically even
scale is exponential in Hz, and a linear frequency axis will never show it as even.

Run:  python labs/day-04-scales/chromatic.py
"""

from pathlib import Path

import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT = Path(__file__).parent / "out"

SR = 22_050
NOTE_S = 0.28
N_SEMITONES = 37            # C3 to C6 inclusive
FMIN = librosa.note_to_hz("C3")
HARMONICS = 8
DB_RANGE = 60


def pluck(f0, sr=SR, dur=NOTE_S):
    """A note with harmonics, so it looks like an instrument rather than a sine."""
    t = np.arange(int(sr * dur)) / sr
    x = np.zeros_like(t)
    for h in range(1, HARMONICS + 1):
        if f0 * h >= sr / 2:
            break
        x += np.sin(2 * np.pi * f0 * h * t) / h
    x *= np.exp(-3.5 * t)                       # decay
    return 0.5 * x / np.abs(x).max()


def build_scale():
    freqs = FMIN * 2 ** (np.arange(N_SEMITONES) / 12)
    return np.concatenate([pluck(f) for f in freqs]), freqs


def main():
    OUT.mkdir(exist_ok=True)
    x, freqs = build_scale()
    sf.write(OUT / "chromatic_scale.wav", x, SR)

    hop = 256
    stft_db = librosa.amplitude_to_db(
        np.abs(librosa.stft(x, n_fft=2048, hop_length=hop)), ref=np.max)
    mel_db = librosa.power_to_db(
        librosa.feature.melspectrogram(y=x, sr=SR, n_fft=2048, hop_length=hop,
                                       n_mels=128), ref=np.max)
    cqt_db = librosa.amplitude_to_db(
        np.abs(librosa.cqt(x, sr=SR, hop_length=hop, fmin=FMIN,
                           n_bins=N_SEMITONES + 11, bins_per_octave=12)),
        ref=np.max)

    panels = [
        (stft_db, "linear", "hz", "frequency (Hz), linear"),
        (mel_db, "mel", "mel", "mel bins"),
        (cqt_db, "cqt", "cqt_note", "one bin per semitone"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, (data, title, yaxis, ylab) in zip(axes, panels):
        librosa.display.specshow(data, sr=SR, hop_length=hop, x_axis="time",
                                 y_axis=yaxis, fmin=FMIN, bins_per_octave=12,
                                 ax=ax, cmap="magma", vmin=-DB_RANGE, vmax=0)
        ax.set_title(title, fontsize=12)
        ax.set_ylabel(ylab, fontsize=10)
        if title == "linear":
            ax.set_ylim(0, 4000)

    fig.suptitle("one chromatic scale, every step the same musical size", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "chromatic.png", dpi=150)

    # ---- measure the staircase instead of eyeballing it ----
    print("is each semitone the same DISTANCE up the axis?\n")
    print(f"{'representation':<16} {'first step':>11} {'last step':>10} {'ratio':>8}")

    def step_sizes(freq_axis):
        """where consecutive notes land on this axis, in bins"""
        pos = np.interp(freqs, freq_axis, np.arange(len(freq_axis)))
        return np.diff(pos)

    lin_axis = librosa.fft_frequencies(sr=SR, n_fft=2048)
    mel_axis = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=SR / 2)
    cqt_axis = librosa.cqt_frequencies(n_bins=N_SEMITONES + 11, fmin=FMIN,
                                       bins_per_octave=12)

    for name, axis in (("linear STFT", lin_axis), ("mel", mel_axis), ("CQT", cqt_axis)):
        s = step_sizes(axis)
        print(f"{name:<16} {s[0]:>11.2f} {s[-1]:>10.2f} {s[-1] / s[0]:>7.1f}x")

    print()
    print("CQT is 1.00x: every semitone is exactly one bin, top to bottom.")
    print("linear grows 7.55x, so the same musical step covers seven times as much")
    print("axis up high as down low.")
    print()
    print("and mel is 7.23x. it is 96% as bad as doing nothing.")
    print()
    print("the reason is not that mel is a bad idea. it is that there are TWO mel")
    print("scales and librosa defaults to the one that is LITERALLY LINEAR below")
    print("1 kHz. run scales.py for the numbers. C3 to C6 sits almost entirely")
    print("inside that linear region, so over the range where melodies live, the")
    print("perceptual axis is not being perceptual at all.")
    print()
    print(f"wrote {OUT / 'chromatic.png'} and chromatic_scale.wav")


if __name__ == "__main__":
    main()
