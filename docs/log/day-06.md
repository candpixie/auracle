# Day 6 — Pitch that isn't there

**Fri Aug 21, 2026**

## The ear

Hears a pitch that is not in the signal.

Play harmonics at 400, 600, 800 and 1000 Hz with **nothing at 200 Hz** and you hear
200 Hz. The partials are all multiples of 200, so the waveform still completes a cycle
200 times a second, and your auditory system reports the repetition rate rather than the
lowest frequency present.

It's why a phone speaker that can't physically produce 60 Hz still lets you hear a bass
line. It reproduces the harmonics and your brain supplies the root.

## The machine

Estimates f0: autocorrelation, YIN, pYIN, CREPE.

## The measurement

Energy at 200 Hz in the missing-fundamental signal: **0.000000**. Zero, not small.

| method | full | f0 removed |
|---|---|---|
| naive autocorrelation | 200.5 Hz | **100.0 Hz** |
| YIN | 200.2 Hz | **200.0 Hz** |

YIN agrees with my ear. The naive method drops an octave.

## Where it breaks

**The octave error is structural.** On the missing-fundamental signal, autocorrelation at
200 Hz is 0.9989 and at 100 Hz is 0.9990. Tied to three decimal places, and **the wrong
one wins by 0.0001.**

Not bad luck: if a signal repeats every T it also repeats every 2T, so every true peak
has an equally tall impostor an octave below it. YIN's cumulative mean normalised
difference function exists specifically to break that tie.

**Then polyphony, which is a different category of failure.** One note at a time, YIN is
accurate to half a cent. Play a C major triad and it returns **130.8 Hz**, which is C3,
an octave below the lowest note in the chord.

And it isn't random. A major triad is near a 4:5:6 ratio, so the three waveforms realign
only after a long common period. YIN found the period of the *mixture*, correctly. The
period of a mixture is not a note anybody played.

Your ear does something adjacent, since you hear a C major chord as rooted on C. The
difference is you also hear three separate notes. YIN returns one number because one
number is all its model has room for.

## The thing I keep noticing

Six days, and the pattern has changed shape. Days 1 to 4 the machine lost to the ear.
Today it drew: YIN gets the missing fundamental right, for essentially the same reason
you do, by tracking repetition rather than looking for the lowest frequency present.

Then it lost completely, on a chord a beginner could name.

## What surprised me

<!-- fill this in yourself -->

## Resources

- de Cheveigné and Kawahara, "YIN, a fundamental frequency estimator for speech and music," JASA, 2002
- Mauch and Dixon, "pYIN," ICASSP, 2014
- Kim, Salamon, Li, Bello, "CREPE," ICASSP 2018 (arXiv:1802.06182)
- Schouten, "The perception of subjective tones," 1938
- Terhardt, "Pitch, consonance, and harmony," JASA, 1974
- Müller, *Fundamentals of Music Processing*, Ch. 8

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-06-pitch

## Post

**Hook:** you're about to hear a note that isn't there
**Artifact:** `reference_200hz.wav` then `missing_fundamental.wav`
