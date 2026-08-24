# Day 8 — The cocktail party problem

**Sun Aug 23, 2026**

The keystone day. This is the field's founding problem.

## The ear

Bregman's auditory scene analysis. One pressure wave arrives at your eardrum with every
source in the room summed into it, and you unpick it into streams without effort. The
cues are grouping heuristics: common onset, harmonicity, common fate, continuity, spatial
location.

## The machine

Code those cues up directly and hope they compose.

## Where it breaks

**Your ear invents sound that was deleted.** I cut a 300 ms hole in a 1 kHz tone and
filled it with loud noise. The tone is gone — deleted from those samples — but broadband
noise puts 17.8% of the reference level at 1 kHz anyway. A meter can't tell tone-energy
from noise-energy.

Your auditory system resolves that ambiguity in one direction: the noise is loud enough
that it *would* have masked the tone, so it concludes the tone continued and hands you
one. Play `tone_gap.wav` then `tone_noise.wav`. Same hole. You only hear one.

**Then the cue that worked and was still useless.** I implemented harmonicity, handed it
both true f0s for free, and expected it to struggle. It got **100% purity** on both
voices.

So I went looking for where it actually fails:

| interval | bins only B owns | separable? |
|---|---|---|
| major third | 77 | yes |
| perfect fifth | 18 | yes |
| **octave** | **0** | **impossible** |

At the octave, voice B owns zero bins. Every harmonic of 440 is also a harmonic of 220.
Not hard — impossible.

And the ordering is the finding. Third, fifth, octave is increasing **consonance**, and
consonance *is* harmonic overlap. **Music is built out of exactly the cases that defeat
this cue.** The better two notes sound together, the less separable they are. I did not
expect the answer to be "the problem is that it's music."

**And then the loop.** Every number above assumed I knew both f0s. YIN on the mixture
returns 274.6 Hz — neither note, for the reason day 6 established.

To use harmonicity you need the f0s. To get the f0s you need the voices separated. There
is no entry point. Every cue is real, correctly implemented, and the system cannot start.

That is why rule-based CASA stalled.

## What surprised me

<!-- fill this in yourself -->

## Resources

- Bregman, *Auditory Scene Analysis*, MIT Press, 1990
- Wang and Brown, *Computational Auditory Scene Analysis*, Wiley/IEEE, 2006
- Warren, "Perceptual restoration of missing speech sounds," Science, 1970
- Darwin, "Perceptual grouping of speech components differing in fundamental frequency," 1981
- Cherry, "Some experiments on the recognition of speech, with one and with two ears," JASA, 1953

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-08-asa

## Post

**Hook:** the hardest thing your ears do, you've never noticed
**Artifact:** `tone_gap.wav` then `tone_noise.wav`
