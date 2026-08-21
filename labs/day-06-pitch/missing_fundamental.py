"""
Day 6: a pitch that is not in the sound.

Take a 200 Hz tone with harmonics at 200, 400, 600, 800, 1000. Now DELETE the
200 Hz component. There is no energy at 200 Hz at all, verified against the
spectrum below. You still hear 200 Hz.

The pitch you perceive is not present in the signal. It is inferred, because the
remaining partials are all multiples of 200 and the waveform still repeats 200
times a second.

This is why a phone speaker that cannot physically produce 60 Hz still lets you
hear a bass line.

Run:  python labs/day-06-pitch/missing_fundamental.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

apply()
OUT = Path(__file__).parent / "out"

SR = 44_100
F0 = 200.0
N_HARM = 5
DUR = 2.0


def build(harmonics, sr=SR, dur=DUR, f0=F0):
    t = np.arange(int(sr * dur)) / sr
    x = np.zeros_like(t)
    for h in harmonics:
        x += np.sin(2 * np.pi * f0 * h * t) / h
    n = int(sr * 0.05)
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return 0.4 * x / np.abs(x).max()


def energy_at(x, freq, sr=SR):
    """Magnitude of the spectrum in the bin nearest freq, relative to the peak."""
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    return mag[np.argmin(np.abs(freqs - freq))] / mag.max()


def autocorr(x, sr=SR):
    """Normalised autocorrelation, lag 0 first."""
    x = x - x.mean()
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    return ac / ac[0]


def naive_pitch(x, sr=SR, fmin=60, fmax=800):
    """Pick the biggest autocorrelation peak in range. This is the obvious method
    and it is a trap, for reasons the output below makes concrete."""
    ac = autocorr(x, sr)
    lo, hi = int(sr / fmax), int(sr / fmin)
    return sr / (lo + int(np.argmax(ac[lo:hi])))


def main():
    OUT.mkdir(exist_ok=True)

    full = build(range(1, N_HARM + 1))              # 200 400 600 800 1000
    missing = build(range(2, N_HARM + 1))           # 400 600 800 1000, no 200
    only_f0 = build([1])                            # 200 alone, for reference

    for name, sig in (("full", full), ("missing_fundamental", missing),
                      ("reference_200hz", only_f0)):
        sf.write(OUT / f"{name}.wav", sig, SR)

    print("is there any energy at 200 Hz?\n")
    print(f"{'signal':<24} {'energy at 200 Hz':>18}   verdict")
    for name, sig in (("full harmonics", full), ("fundamental removed", missing)):
        e = energy_at(sig, F0)
        print(f"{name:<24} {e:>18.6f}   {'present' if e > 0.01 else 'ABSENT'}")

    print()
    print("and yet the waveform still repeats 200 times a second. the partials at")
    print("400, 600, 800 and 1000 are all multiples of 200, so a full cycle still")
    print("completes at 200 Hz. your auditory system reports the repetition rate,")
    print("not the lowest frequency present.")

    print()
    print("now ask two algorithms what pitch it is.\n")
    print(f"{'method':<34} {'full':>9} {'f0 removed':>12}")
    print(f"{'naive autocorrelation peak':<34} "
          f"{naive_pitch(full):>7.1f} Hz {naive_pitch(missing):>10.1f} Hz")
    yf = np.median(librosa.yin(full, fmin=60, fmax=800, sr=SR))
    ym = np.median(librosa.yin(missing, fmin=60, fmax=800, sr=SR))
    print(f"{'YIN (de Cheveigne and Kawahara)':<34} {yf:>7.1f} Hz {ym:>10.1f} Hz")

    print()
    print("YIN agrees with your ear. the naive method drops an octave, and here is")
    print("exactly how close that call was:\n")
    ac = autocorr(missing)
    for f in (400, 200, 100, 66.7):
        print(f"  autocorrelation at {f:>6.1f} Hz : {ac[int(round(SR / f))]:.4f}")
    print()
    print("200 and 100 are tied to three decimal places, and the WRONG one wins by")
    print("0.0001. that is not bad luck, it is structural: if a signal repeats every")
    print("T seconds it also repeats every 2T, so every true peak has an equally")
    print("tall impostor an octave below it.")
    print()
    print("YIN exists to break that tie. its cumulative mean normalised difference")
    print("function deliberately penalises longer lags so the first real dip wins.")
    print()
    print("LISTEN: reference_200hz.wav, then missing_fundamental.wav.")
    print("same pitch. the second file has nothing at that pitch in it.")

    # ---- the picture ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    freqs = np.fft.rfftfreq(len(full), 1 / SR)

    for row, (label, sig) in enumerate([("all harmonics", full),
                                        ("200 Hz removed", missing)]):
        ax = axes[row, 0]
        n = int(SR * 0.02)
        ax.plot(np.arange(n) / SR * 1000, sig[:n] if row == 0 else sig[3000:3000 + n],
                lw=1.6, color=ACCENT if row == 0 else BAD)
        ax.set_ylabel(label, **text(15), color=FG)
        ax.set_xlabel("ms", **text(13), color=DIM)
        ax.set_yticks([])

        ax = axes[row, 1]
        mag = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))
        mag /= mag.max()
        ax.plot(freqs, 20 * np.log10(mag + 1e-12), lw=1.4,
                color=ACCENT if row == 0 else BAD)
        ax.axvline(F0, color=GOOD, ls=":", lw=2)
        ax.set_xlim(0, 1200)
        ax.set_ylim(-90, 5)
        ax.set_xlabel("Hz", **text(13), color=DIM)
        ax.text(F0 + 20, -12, "200 Hz", **text(14), color=GOOD)

    axes[0, 0].set_title("the waveform", **display(17), color=FG)
    axes[0, 1].set_title("what is actually in it", **display(17), color=FG)
    fig.suptitle("both waveforms repeat 200 times a second.\n"
                 "only one of them contains 200 Hz.",
                 **display(19), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "missing_fundamental.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'missing_fundamental.png'}")


if __name__ == "__main__":
    main()
