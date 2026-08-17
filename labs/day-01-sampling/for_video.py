"""
Day 1: the version that goes in the video.

aliasing.py builds the sweep for the FIGURE: 10 seconds, full scale, up to 20 kHz.
That is correct for a spectrogram and genuinely painful in headphones.

This one is built for ears. 5 seconds, quieter, and it stops at 12 kHz so it does
not stab anyone. 12 kHz still folds twice at an 8 kHz sample rate (up to 4k, down
to 0, back up to 4k), so the turnaround is unmistakable and it is over fast.

Run:  python labs/day-01-sampling/for_video.py
"""

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import chirp

import librosa

OUT = Path(__file__).parent / "out"

FS = 48_000
TARGET_FS = 8_000
DECIM = FS // TARGET_FS
DURATION = 5.0
F_START = 200.0
F_END = 12_000.0   # low enough to not hurt, high enough to fold twice
AMP = 0.25         # about 6 dB below the figure version


def fade(x, fs, ms=30):
    n = int(fs * ms / 1000)
    ramp = np.linspace(0.0, 1.0, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def main():
    OUT.mkdir(exist_ok=True)

    t = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
    clean = fade(AMP * chirp(t, f0=F_START, f1=F_END, t1=DURATION, method="linear"), FS)

    aliased = clean[::DECIM]                    # no filter: folds
    correct = librosa.resample(clean, orig_sr=FS, target_sr=TARGET_FS,
                               res_type="soxr_vhq")

    sf.write(OUT / "video_1_normal.wav", clean, FS)
    sf.write(OUT / "video_2_broken.wav", aliased, TARGET_FS)
    sf.write(OUT / "video_3_correct.wav", correct, TARGET_FS)

    print("for the video, 5 seconds each:")
    print("  video_1_normal.wav   goes up. that's all it does.")
    print("  video_2_broken.wav   goes up, TURNS AROUND, comes back down, goes up again.")
    print("  video_3_correct.wav  goes up, stops early. the boring correct one.")
    print()
    print("you only need the first two on camera.")


if __name__ == "__main__":
    main()
