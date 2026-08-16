"""
Day 1: the staircase.

The single most important idea of the whole 17 days, and it takes one figure:
a digital sound is a list of numbers. Amplitude, measured 44,100 times a second.
Every transform in every later lab is a rearrangement of that list.

Zoom in far enough and the smooth waveform stops being smooth.

Run:  python labs/day-01-sampling/staircase.py [path/to/audio.wav]

With no argument it synthesizes a 440 Hz tone so the lab runs with no assets.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT = Path(__file__).parent / "out"

# each panel shows this many milliseconds. the last one is short enough that
# individual samples become visible as steps.
ZOOMS_MS = [1000, 50, 5, 1]


def load(path=None):
    if path:
        x, fs = sf.read(path, always_2d=False)
        if x.ndim > 1:
            x = x.mean(axis=1)  # mono, so there is one number per instant
        return x, fs, Path(path).name
    fs = 44_100
    t = np.linspace(0, 1.0, fs, endpoint=False)
    return 0.5 * np.sin(2 * np.pi * 440 * t), fs, "synthesized 440 Hz"


def main():
    OUT.mkdir(exist_ok=True)
    x, fs, label = load(sys.argv[1] if len(sys.argv) > 1 else None)

    # start a little way in, so we're not looking at silence or a fade
    start = min(len(x) // 3, int(fs * 5))

    fig, axes = plt.subplots(len(ZOOMS_MS), 1, figsize=(11, 9))

    for ax, ms in zip(axes, ZOOMS_MS):
        n = max(int(fs * ms / 1000), 2)
        seg = x[start:start + n]
        t_ms = np.arange(len(seg)) / fs * 1000

        if len(seg) <= 200:
            # few enough samples that we can draw each one. this is the payoff:
            # the "wave" is dots, and the line between them is an assumption.
            ax.step(t_ms, seg, where="post", lw=1.0, color="#7c5cff")
            ax.plot(t_ms, seg, "o", ms=4, color="#ff5c8a")
        else:
            ax.plot(t_ms, seg, lw=0.7, color="#7c5cff")

        # report the span we actually got, not the one we asked for; near the end
        # of a short file the first panel can be truncated
        actual_ms = len(seg) / fs * 1000
        ax.set_title(f"{actual_ms:.0f} ms  ({len(seg)} samples)", fontsize=10, loc="left")
        ax.set_xlabel("time (ms)")
        ax.set_ylabel("amplitude")
        ax.margins(x=0)

    fig.suptitle(f"a sound is a list of numbers  ·  {label}  ·  {fs} Hz", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "staircase.png", dpi=150)

    print(f"source: {label}")
    print(f"sample rate: {fs} Hz  ->  {fs} numbers per second per channel")
    print(f"total samples: {len(x):,}   duration: {len(x) / fs:.2f} s")
    print(f"dtype in memory: {x.dtype}   range: [{x.min():.3f}, {x.max():.3f}]")
    print()
    print(f"wrote {OUT / 'staircase.png'}")
    print("look at the bottom panel. that is what the machine actually receives.")


if __name__ == "__main__":
    main()
