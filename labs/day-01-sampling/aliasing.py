"""
Day 1: aliasing.

Generate a sine sweep that climbs from 20 Hz to 20 kHz, then destroy it two
different ways to hear what Nyquist actually means.

  sweep_48k.wav          the original. climbs and stops.
  sweep_aliased_8k.wav   decimated with NO anti-alias filter. climbs, hits the
                         ceiling, and comes back DOWN. that descent is the alias.
  sweep_resampled_8k.wav decimated correctly, with the filter. climbs and stops,
                         just earlier. this is what your resampler does for you.

Run:  python labs/day-01-sampling/aliasing.py
"""

from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import chirp

DB_RANGE = 80  # every spectrogram gets the same 80 dB window, so the panels are
               # honestly comparable and filter leakage can't masquerade as signal

OUT = Path(__file__).parent / "out"

FS = 48_000          # source sample rate
TARGET_FS = 8_000    # what we drop to. 48000 / 8000 = 6, a clean integer.
DECIM = FS // TARGET_FS
DURATION = 10.0      # seconds
F_START = 20.0
F_END = 20_000.0


def fade(x, fs, ms=20):
    """Short fade in/out so the file doesn't start and end with a click."""
    n = int(fs * ms / 1000)
    ramp = np.linspace(0.0, 1.0, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def make_sweep():
    t = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
    x = 0.5 * chirp(t, f0=F_START, f1=F_END, t1=DURATION, method="linear")
    return fade(x, FS)


def alias_it(x):
    """
    Keep every 6th sample and throw the rest away.

    This is the naive thing, and it is wrong. Anything above the new Nyquist
    (8000 / 2 = 4000 Hz) does not disappear. It FOLDS back down and reappears
    as a lower frequency, indistinguishable from a real one. The information
    is not degraded, it is gone and replaced with a lie.
    """
    return x[::DECIM]


def resample_it(x):
    """
    The correct version: low-pass filter first, THEN decimate.

    Filter quality is the whole story here. scipy's resample_poly defaults to a
    Kaiser window with roughly 40 dB of stopband attenuation, which sounds like a
    lot until you feed it a full-scale sweep: 40 dB down is still plainly visible
    on a spectrogram, and the "correct" panel ends up folding almost as badly as
    the broken one. soxr_vhq gets past 100 dB, which is what a real resampler
    actually does.
    """
    return librosa.resample(x, orig_sr=FS, target_sr=TARGET_FS, res_type="soxr_vhq")


def predicted_alias(f):
    """
    Where a frequency f actually lands after sampling at TARGET_FS.

    It folds into [0, TARGET_FS/2] like light bouncing between two mirrors.
    Our sweep goes to 20 kHz, so at 8 kHz it bounces off the 4 kHz ceiling
    and the 0 Hz floor twice on the way up. You can hear every bounce.
    """
    f = np.mod(f, TARGET_FS)
    return np.where(f > TARGET_FS / 2, TARGET_FS - f, f)


def spectrogram(ax, x, fs, title):
    *_, im = ax.specgram(x, NFFT=1024, Fs=fs, noverlap=768, cmap="magma")
    top = im.get_clim()[1]
    im.set_clim(top - DB_RANGE, top)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("frequency (Hz)")


def main():
    OUT.mkdir(exist_ok=True)

    original = make_sweep()
    aliased = alias_it(original)
    correct = resample_it(original)

    sf.write(OUT / "sweep_48k.wav", original, FS)
    sf.write(OUT / "sweep_aliased_8k.wav", aliased, TARGET_FS)
    sf.write(OUT / "sweep_resampled_8k.wav", correct, TARGET_FS)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    spectrogram(axes[0], original, FS, f"original @ {FS} Hz\nclimbs to 20 kHz and stops")
    spectrogram(axes[1], aliased, TARGET_FS, f"decimated, NO filter @ {TARGET_FS} Hz\nfolds back down. this is aliasing.")
    spectrogram(axes[2], correct, TARGET_FS, f"resampled correctly @ {TARGET_FS} Hz\nfiltered first, so nothing folds")

    # overlay the predicted fold pattern on the broken one
    t = np.linspace(0, DURATION, 500)
    f_inst = F_START + (F_END - F_START) * t / DURATION
    axes[1].plot(t, predicted_alias(f_inst), "c--", lw=1.2, alpha=0.8,
                 label="predicted fold")
    axes[1].legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "aliasing.png", dpi=150)

    print(f"wrote 3 wav files and aliasing.png to {OUT}")
    print()
    print("now go LISTEN, in this order:")
    print("  1. sweep_48k.wav           it goes up, then stops.")
    print("  2. sweep_resampled_8k.wav  it goes up, then stops earlier. correct.")
    print("  3. sweep_aliased_8k.wav    it goes up, comes back DOWN, goes up again.")
    print()
    print("nothing in that third file is real above 4 kHz. the descent is a")
    print("frequency that was never played, and no amount of processing gets")
    print("the original back.")


if __name__ == "__main__":
    main()
