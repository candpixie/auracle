# Day 7 — The beat is not in the signal

**Sat Aug 22, 2026**

## The ear

Infers a pulse and then keeps it. You tap it, come in on it after a rest, feel a downbeat
nothing marks. The beat is a construction and it survives the absence of evidence.

You also know instantly which layer is the beat. Kick on 1 and 3, hat on every "and" —
nobody has to be told which one to tap.

## The machine

Find the onsets, build a tempogram, fit a periodic grid. Events first, then a beat.

## Where it breaks

**A third of tempo estimates are metrically off.** I swept a plain four-on-the-floor from
60 to 200 BPM. 34% wrong, and **zero of the misses are non-metrical.** Every one is the
same rhythm counted at half time, double time, or the dotted level. It never failed to
find a periodicity; it found a real one and picked a level I wouldn't tap.

**And "the tempo" isn't a property of the audio.** librosa multiplies the tempogram by a
log-normal prior centred on `start_bpm`, default 120. Same file: 60 BPM reads as 60.1 with
`start_bpm=60` and 117.5 with `start_bpm=120`. The answer depends on a parameter someone
picked.

**Then the one I didn't expect.** Kick on 1 and 3, hat on every off-beat. The tracker
lands **23 ms from the hats and 320 ms from the kicks.** It's on the off-beat. Tempo
correct, phase half a beat out, and nothing in the output says so.

It's not confused. The hats are a perfectly even pulse and the kicks aren't, so the hats
win. Remove the hats and it finds the kicks — at half tempo.

## The experiment that couldn't work

I built that second lab to test something else entirely: remove the downbeat, watch the
tracker lose a bar line I could still feel.

It changed nothing. Byte-identical output in both conditions.

I assumed my code was broken and checked whether the signals actually differed. They do,
total energy 1272 vs 672. They differ and the tracker doesn't care, **because it was never
using the downbeat.** It had locked to the hats from the first bar.

So the experiment I designed could not have produced a result, and working out why is what
produced the real one. That's twice in three days that the null result taught me more than
the measurement I planned. I'm starting to think that's the actual skill.

## What surprised me

<!-- fill this in yourself -->

## Resources

- Bello, Daudet, Abdallah, Duxbury, Davies, Sandler, "A Tutorial on Onset Detection in Music Signals," IEEE TSAP, 2005
- Ellis, "Beat Tracking by Dynamic Programming," JNMR, 2007
- Grosche, Müller, Kurth, "Cyclic tempogram," ICASSP, 2010
- Müller, *Fundamentals of Music Processing*, Ch. 6
- madmom (state of the art for beat tracking)

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-07-rhythm

## Post

**Hook:** the computer is dancing on the wrong beat
**Artifact:** `normal.wav` — tap along, then see where the machine put the grid
