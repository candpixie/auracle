"""
Day 4: phone-shaped cards, numbers measured live rather than typed in.

  video_staircase.png   the three representations stacked, CQT last
  video_ratio.png       the 7.55 / 7.23 / 3.66 / 1.00 measurement
  video_two_mels.png    "mel spectrogram" names two different scales

Run:  python labs/day-04-scales/video_cards.py
"""

import sys
from pathlib import Path

import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

from chromatic import FMIN, N_SEMITONES, SR, build_scale
from scales import hz_to_mel_htk, hz_to_mel_slaney

apply()
OUT = Path(__file__).parent / "out"

HOP = 256
DB_RANGE = 60


def semitone_ratio(axis, freqs):
    """How much does one semitone's distance along this axis grow, low to high?"""
    pos = np.interp(freqs, axis, np.arange(len(axis)))
    steps = np.diff(pos)
    return steps[-1] / steps[0]


def measure():
    freqs = FMIN * 2 ** (np.arange(N_SEMITONES) / 12)
    lin = librosa.fft_frequencies(sr=SR, n_fft=2048)
    slaney = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=SR / 2, htk=False)
    htk = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=SR / 2, htk=True)
    return {
        "linear": semitone_ratio(lin, freqs),
        "slaney": semitone_ratio(slaney, freqs),
        "htk": semitone_ratio(htk, freqs),
        "cqt": 1.0,
        "linear_bins": int((np.diff(slaney) < np.diff(slaney).min() + 1.0).sum()),
    }


def card_staircase(x):
    panels = [
        ("what a computer sees", "hz", librosa.amplitude_to_db(
            np.abs(librosa.stft(x, n_fft=2048, hop_length=HOP)), ref=np.max), BAD),
        ("the standard 'fix'", "mel", librosa.power_to_db(
            librosa.feature.melspectrogram(y=x, sr=SR, n_fft=2048,
                                           hop_length=HOP, n_mels=128), ref=np.max), BAD),
        ("what it should look like", "cqt_note", librosa.amplitude_to_db(
            np.abs(librosa.cqt(x, sr=SR, hop_length=HOP, fmin=FMIN,
                               n_bins=N_SEMITONES + 11, bins_per_octave=12)),
            ref=np.max), GOOD),
    ]

    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.968, "a scale going up.", ha="center", va="top",
             **display(38, "bold"), color=FG)
    fig.text(0.5, 0.920, "every step the same size.", ha="center", va="top",
             **display(28), color=DIM)

    for k, (label, yaxis, data, colour) in enumerate(panels):
        ax = fig.add_axes([0.13, 0.665 - k * 0.198, 0.80, 0.150])
        librosa.display.specshow(data, sr=SR, hop_length=HOP, y_axis=yaxis,
                                 fmin=FMIN, bins_per_octave=12, ax=ax,
                                 cmap="magma", vmin=-DB_RANGE, vmax=0)
        if yaxis == "hz":
            ax.set_ylim(0, 4000)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylabel("")
        fig.text(0.13, 0.842 - k * 0.198, label, **text(21), color=colour, va="top")

    fig.text(0.5, 0.228, "only the last one is straight.", ha="center", va="top",
             **display(31, "bold"), color=FG)
    fig.text(0.5, 0.176,
             "going up one note MULTIPLIES the\nfrequency. it doesn't add to it.",
             ha="center", va="top", **text(22), color=DIM, linespacing=1.4)
    fig.text(0.5, 0.092,
             "steps that are even to your ear\naren't even to a computer.",
             ha="center", va="top", **display(26), color=FG, linespacing=1.4)
    fig.text(0.5, 0.018, "why a piano looks wrong.", ha="center",
             **display(30, "bold"), color=ACCENT)
    fig.savefig(OUT / "video_staircase.png", dpi=100, facecolor=BG)
    plt.close(fig)


