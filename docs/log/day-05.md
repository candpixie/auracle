# Day 5 — Timbre, or why a violin is not a flute

**Thu Aug 20, 2026**

## The ear

Identifies an instrument in well under a second, often from the attack alone, before one
full pitch period has finished.

Timbre is the only perceptual attribute defined negatively. The ANSI definition is
basically "whatever makes two sounds with the same pitch, loudness and duration still
sound different." Everything left over.

## The machine

Spectral shape scalars (centroid, rolloff, flatness, zero-crossing rate), then MFCCs:
mel spectrum, log, DCT, keep the low coefficients. Built in 1980 for speech recognition,
where the talker's pitch is a nuisance variable you want gone.

## The measurement

Three synthetic instruments crossed with two melodies, then: how much does each feature
move when the instrument changes, versus when the melody changes?

| feature | instrument differs | melody differs | ratio |
|---|---|---|---|
| MFCC | 0.144 | 0.004 | **36.7x** |
| chroma | 0.016 | 0.592 | **0.03x** |
| centroid | 0.165 | 0.003 | 52.5x |
| rolloff | 0.268 | 0.006 | 45.5x |

Clean result. MFCCs are a timbre feature and a pitch-destroying one, and chroma is the
mirror image.

Side note that deflated me slightly: **spectral centroid, a single number, separates
these instruments better than 13 MFCCs.** MFCCs are not magic.

## Where it breaks

**Mean-pooled MFCCs cannot see time reversal.** Reverse a note and the MFCCs move by
0.000004, against 0.324 between two different instruments. That is 0.001% of an
instrument change.

And it is not luck, it is guaranteed. For a real signal `|DFT|` is exactly invariant
under time reversal (I measured 1.4e-14). So every frame keeps its magnitude spectrum,
only the frame order flips, and mean-pooling throws order away.

Play the reversed pluck. It is an organ swell. Your ear reclassifies it in one note and
the feature is structurally incapable of noticing. Every "average the MFCCs over the
clip" tagging pipeline inherits this.

## The negative result, which is the actual day

Saldanha and Corso (1964) cut the attack off recorded notes and identification collapsed.
I tried to reproduce it and got the opposite three times: the sustain separated my
instruments better than the attack did.

The literature is not wrong. My stimulus is.

Real instruments holding the same note have fairly *similar* steady spectra, and that
similarity is exactly why removing the attack destroys human identification. Mine are
nothing alike: one is nearly a sine, one suppresses every even harmonic, one has nine
strong partials. The sustains are cartoonishly distinct, so of course the sustain wins.

**I built a dataset in which the effect I was looking for could not appear**, and only
caught it because the number came out backwards.

Two bugs on the way there, both mine:

1. librosa's default `n_fft=2048` is 93 ms at this sample rate, longer than the 50 ms
   attack I was analysing. The attack MFCCs were largely describing zero-padding.
2. I then added spectrally distinct onset transients, assuming envelope was the missing
   ingredient. It helped and did not flip the result, because the sustains were still
   too different.

The easy move was to keep adjusting the synthesis until it matched the textbook. I want
to remember that I didn't, because on day 16 I have to do this to my own results.

## What surprised me

<!-- fill this in yourself -->

## Resources

- Davis and Mermelstein, "Comparison of Parametric Representations for Monosyllabic Word Recognition," IEEE TASSP, 1980
- Saldanha and Corso, "Timbre Cues and the Identification of Musical Instruments," JASA, 1964
- Grey, "Multidimensional perceptual scaling of musical timbres," JASA, 1977
- Sethares, *Tuning, Timbre, Spectrum, Scale*, Springer, 2005
- Müller, *Fundamentals of Music Processing*, Ch. 1

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-05-timbre

## Post

**Hook:** the standard tool for music was built to ignore music
**Artifact:** `plucked_A4.wav` then `plucked_A4_reversed.wav`, with the 0.001% number
