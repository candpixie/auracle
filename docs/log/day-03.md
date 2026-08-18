# Day 3 — Amplitude becomes loudness

**Tue Aug 18, 2026**

## The ear

Your ear is not a microphone with a number attached. Sensitivity depends on frequency,
peaking around 3 to 4 kHz and falling off hard at the bottom and top. It also depends on
level, which is why a mix that sounded balanced quiet turns bass-heavy loud.

Fletcher and Munson mapped this in 1933 by asking people which tones sounded equally loud.
The modern version is ISO 226. Both are surveys. That matters more than it sounds: there
is no formula for loudness derivable from physics, because loudness is not a property of
the air. It's a property of a listener.

## The machine

Puts a number on it and hopes. Four of them: peak (the biggest sample), RMS (average
energy), A-weighting (RMS after discounting frequencies your ear is bad at), and LUFS,
which is the ITU standard every streaming platform normalises to, so it's the meter that
actually decides how loud your song comes out on Spotify.

## Where it breaks

I made five tones at 63, 250, 1000, 4000 and 12500 Hz with **exactly the same RMS**. The
63 Hz one is nearly inaudible. The 4 kHz one is piercing.

| meter | spread across the five | verdict |
|-------|----------------------|---------|
| peak | 0.0 dB | identical |
| RMS | 0.0 dB | identical |
| A-weighted | 27.2 dB | wildly different |
| LUFS | 6.7 dB | wildly different |

Peak and RMS can't even rank them. Every tone ties exactly, which isn't rounding, it's
those meters saying frequency is none of their business.

**And then the awkward one.** At 12500 Hz, A-weighting says -24.3 dB (discount it, your
ear is losing sensitivity up there) and LUFS says -16.7, one of the loudest tones in the
set. They disagree by 7.6 dB about the same file, and it's LUFS, the industry standard,
that contradicts perception.

That's a limitation of the standard, not of my code. K-weighting inside BS.1770 has a high
shelf that keeps boosting above 2 kHz to model head diffraction for broadband programme
material. It was never designed to judge a lone 12.5 kHz sine, and on one it's just wrong.
This is the meter every streaming service runs on every song.

## The thing that actually got me

Days 1 and 2 broke because the machine works in discrete chunks. Today broke for a
different and worse reason: **there is no correct answer to compute.**

Loudness isn't in the signal. Every meter I used is a compressed opinion about human
beings, derived from surveys of people in rooms in 1933 and 2003, and A-weighting and LUFS
disagree because they're opinions from different decades built for different purposes.

I keep expecting these failures to be engineering problems. Day 1 was algebra. Day 2 was
algebra. Day 3 is a survey.

## What surprised me

<!-- fill this in yourself -->

## Resources

- Fletcher and Munson, "Loudness, its definition, measurement and calculation," JASA, 1933
- ISO 226:2003, equal-loudness-level contours
- IEC 61672-1, A-weighting
- ITU-R BS.1770-4, loudness and true-peak measurement (free from the ITU)
- pyloudnorm (Steinmetz and Reiss) — https://github.com/csteinmetz1/pyloudnorm

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-03-loudness

## Post

**Hook:** these five sounds are identical. your ear disagrees.
**Artifact:** `out/all_five_tones.wav` plus the meter table
