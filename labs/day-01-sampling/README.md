# Day 01 — Air pressure becomes a number

## The ear does this

The eardrum is a transducer. Pressure variation in air becomes mechanical motion,
the ossicles pass it to the cochlea, and hair cells convert it into neural firing.
It is a continuous system from end to end. There is no sample rate anywhere in it.

## The machine does this

Measures the pressure a fixed number of times per second and stores each
measurement as an integer.

- **Sample rate**: how often. 44,100 times a second is standard.
- **Nyquist**: you can only represent frequencies below *half* the sample rate.
  Hearing tops out near 20 kHz, so you need 40 kHz minimum, plus headroom for
  the anti-alias filter. That is where 44.1 kHz comes from.
- **Bit depth**: how precisely each measurement is stored. 16 bits gives roughly
  96 dB of dynamic range, and the leftover error is quantization noise.

## Where it breaks

**Aliasing.** Sample too slowly and frequencies above Nyquist do not vanish, they
*fold back* and reappear as lower frequencies, indistinguishable from real ones.
It is not degradation you can clean up afterward. The information is gone and has
been replaced with something false.

And the deeper point: **aliasing has no perceptual counterpart at all.** The cochlea
cannot alias, because it never samples. This is the cleanest example in the whole
17 days of the machine not being a model of the ear, just a substitute for it.

## Run it

```bash
source .venv/bin/activate
python labs/day-01-sampling/staircase.py          # optionally pass an audio file
python labs/day-01-sampling/aliasing.py
```

Then open `out/` and **listen in this order**:

1. `sweep_48k.wav` — climbs to 20 kHz and stops.
2. `sweep_resampled_8k.wav` — climbs, stops earlier at 4 kHz. Correct.
3. `sweep_aliased_8k.wav` — climbs, hits 4 kHz, and comes back **down**.

That descent is a frequency that was never played.

## Output

- `out/staircase.png` — the same waveform at 1000 ms, 50 ms, 5 ms, 1 ms. In the
  last panel the samples become visible as dots, and the line connecting them is
  revealed as an assumption.
- `out/aliasing.png` — three spectrograms, with the predicted fold pattern
  overlaid on the broken one. The measured alias should sit exactly on the
  dashed prediction line.
- Three `.wav` files (gitignored, regenerate by running the script).

## Sources

- Julius O. Smith, *Mathematics of the DFT*, CCRMA Stanford —
  https://ccrma.stanford.edu/~jos/mdft/
- Meinard Müller, *Fundamentals of Music Processing*, Chapter 2 —
  https://www.audiolabs-erlangen.de/resources/MIR/FMP/C2/C2.html
- Shannon, "Communication in the Presence of Noise," Proc. IRE, 1949
- librosa `load` / `resample`; scipy `resample_poly`, `chirp`
