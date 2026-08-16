# Day 1 — Air pressure becomes a number

**Sun Aug 16, 2026**

## The ear

The eardrum is a transducer: pressure variation in air becomes mechanical motion,
the ossicles pass it to the cochlea, hair cells turn it into neural firing. Continuous
all the way through. There is no sample rate anywhere in human hearing.

## The machine

A digital sound is a list of numbers. Amplitude, measured a fixed number of times per
second, each measurement stored as an integer. That is the whole representation, and
every transform in the next sixteen days is a rearrangement of that list.

Three numbers describe the entire scheme:

- **Sample rate** — how often you measure. 44,100 Hz is standard.
- **Nyquist** — you can only represent frequencies below half the sample rate. Human
  hearing tops out near 20 kHz, so you need at least 40 kHz, plus headroom for the
  anti-alias filter. That is where 44.1 comes from. It is not arbitrary.
- **Bit depth** — how precisely each measurement is stored. 16 bits gives about 96 dB
  of dynamic range; the error left over is quantization noise.

## Where it breaks

**Aliasing.** Frequencies above Nyquist do not disappear when you sample too slowly.
They *fold back* and come out as lower frequencies that are indistinguishable from real
ones. This is not degradation you can undo. The information is gone and has been
replaced with something false.

I generated a sweep from 20 Hz to 20 kHz and decimated it to 8 kHz without filtering.
It climbs, hits the 4 kHz ceiling, and comes back down, twice. Every descending part is
a frequency that was never played.

And the part that matters for this whole project: **aliasing has no perceptual
counterpart.** The cochlea cannot alias, because it never samples. Day one and the
machine is already failing in a way the ear cannot. That is the pattern for the next
sixteen days.

## What surprised me

<!-- fill this in yourself. this section is the reason anyone reads a learning log. -->

## Resources

- Julius O. Smith, *Mathematics of the DFT*, CCRMA Stanford — https://ccrma.stanford.edu/~jos/mdft/
- Meinard Müller, *Fundamentals of Music Processing*, Ch. 2 — https://www.audiolabs-erlangen.de/resources/MIR/FMP/C2/C2.html
- Shannon, "Communication in the Presence of Noise," Proc. IRE, 1949
- scipy `chirp`, `resample_poly`; librosa `load`, `resample`

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-01-sampling

## Post

**Hook:** this sound is lying to you
**Artifact:** the descending sweep (`out/sweep_aliased_8k.wav`) + the three spectrograms
