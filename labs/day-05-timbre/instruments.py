"""
Day 5: three synthetic instruments that differ only in timbre.

Real recordings would be better, but they also drag in room, mic, player and
copyright. Synthesising means the ONLY thing that differs between these three is
the spectral recipe, which is exactly the variable under test.

The recipes are not arbitrary:

  flute      near-sinusoidal. weak upper harmonics, plus breath noise. slow
             attack (~80 ms), because you have to get an air column moving.
  clarinet   a cylindrical bore closed at one end suppresses EVEN harmonics, so
             1, 3, 5, 7 dominate. that is a real acoustic fact, not a stylisation,
             and it is why a clarinet sounds hollow.
  plucked    fast attack (~3 ms), exponential decay, all harmonics present, plus
             slight inharmonicity (real strings are stiff, so overtones run sharp
             of exact multiples).

Each also gets an ONSET TRANSIENT with its own spectral character, which is the
part that took a second pass to get right. A first version varied only the
harmonic recipe and the attack TIME, and measured attack and sustain as equally
informative. That was correct about the code and wrong about instruments: in a
real one the onset is not a quieter version of the sustain, it is a different
sound. Breath noise, a reed's chiff, the click of a pick. That is what people
are actually recognising in the first 50 ms.

Run:  python labs/day-05-timbre/instruments.py
"""

from pathlib import Path

import numpy as np
import soundfile as sf

OUT = Path(__file__).parent / "out"

SR = 22_050
DUR = 0.55

# harmonic amplitude recipes, index 0 = fundamental
# onset: (amplitude, decay rate, low-pass smoothing width in samples).
# a wide smoothing window means a dark, breathy transient; a narrow one means a
# bright click.
RECIPES = {
    "flute":   dict(harm=[1.0, 0.25, 0.08, 0.03, 0.01],
                    attack=0.080, decay=0.0, noise=0.010, inharm=0.0,
                    onset=(0.55, 45.0, 12)),      # airy breath, dark
    "clarinet": dict(harm=[1.0, 0.04, 0.60, 0.03, 0.35, 0.02, 0.18, 0.01, 0.08],
                    attack=0.030, decay=0.0, noise=0.003, inharm=0.0,
                    onset=(0.30, 160.0, 4)),      # short reed chiff, mid
    "plucked": dict(harm=[1.0, 0.55, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03],
                    attack=0.003, decay=4.5, noise=0.0, inharm=4e-4,
                    onset=(0.75, 900.0, 1)),      # bright percussive click
}

INSTRUMENTS = list(RECIPES)


def note(name, f0, sr=SR, dur=DUR, seed=0):
    r = RECIPES[name]
    rng = np.random.default_rng(seed)
    t = np.arange(int(sr * dur)) / sr
    x = np.zeros_like(t)

    for i, amp in enumerate(r["harm"], start=1):
        # stiff strings: partials run sharp of exact multiples
        f = f0 * i * np.sqrt(1 + r["inharm"] * i * i) if r["inharm"] else f0 * i
        if f >= sr / 2:
            break
        x += amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))

    if r["noise"]:
        # breath noise, band-limited around the fundamental so it reads as air
        n = rng.standard_normal(len(t))
        n = np.convolve(n, np.ones(24) / 24, mode="same")
        x += r["noise"] * n * len(r["harm"])

    # onset transient: a burst with its own spectral colour, not just a fade-in
    amp, rate, width = r["onset"]
    burst = rng.standard_normal(len(t))
    if width > 1:
        burst = np.convolve(burst, np.ones(width) / width, mode="same")
    x += amp * burst * np.exp(-rate * t)

    # amplitude envelope
    env = np.ones_like(t)
    a = max(int(sr * r["attack"]), 1)
    env[:a] = np.linspace(0, 1, a) ** 2
    if r["decay"]:
        env *= np.exp(-r["decay"] * t)
    rel = int(sr * 0.04)
    env[-rel:] *= np.linspace(1, 0, rel)

    x *= env
    return 0.5 * x / (np.abs(x).max() + 1e-12)


def melody(name, notes_hz, gap=0.06, sr=SR):
    parts = []
    for i, f in enumerate(notes_hz):
        parts.append(note(name, f, seed=i))
        parts.append(np.zeros(int(sr * gap)))
    return np.concatenate(parts)


# two melodies, so we can vary pitch content independently of instrument
def hz(names):
    table = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
             "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25}
    return [table[n] for n in names]


MELODIES = {
    "tune_A": hz(["C4", "E4", "G4", "C5", "G4", "E4"]),
    "tune_B": hz(["A4", "F4", "D4", "B4", "D4", "F4"]),
}


def main():
    OUT.mkdir(exist_ok=True)
    for inst in INSTRUMENTS:
        for mel, notes in MELODIES.items():
            x = melody(inst, notes)
            sf.write(OUT / f"{inst}_{mel}.wav", x, SR)
        sf.write(OUT / f"{inst}_A4.wav", note(inst, 440.0), SR)

    print(f"wrote {len(INSTRUMENTS) * (len(MELODIES) + 1)} files to {OUT}\n")
    print("listen to the three single notes first. all exactly A4, 440 Hz:")
    for inst in INSTRUMENTS:
        print(f"  {inst}_A4.wav")
    print("\nsame pitch every time. you can still tell them apart instantly.")
    print("that difference is timbre, and it is defined by what it is NOT:")
    print("everything left over once pitch, loudness and duration are accounted for.")


if __name__ == "__main__":
    main()