def card_ratio(m):
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.955, "does one note cover", ha="center", va="top",
             **display(36, "bold"), color=FG)
    fig.text(0.5, 0.903, "the same distance", ha="center", va="top",
             **display(36, "bold"), color=FG)
    fig.text(0.5, 0.851, "everywhere?", ha="center", va="top",
             **display(36, "bold"), color=ACCENT)

    fig.text(0.5, 0.775, "1.00x would mean yes.", ha="center", va="top",
             **text(24), color=DIM)

    rows = [("no perceptual scale", m["linear"], BAD),
            ("mel  (the default)", m["slaney"], BAD),
            ("mel  (the other one)", m["htk"], BAD),
            ("CQT", m["cqt"], GOOD)]
    for k, (label, val, colour) in enumerate(rows):
        y0 = 0.660 - k * 0.088
        fig.text(0.11, y0, label, **text(25), color=FG, va="center")
        fig.text(0.89, y0, f"{val:.2f}x", **display(38, "bold"), color=colour,
                 ha="right", va="center")
        fig.add_artist(plt.Line2D([0.11, 0.89], [y0 - 0.036, y0 - 0.036],
                                  color="#2a2440", lw=1.5))

    fig.text(0.5, 0.268, "the fix is 96% as uneven", ha="center", va="top",
             **display(31, "bold"), color=FG)
    fig.text(0.5, 0.216, "as doing nothing at all.", ha="center", va="top",
             **display(31, "bold"), color=FG)

    fig.text(0.5, 0.130,
             "over C3 to C6, which is where\nnearly every melody lives.",
             ha="center", va="top", **text(23), color=DIM, linespacing=1.5)
    fig.text(0.5, 0.030, "so why does it barely work?", ha="center",
             **display(29), color=ACCENT)
    fig.savefig(OUT / "video_ratio.png", dpi=100, facecolor=BG)
    plt.close(fig)


def card_two_mels(m):
    fig = plt.figure(figsize=(10.8, 19.2), facecolor=BG)
    fig.text(0.5, 0.958, "there are two", ha="center", va="top",
             **display(38, "bold"), color=FG)
    fig.text(0.5, 0.906, "different mel scales.", ha="center", va="top",
             **display(38, "bold"), color=ACCENT)
    fig.text(0.5, 0.848, "papers just say “mel”.", ha="center", va="top",
             **display(27), color=DIM)

    ax = fig.add_axes([0.15, 0.470, 0.78, 0.300])
    f = np.linspace(1, SR / 2, 2000)
    ax.plot(f, hz_to_mel_htk(f) / hz_to_mel_htk(SR / 2), lw=4, color=GOOD,
            label="HTK: curved everywhere")
    ax.plot(f, hz_to_mel_slaney(f) / hz_to_mel_slaney(SR / 2), lw=4, color=BAD,
            label="Slaney: STRAIGHT below 1 kHz")
    ax.axvspan(130, 1050, color=ACCENT, alpha=0.15)
    ax.set_xlim(0, 4000)
    ax.set_ylim(0, 0.72)
    ax.set_xticks([0, 1000, 2000, 3000, 4000])
    ax.set_xticklabels(["0", "1k", "2k", "3k", "4k"], **text(18))
    ax.set_yticks([])
    ax.legend(loc="lower right", fontsize=17)
    ax.grid(alpha=0.12)
    fig.text(0.54, 0.792, "the violet band is where melodies live",
             ha="center", **text(19), color=ACCENT)

    fig.text(0.5, 0.418, "the one every library defaults to", ha="center",
             va="top", **text(23), color=DIM)
    fig.text(0.5, 0.368, "is literally linear", ha="center", va="top",
             **display(34, "bold"), color=FG)
    fig.text(0.5, 0.316, "below 1000 Hz.", ha="center", va="top",
             **display(34, "bold"), color=FG)

    fig.text(0.5, 0.235,
             f"{m['linear_bins']} of its 128 bins sit inside\nthat linear region.",
             ha="center", va="top", **text(22), color=DIM, linespacing=1.5)

    fig.text(0.5, 0.140, "the two disagree by", ha="center", va="top",
             **text(23), color=DIM)
    fig.text(0.5, 0.092, f"{m['slaney'] / m['htk']:.1f}x", ha="center", va="top",
             **display(52, "bold"), color=BAD)
    fig.text(0.5, 0.026, "on the same sound.", ha="center",
             **display(29, "bold"), color=FG)
    fig.savefig(OUT / "video_two_mels.png", dpi=100, facecolor=BG)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    m = measure()
    x, _ = build_scale()
    card_staircase(x)
    card_ratio(m)
    card_two_mels(m)
    print("wrote video_staircase.png, video_ratio.png, video_two_mels.png")
    for k, v in m.items():
        print(f"  {k:<12} {v}")


if __name__ == "__main__":
    main()
