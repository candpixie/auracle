"""
Day 9: the ground-truth mixture, and the two ways to score a separation.

Real music gives you a mixture and no stems, so you cannot tell leakage from
reconstruction error. Everything in this lab is built from sources I synthesise,
so every number is measured against the signal that actually went in.

Two knobs, because they are the two things the day-9 model assumes away:

  vibrato   how far the harmonic source bends in pitch. A spectrogram row is
            only horizontal if the singer holds dead still.
  decay     how long each percussive hit rings. A spectrogram column is only
            vertical if the hit stops immediately.

Both scoring functions here allow the estimate to be wrong in ways the ear
forgives, and they disagree about which ways those are. That disagreement is
the point of `metrics.py`.
"""

import numpy as np
from scipy.linalg import toeplitz

SR = 22_050
DUR = 4.0
F0 = 220.0
N_HARM = 10
VIB_RATE = 5.5          # Hz, the middle of the trained-voice range
HITS_PER_SEC = 4.0


def harmonic(vib_semitones=0.0, sr=SR, dur=DUR, f0=F0, n_harm=N_HARM):
    """A sung-like tone. Phase is integrated so vibrato bends f0 continuously."""
    t = np.arange(int(sr * dur)) / sr
    bend = 2.0 ** (vib_semitones * np.sin(2 * np.pi * VIB_RATE * t) / 12.0)
    phase = 2 * np.pi * f0 * np.cumsum(bend) / sr
    x = np.zeros_like(t)
    for h in range(1, n_harm + 1):
        if f0 * h * 2 ** (vib_semitones / 12) >= sr / 2:
            break
        x += np.sin(h * phase) / h
    n = int(sr * 0.05)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return x


def percussive(decay_s=0.02, sr=SR, dur=DUR, hits_per_sec=HITS_PER_SEC, seed=0):
    """Band-passed noise bursts with an exponential tail of length decay_s."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(sr * dur))
    noise = rng.standard_normal(x.size)
    # one-pole high pass, so the hits sit above the tone's lower harmonics
    hp = np.zeros_like(noise)
    a = 0.85
    for_prev = 0.0
    prev_in = 0.0
    for i, v in enumerate(noise):
        for_prev = a * for_prev + (v - prev_in)
        prev_in = v
        hp[i] = for_prev
    step = int(sr / hits_per_sec)
    tail = int(sr * decay_s * 6)
    for start in range(int(sr * 0.1), x.size - 1, step):
        n = min(tail, x.size - start)
        env = np.exp(-np.arange(n) / (sr * decay_s))
        x[start:start + n] += hp[start:start + n] * env
    return x


def mix(h, p, ratio_db=0.0):
    """Sum at a chosen harmonic-to-percussive RMS ratio, then normalise."""
    h = h / np.sqrt(np.mean(h ** 2))
    p = p / np.sqrt(np.mean(p ** 2))
    p *= 10 ** (-ratio_db / 20)
    m = h + p
    peak = np.abs(m).max()
    return h / peak, p / peak, m / peak


# --- scoring -----------------------------------------------------------------
# Both of these are "SDR": signal to distortion ratio in dB, higher is better.
# They differ only in what counts as an allowed distortion rather than an error.

def si_sdr(est, ref):
    """
    Scale-invariant SDR. The estimate may be any constant multiple of the
    reference and still score perfectly. Nothing else is forgiven.
    """
    est, ref = _trim(est, ref)
    alpha = np.dot(est, ref) / np.dot(ref, ref)
    target = alpha * ref
    err = est - target
    return 10 * np.log10(np.sum(target ** 2) / (np.sum(err ** 2) + 1e-20) + 1e-20)


def filtered_sdr(est, ref, taps=512):
    """
    bss_eval's SDR: the estimate may be the reference through any FIR filter of
    `taps` length, and that still counts as clean. Delays, small EQ moves and
    phase rotations are all absorbed, because they are all filters.
    """
    est, ref = _trim(est, ref)
    pad = np.concatenate([np.zeros(taps - 1), ref])
    first_col = pad[taps - 1:]
    first_row = pad[taps - 1::-1][:taps]
    basis = toeplitz(first_col, first_row)          # ref shifted 0..taps-1
    coef, *_ = np.linalg.lstsq(basis, est, rcond=None)
    target = basis @ coef
    err = est - target
    return 10 * np.log10(np.sum(target ** 2) / (np.sum(err ** 2) + 1e-20) + 1e-20)


def _trim(a, b):
    n = min(a.size, b.size)
    return a[:n], b[:n]
