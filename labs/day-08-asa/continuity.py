"""
Day 8: your brain fills in sound that was deleted.

The continuity illusion. Take a steady tone, cut a hole in it, and drop a burst of
loud broadband noise into the hole. You do not hear a tone, a gap, then a tone.
You hear one continuous tone with noise on top of it.

The condition is that the noise must be loud enough that it WOULD have masked the
tone had the tone been there. Given that, your auditory system concludes the tone
probably continued and was merely covered, so it reconstructs it. Bregman calls
this the "old-plus-new" heuristic.

Three files here:

  tone_continuous.wav   an unbroken tone. the thing you think you hear.
  tone_gap.wav          tone, silence, tone. you clearly hear the hole.
  tone_noise.wav        tone, NOISE, tone. the hole is still there and you
                        will not hear it.

The machine measures energy at the tone frequency and finds the hole every time,
because the hole is really there.

Run:  python labs/day-08-asa/continuity.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

apply()
OUT = Path(__file__).parent / "out"

SR = 44_100
F0 = 1000.0
DUR = 2.4
GAP_START, GAP_END = 1.0, 1.30      # 300 ms hole


def ramp(x, sr=SR, ms=8):
    n = int(sr * ms / 1000)
    r = np.linspace(0, 1, n)
    x[:n] *= r
    x[-n:] *= r[::-1]
    return x


def build(fill):
    """fill: 'none' (continuous), 'silence', or 'noise'."""
    t = np.arange(int(SR * DUR)) / SR
    tone = 0.30 * np.sin(2 * np.pi * F0 * t)
    hole = (t >= GAP_START) & (t < GAP_END)

    x = tone.copy()
    if fill != "none":
        x[hole] = 0.0
        # taper the tone into and out of the hole so there is no click
        n = int(SR * 0.006)
        idx = np.where(hole)[0]
        x[idx[0] - n:idx[0]] *= np.linspace(1, 0, n)
        x[idx[-1]:idx[-1] + n] *= np.linspace(0, 1, n)

    if fill == "noise":
        rng = np.random.default_rng(0)
        burst = np.zeros_like(t)
        # loud enough that it would have masked the tone if the tone were present
        burst[hole] = 0.75 * rng.standard_normal(hole.sum())
        n = int(SR * 0.006)
        idx = np.where(hole)[0]
        burst[idx[:n]] *= np.linspace(0, 1, n)
        burst[idx[-n:]] *= np.linspace(1, 0, n)
        x = x + burst

    return ramp(0.9 * x / np.abs(x).max(), SR)


def tone_energy(x, sr=SR, f0=F0, win_ms=25):
    """Narrowband energy at f0 over time, by projecting onto a complex sinusoid."""
    n = int(sr * win_ms / 1000)
    hop = n // 2
    t = np.arange(n) / sr
    ref = np.exp(-2j * np.pi * f0 * t) * np.hanning(n)
    out, times = [], []
    for i in range(0, len(x) - n, hop):
        out.append(np.abs(x[i:i + n] @ ref) / n)
        times.append((i + n / 2) / sr)
    return np.array(times), np.array(out)


def main():
    OUT.mkdir(exist_ok=True)
    sigs = {name: build(name) for name in ("none", "silence", "noise")}
    names = {"none": "tone_continuous", "silence": "tone_gap", "noise": "tone_noise"}
    for k, v in sigs.items():
        sf.write(OUT / f"{names[k]}.wav", v, SR)

    print(f"a {F0:.0f} Hz tone with a {1000 * (GAP_END - GAP_START):.0f} ms hole "
          f"in the middle.\n")
    print(f"{'file':<20} {'energy at 1 kHz IN the hole':>28}   the hole is")

    for k, v in sigs.items():
        t, e = tone_energy(v)
        inside = e[(t >= GAP_START + 0.05) & (t < GAP_END - 0.05)]
        outside = e[(t < GAP_START - 0.05)]
        rel = inside.mean() / outside.mean()
        print(f"{names[k] + '.wav':<20} {rel:>27.1%}   "
              f"{'not there' if rel > 0.5 else 'REALLY THERE'}")

    print()
    print("careful with that middle column, because it is the whole mechanism.")
    print()
    print("the TONE is equally absent in both: it was deleted from the same samples.")
    print("but broadband noise has energy everywhere, so during the burst there IS")
    print("17.8% of the reference level sitting in the 1 kHz band. it just is not")
    print("the tone.")
    print()
    print("and a meter cannot tell those apart. energy at 1 kHz is energy at 1 kHz,")
    print("whatever produced it. so the machine is left with: something is there,")
    print("unclear what.")
    print()
    print("your auditory system resolves that ambiguity in a specific direction. the")
    print("noise is loud enough that it WOULD have masked the tone, so the evidence")
    print("is consistent with the tone continuing underneath. it concludes that the")
    print("tone continued, and hands you a tone. Bregman calls this old-plus-new.")
    print()
    print("LISTEN in this order:")
    print("  1. tone_gap.wav    you hear the hole. obviously.")
    print("  2. tone_noise.wav  same hole. you will hear one unbroken tone.")
    print()
    print("the tone you hear during the noise was never recorded. it is inference")
    print("from an ambiguous measurement, and notice which way the inference goes:")
    print("toward the simpler world, where one tone kept going, rather than the one")
    print("where a tone stopped and restarted in perfect phase behind a noise burst.")
    print()
    print("this is a construction, not a detection, and it is the same machinery")
    print("that lets you follow one voice at a party while other voices keep")
    print("stepping on the words.")

    # ---- the picture ----
    fig, axes = plt.subplots(3, 1, figsize=(13, 8))
    for ax, (k, v) in zip(axes, sigs.items()):
        t, e = tone_energy(v)
        ax.fill_between([GAP_START, GAP_END], 0, 1, color=BAD, alpha=0.13)
        ax.plot(t, e / e.max(), lw=2.6, color=ACCENT)
        ax.set_xlim(0, DUR)
        ax.set_ylim(0, 1.05)
        ax.set_yticks([])
        ax.set_ylabel(names[k].replace("tone_", ""), **text(15), color=FG)
    axes[-1].set_xlabel("seconds", **text(13), color=DIM)
    axes[0].set_title("energy at 1 kHz. the red band is the hole.",
                      **display(17), color=FG)
    fig.suptitle("the tone is deleted in both of the bottom two.\n"
                 "you only hear the hole in one of them.",
                 **display(19), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "continuity.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'continuity.png'}")


if __name__ == "__main__":
    main()
