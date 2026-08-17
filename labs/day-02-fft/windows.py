"""
Day 2: why you never hand the FFT a raw chunk.

The DFT assumes the chunk you gave it repeats forever. If the waveform does not
happen to end exactly where it started, the assumed loop has a discontinuity in
it, and a discontinuity is broadband, so the transform reports energy at hundreds
of frequencies that are not in the signal. That is spectral leakage.

Fix: multiply the chunk by a window that tapers to zero at both ends, so the loop
is seamless. It costs a little frequency resolution and removes an artifact that
is orders of magnitude worse.

Two sines here, at the SAME amplitude:
  - 100 Hz exactly, which fits a whole number of cycles in the chunk. No
    discontinuity, so even the raw version looks clean.
  - 100.5 Hz, which does not fit. Same signal, half a hertz different, and the
    raw transform smears it across the whole spectrum.

Run:  python labs/day-02-fft/windows.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / "out"

N = 1024
FS = 1024          # so bin width is exactly 1 Hz and "fits the chunk" means integer Hz
CASES = [100.0, 100.5]


def spectrum_db(x):
    mag = np.abs(np.fft.rfft(x))
    mag /= mag.max()
    return 20 * np.log10(mag + 1e-12)


def main():
    OUT.mkdir(exist_ok=True)
    t = np.arange(N) / FS
    hann = np.hanning(N)

    fig, axes = plt.subplots(2, 2, figsize=(13, 7))

    for row, freq in enumerate(CASES):
        x = np.sin(2 * np.pi * freq * t)
        fits = abs(freq - round(freq)) < 1e-9

        # left: the signal ACROSS THE WRAP. the DFT assumes the chunk loops, so what
        # matters is whether the end joins back onto the start smoothly. splice the
        # tail directly onto the head and look at the join.
        ax = axes[row, 0]
        wrap = np.concatenate([x[-40:], x[:40]])
        ax.plot(np.arange(-40, 0), wrap[:40], lw=1.4, color="#ff5c8a", label="end of chunk")
        ax.plot(np.arange(0, 40), wrap[40:], lw=1.4, color="#7c5cff", label="start, spliced on")
        ax.axvline(0, color="k", ls="--", lw=1.0, alpha=0.6)
        ax.set_title(f"{freq} Hz  ·  {'fits: the loop is seamless' if fits else 'does NOT fit: look at the kink'}",
                     fontsize=10)
        ax.legend(fontsize=8, loc="lower left")
        ax.set_xlabel("sample (0 = the wrap point)")
        ax.set_ylim(-1.35, 1.35)

        # right: what the transform reports, raw vs windowed
        ax = axes[row, 1]
        ax.plot(spectrum_db(x), lw=1.0, color="#ff5c8a", label="raw (no window)")
        ax.plot(spectrum_db(x * hann), lw=1.0, color="#7c5cff", label="Hann window")
        ax.set_xlim(60, 145)
        ax.set_ylim(-120, 5)
        ax.axvline(freq, color="k", ls=":", lw=0.8, alpha=0.5)
        ax.set_title("what the FFT reports", fontsize=10)
        ax.set_xlabel("frequency (Hz)")
        ax.set_ylabel("dB (relative)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.15)

    fig.suptitle("spectral leakage: the same sine, half a hertz apart", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "windows.png", dpi=150)

    # put a number on it: how much energy lands away from the true peak
    print(f"{'freq':>8}  {'window':>12}  {'leakage 20+ Hz away':>22}")
    for freq in CASES:
        x = np.sin(2 * np.pi * freq * t)
        for label, sig in (("none", x), ("Hann", x * hann)):
            db = spectrum_db(sig)
            far = np.concatenate([db[:int(freq) - 20], db[int(freq) + 20:]])
            print(f"{freq:>8}  {label:>12}  {far.max():>19.1f} dB")

    print()
    print("100.0 Hz is fine either way, because it happens to fit.")
    print("100.5 Hz is the same sine, and raw it smears across the whole spectrum.")
    print("real music never 'happens to fit', so this is not an edge case, it is")
    print("the normal case. window everything.")
    print()
    print(f"wrote {OUT / 'windows.png'}")


if __name__ == "__main__":
    main()
