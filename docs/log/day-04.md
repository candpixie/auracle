# Day 4 — The perceptual frequency axis

**Wed Aug 19, 2026**

## The ear

Pitch is roughly logarithmic. An octave is a doubling, and it feels like the same size
step wherever you play it. 100 to 200 Hz and 2000 to 4000 Hz are both one octave, even
though one spans 100 Hz and the other 2000.

Underneath that, the cochlea groups nearby frequencies into critical bands that widen as
you go up. Bark and ERB are two measurements of that widening.

## The machine

Warps the frequency axis to try to match. The mel scale (1937, built by asking people to
adjust a tone until it sounded "half as high"), Bark (1961, critical bands), and the CQT
(1991), which isn't a perceptual scale at all, just log-spaced bins, one per semitone.

## Where it breaks

I synthesized a chromatic scale, C3 to C6, 37 steps, every step the same *musical* size.
Then measured whether one semitone covers the same distance up each axis.

| representation | semitone step, C3 → C6 |
|---|---|
| linear STFT | 7.55x |
| mel, Slaney (librosa default) | 7.23x |
| mel, HTK | 3.66x |
| CQT | 1.00x |

**Over the musical register, librosa's default mel is 96% as uneven as no warping at
all.** That is not what I expected from a scale whose entire job is to be perceptual.

And then the actual finding. **There are two mel formulas in common use.** HTK is
`2595·log10(1 + f/700)`, logarithmic everywhere. Slaney is *linear below 1000 Hz* and
logarithmic above, and that is the definition, not an approximation. librosa defaults to
Slaney, and 39 of its 128 default bins sit inside that linear region, spaced a constant
26.2 Hz apart.

C3 to C6 lives almost entirely inside it. So across the range where nearly every melody
on earth sits, the perceptual axis isn't being perceptual.

The two disagree by **2x** on the same signal, and papers say "mel spectrogram" without
specifying which one. If a pitch-related result ever comes out off by roughly a factor
of two from a published number, this is a candidate explanation.

## Why mel is still fine, actually

It was never for this. Mel was fit to speech, where the fundamental matters far less than
the formants sitting above 1 kHz, which is exactly where Slaney mel *does* compress.
Tomorrow's MFCCs then throw pitch away deliberately. Mel is a good tool doing the job it
was built for, borrowed by a field with a different job.

That's a different flavour of failure from days 1 to 3. Not sampling, not algebra, not a
survey. Just a tool used outside its domain by people who inherited it.

## Bug worth recording

My two scripts reported 7.23x and 3.72x for the same quantity. One had `hz_to_mel`
hand-written with the HTK formula; the other interpolated onto librosa's real bin
centres, which are Slaney. Neither was wrong. They were measuring two different scales
that share a name.

I'd have shipped whichever number I looked at first if I hadn't cross-checked. Third day
running that the bug surfaced because two things disagreed, not because anything looked
broken.

## What surprised me

<!-- fill this in yourself -->

## Resources

- Stevens, Volkmann and Newman, "A Scale for the Measurement of the Psychological Magnitude Pitch," JASA, 1937
- Zwicker, "Subdivision of the Audible Frequency Range into Critical Bands," JASA, 1961
- Glasberg and Moore, "Derivation of auditory filter shapes from notched-noise data," Hearing Research, 1990
- Judith C. Brown, "Calculation of a constant Q spectral transform," JASA, 1991
- Slaney, *Auditory Toolbox*, Interval Research, 1998
- librosa `mel_frequencies`, `cqt`, `melspectrogram` (see the `htk=` flag)

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-04-scales

## Post

**Hook:** why a piano looks wrong to a computer
**Artifact:** `out/chromatic.png`, the CQT panel is a straight staircase and the other two curve
