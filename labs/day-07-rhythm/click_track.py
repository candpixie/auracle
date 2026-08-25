"""
Day 7: render the machine's beat as clicks over the music.

The tables say the tracker sits 320 ms from the beat. That is abstract. This
plays its answer on top of the audio so you can hear it landing between the
kicks instead of on them.

  beat_correct.wav   clicks on the real beat, for reference
  beat_machine.wav   clicks where the tracker actually put them
  beat_both.wav      both, panned apart, so the offset is unmissable

Run:  python labs/day-07-rhythm/click_track.py
"""

import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from silent_beat import BEATS, BARS, SPB, build, track
from tempo_sweep import SR

OUT = Path(__file__).parent / "out"


def beep(freq, sr=SR, dur=0.045):
    t = np.arange(int(sr * dur)) / sr
    return np.sin(2 * np.pi * freq * t) * np.exp(-55 * t)


def lay(base, times, freq, gain=0.75):
    out = base.copy()
    c = beep(freq)
    for t in times:
        i = int(t * SR)
        if 0 <= i < len(out) - len(c):
            out[i:i + len(c)] += gain * c
    return out


def main():
    OUT.mkdir(exist_ok=True)
    x = build()
    _, machine = track(x)
    true_beats = np.array([b * SPB for b in range(BEATS * BARS)])

    correct = lay(x, true_beats, 2400)
    machine_only = lay(x, machine, 1300)

    sf.write(OUT / "beat_correct.wav", 0.85 * correct / np.abs(correct).max(), SR)
    sf.write(OUT / "beat_machine.wav",
             0.85 * machine_only / np.abs(machine_only).max(), SR)

    # both at once, panned, so the gap is spatial as well as temporal
    left = lay(0.5 * x, true_beats, 2400)
    right = lay(0.5 * x, machine, 1300)
    n = min(len(left), len(right))
    stereo = np.stack([left[:n], right[:n]], axis=1)
    sf.write(OUT / "beat_both.wav", 0.85 * stereo / np.abs(stereo).max(), SR)

    offset_ms = float(np.median([np.min(np.abs(true_beats - m)) for m in machine])) * 1000
    print(f"the tracker's clicks sit {offset_ms:.0f} ms from the nearest real beat.")
    print(f"one beat at this tempo is {SPB * 1000:.0f} ms, so that is "
          f"{offset_ms / (SPB * 1000):.0%} of a beat.\n")
    print("LISTEN:")
    print("  beat_correct.wav   high clicks, on the kick. sounds right.")
    print("  beat_machine.wav   low clicks, where the machine put them.")
    print("  beat_both.wav      both. correct in the left ear, machine in the right.")


if __name__ == "__main__":
    main()
