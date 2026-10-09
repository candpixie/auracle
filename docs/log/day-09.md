# Day 9 — Source separation, the learned answer

**Thu Oct 8, 2026.** Planned for Aug 24. Six weeks late, written on the real date rather
than the one that would make the streak look unbroken.

Day 8 ended with no entry point: harmonicity needs the f0s, the f0s need the separation.
This is the day the field stops writing rules. Except the two methods here are still
rules, and watching exactly how they break is the argument for learning one instead.

## The ear

You hear the singer apart from the band. One pressure wave, no stems, no second take, no
training.

## The machine

HPSS: in a spectrogram, held notes are horizontal and hits are vertical, so median-filter
along each axis. Ten lines, no training, **19.7 dB SI-SDR** on a mixture that suits it.

NMF: factor the magnitude spectrogram into K templates and their activations. Also works,
also unsupervised, **16.5 dB** at K=4.

Everything measured against sources I synthesised, so leakage and reconstruction error
can be told apart.

## Where it breaks

**HPSS is a bet that the music holds still.** Horizontal and vertical are assumptions:
that the singer does not bend and the hit does not ring. Give the singer a half-semitone
vibrato, which is ordinary pop singing, and it costs 3.6 dB. Two semitones costs 6.8.
Let the hit ring for 300 ms like a cymbal and the **harmonic** stem loses 14 dB, because
a long tail is a horizontal smear so the filter posts the cymbal to the singer.

Both failures point the same way. Vibrato is a held note behaving vertically, a cymbal is
a hit behaving horizontally, and the model has two bins. Expression is the diagonal.

librosa's `margin` adds the third bin, a residual for anything ambiguous. It does not
rescue it. At margin 8 both stems are worse and 43% of the audio has been thrown away.
The vibrato is in both stems because it genuinely is both things.

**NMF finds the parts and will not name them.** At K=16 the oracle gets 15 dB out of the
components and a real unsupervised labelling rule gets 4.1. The factorisation is fine,
11 dB is lost purely to deciding which component is the singer. Truth is 14 of 16
components are drums, the median-split rule insists on 8. To label the components you
need the sources, and the components were how you were going to find the sources. Day 8's
loop in a different costume.

**And then the thing I did not plan to spend the day on.** Hand SDR the true stem,
undamaged, and break it on purpose:

- A 1-sample delay, 45 microseconds, scores **15.9 dB on SI-SDR. So does punching 100 ms
  of silence into it.** The metric cannot tell a shift nothing can hear from a hole that
  swallows a syllable.
- The two standard SDRs **disagree by over 200 dB on the same file**, because bss_eval
  allows any 512-tap filter and a delay is a filter. Which one is cited decides whether a
  system looks broken or perfect.
- **Both call a polarity flip a flawless separation.** Scaling is free and -1 is a scale.
  Put that stem back in the mix and it cancels the singer out of the record: -200 dB
  against the original mixture.

Scale invariance and filter invariance are only free if you never put the stem back, and
putting it back is the reason to separate it.

Scoring the remix instead of the stem catches all of it in one line of arithmetic, and it
reorders the rest sensibly too: being 6 dB loud is the worst of the real damage, and the
inaudible delay drops to the bottom where it belongs.

## What surprised me

<!-- fill this in yourself -->

## Caveats

Synthetic, two sources, and by construction HPSS's best case, so none of these dB values
compare to MUSDB numbers. No learned baseline: Demucs needs torch and this environment
does not have it, so day 14 still owes that comparison. One synthetic case does not prove
the metric fails on real music, only that its invariances are not the ear's. Day 16.

## Resources

- Fitzgerald, "Harmonic/Percussive Separation using Median Filtering," DAFx 2010
- Driedger, Müller, Disch, "Extending harmonic-percussive separation of audio signals," ISMIR 2014
- Lee and Seung, "Learning the parts of objects by non-negative matrix factorization," Nature 1999
- Vincent, Gribonval, Févotte, "Performance measurement in blind audio source separation," IEEE TASLP 2006
- Le Roux et al., "SDR: half-baked or well done?", ICASSP 2019
- Müller, *Fundamentals of Music Processing*, Chapter 8
- Namballa, Roginska, Fuentes, ISMIR 2025, and Namballa and Fuentes, ISMIR 2026, on whether
  separation models preserve spatial information and whether the metrics for it are reliable.
  The binaural version of the same problem, and sharper: interaural cues live in exactly the
  phase and filter differences these metrics forgive.

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-09-separation

## Post

**Hook:** two standard metrics agree this separation is flawless, and it deletes the singer
**Artifact:** the polarity-flip row, 'perfect' on both metrics, -200 dB in the mix
