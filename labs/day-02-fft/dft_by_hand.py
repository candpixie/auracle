"""
Day 2: the DFT, written out once by hand.

The Fourier transform gets treated as a black box you import. It is four lines.
Write it once, check it against numpy, and never be superstitious about it again.

For each candidate frequency k, multiply the signal by a complex sinusoid at that
frequency and sum. If the signal contains that frequency, the products line up and
the sum is large. If it doesn't, they cancel and the sum is near zero. That is the
entire idea: correlation against every frequency in turn.

Run:  python labs/day-02-fft/dft_by_hand.py
"""

import time

import numpy as np


def dft(x):
    """
    Naive DFT. O(n^2), because it literally builds the n x n matrix of every
    frequency against every sample.

        X[k] = sum_n  x[n] * exp(-2j*pi*k*n/N)
    """
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    basis = np.exp(-2j * np.pi * k * n / N)   # the n x n matrix of sinusoids
    return basis @ x


def dft_loop(x):
    """Same thing with the loop spelled out, in case the matrix version hides it."""
    N = len(x)
    out = np.zeros(N, dtype=complex)
    for k in range(N):
        total = 0.0 + 0.0j
        for n in range(N):
            total += x[n] * np.exp(-2j * np.pi * k * n / N)
        out[k] = total
    return out


def main():
    rng = np.random.default_rng(0)

    # a signal with three known frequencies in it, plus noise
    fs = 1024
    t = np.arange(fs) / fs
    x = (1.0 * np.sin(2 * np.pi * 50 * t)
         + 0.5 * np.sin(2 * np.pi * 120 * t)
         + 0.2 * np.sin(2 * np.pi * 300 * t)
         + 0.05 * rng.standard_normal(fs))

    mine = dft(x)
    theirs = np.fft.fft(x)

    err = np.abs(mine - theirs).max()
    print(f"max absolute difference from numpy: {err:.3e}")
    print("(anything near 1e-9 or below is just float rounding, so they agree)")
    print()

    # confirm the small version matches too, so the matrix trick isn't lying
    small = x[:64]
    assert np.allclose(dft(small), dft_loop(small)), "matrix and loop disagree"
    print("matrix version and explicit-loop version agree")
    print()

    # and now the reason nobody uses the naive one
    for name, fn in (("mine (naive, O(n^2))", dft), ("numpy (FFT, O(n log n))", np.fft.fft)):
        start = time.perf_counter()
        fn(x)
        print(f"{name:26s} {(time.perf_counter() - start) * 1000:8.2f} ms")

    print()
    print("the FFT is not a different transform. it is the same answer, computed by")
    print("noticing that the naive version recomputes the same products over and over.")
    print()

    # read the peaks back out, to prove the output means what we think
    mags = np.abs(theirs[:fs // 2])
    peaks = np.argsort(mags)[-3:][::-1]
    print(f"three strongest bins: {sorted(peaks)} Hz  (put in: 50, 120, 300)")


if __name__ == "__main__":
    main()
