"""
Day 4: the chromatic scale, drawn as it plays.

Three representations stacked, with a playhead sweeping left to right and the
spectrogram revealing behind it. You watch the staircase build note by note, so
the curve in the linear panel and the straight line in the CQT panel appear in
real time rather than being asserted.

Length defaults to the audio's own duration, so it can sit under
out/chromatic_scale.mp3 with no drift.

Run:  python labs/day-04-scales/video_scale_anim.py [seconds]
"""

import shutil
import subprocess
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

apply()
OUT = Path(__file__).parent / "out"
FRAMES = OUT / "_frames_scale"
FPS = 30
HOP = 256
DB_RANGE = 60


def panels(x):
    stft = librosa.amplitude_to_db(
        np.abs(librosa.stft(x, n_fft=2048, hop_length=HOP)), ref=np.max)
    mel = librosa.power_to_db(
        librosa.feature.melspectrogram(y=x, sr=SR, n_fft=2048, hop_length=HOP,
                                       n_mels=128), ref=np.max)
    cqt = librosa.amplitude_to_db(
        np.abs(librosa.cqt(x, sr=SR, hop_length=HOP, fmin=FMIN,
                           n_bins=N_SEMITONES + 11, bins_per_octave=12)), ref=np.max)
    return [
        ("what a computer sees", "hz", stft, BAD, (0, 4000)),
        ("the standard 'fix'", "mel", mel, BAD, None),
        ("one bin per note", "cqt_note", cqt, GOOD, None),
    ]


def render(idx, data, frac):
    with plt.rc_context({"figure.facecolor": BG, "axes.facecolor": BG}):
        fig = plt.figure(figsize=(10.8, 19.2))
        fig.suptitle("a scale going up.\nevery step the same size.",
                     **display(33, "bold"), color=FG, y=0.978, va="top",
                     linespacing=1.35)

        for k, (label, yaxis, full, colour, ylim) in enumerate(data):
            ax = fig.add_axes([0.15, 0.640 - k * 0.212, 0.78, 0.162])

            # reveal only up to the playhead
            n = max(2, int(frac * full.shape[1]))
            shown = np.full_like(full, full.min())
            shown[:, :n] = full[:, :n]

            librosa.display.specshow(shown, sr=SR, hop_length=HOP, y_axis=yaxis,
                                     fmin=FMIN, bins_per_octave=12, ax=ax,
                                     cmap="magma", vmin=-DB_RANGE, vmax=0)
            if ylim:
                ax.set_ylim(*ylim)
            ax.set_xticks([]); ax.set_yticks([]); ax.set_ylabel("")

            # the playhead. drawn twice so it reads against both the lit region
            # on its left and the black on its right.
            xpos = frac * full.shape[1] * HOP / SR
            ax.axvline(xpos, color=BG, lw=6, alpha=0.9)
            ax.axvline(xpos, color=GOOD, lw=2.6)

            fig.text(0.15, 0.822 - k * 0.212, label, **text(20), color=colour,
                     va="top")

        note_idx = min(N_SEMITONES - 1, int(frac * N_SEMITONES))
        semis = note_idx
        fig.text(0.5, 0.190, f"+{semis} semitones", ha="center", va="top",
                 **display(30, "bold"), color=FG)
        fig.text(0.5, 0.132, f"{FMIN * 2 ** (semis / 12):.0f} Hz", ha="center",
                 va="top", **text(24), color=DIM)

        fig.text(0.5, 0.072, "only the bottom one is straight.", ha="center",
                 va="top", **display(27), color=GOOD)
        fig.text(0.5, 0.020, "why a piano looks wrong.", ha="center",
                 **display(29, "bold"), color=ACCENT)

        fig.savefig(FRAMES / f"f{idx:04d}.png", dpi=100, facecolor=BG)
        plt.close(fig)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. brew install ffmpeg")
    OUT.mkdir(exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    x, _ = build_scale()
    audio_s = len(x) / SR
    total = float(sys.argv[1]) if len(sys.argv) > 1 else audio_s
    n_frames = int(total * FPS)

    data = panels(x)
    for i in range(n_frames):
        render(i, data, (i + 1) / n_frames)
        if i % 50 == 0:
            print(f"  frame {i}/{n_frames}")

    mp4 = OUT / "day04_scale.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920", str(mp4)],
                   check=True)
    shutil.rmtree(FRAMES)

    print(f"\nwrote {mp4}  ({n_frames / FPS:.1f} s, 1080x1920)")
    print(f"the audio itself is {audio_s:.2f} s "
          f"({'matched' if abs(total - audio_s) < 0.2 else 'NOT matched, playhead will drift'})")


if __name__ == "__main__":
    main()
