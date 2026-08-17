# Day 2 — Frequency becomes pitch

**Mon Aug 17, 2026**

## The ear

The basilar membrane is a mechanical frequency analyzer. Stiff and narrow at one end,
floppy and wide at the other, so high frequencies peak near the base and low ones near the
apex. Position becomes frequency, and that map, **tonotopy**, survives all the way into
auditory cortex. There is a physical place in your head for 440 Hz.

And it does it continuously, all at once. It is not chopping the sound into chunks.

## The machine

The DFT correlates the signal against a sinusoid at every candidate frequency. Where a
frequency is present the products reinforce and the sum is large; where it isn't they
cancel. That's the entire idea, and it's four lines of code.

I wrote it out by hand and checked it against numpy: max difference 1.4e-10, which is
float rounding. The FFT gave the same answer 400x faster. It is not a different
transform, just the same one computed without redoing identical work.

Then, to find out *when* something happened, you chop the signal up and transform each
chunk. That's the STFT, and that's where it falls apart.

## Where it breaks

**You cannot know when and what at the same time.**

Short windows tell you *when* precisely and *what* vaguely. Long windows do the reverse.

I built a signal to make this inescapable: two tones 20 Hz apart, which need a window
longer than 50 ms to separate, plus two clicks 20 ms apart, which need a window shorter
than 20 ms. The two requirements contradict each other, so every window length loses one
of them, and you can watch it happen across three panels.

| window | time res | freq res | product |
|--------|----------|----------|---------|
| 128 | 2.9 ms | 345 Hz | 1000 |
| 1024 | 23.2 ms | 43 Hz | 1000 |
| 8192 | 185.8 ms | 5 Hz | 1000 |

The product never changes. I want to be honest about why: it can't. Time resolution is
`n/fs`, frequency resolution is `fs/n`, so the product is 1 no matter what you pick. It's
algebra, not a measurement.

That's what makes it a wall instead of a bug. Nobody is going to fix this. You are not
gaining resolution by picking a better window, you are choosing which axis to spend a
fixed budget on.

**And here the ear straightforwardly wins.** The cochlea doesn't use one window length. It
behaves like a bank of filters that are broad at high frequencies and narrow at low ones,
so it gets sharp timing where transients live and sharp pitch where pitch lives. The STFT
picks one window for the entire signal and eats the consequences everywhere.

Second failure, smaller: **spectral leakage.** The DFT assumes your chunk loops forever,
so if the waveform doesn't end where it started, the imagined loop has a discontinuity in
it, and discontinuities are broadband. A 100.5 Hz sine smears across the whole spectrum at
only -32 dB down. The same sine at 100.0 Hz, which happens to fit the chunk exactly, is
clean. A Hann window takes the bad case to -86 dB. Real music never happens to fit, so
this is the normal case.

## What surprised me

<!-- fill this in yourself -->

## A pattern I'm noticing

Two days, two failures, and they rhyme. Day 1: sample too slowly and the machine invents
a frequency. Day 2: pick a window and the machine has to be vague about either time or
frequency. Both are consequences of the machine working in discrete chunks, and the ear
does neither because it never chunks anything.

I did not expect the thesis of this project to show up this early.

## Bugs worth recording

Both figures were wrong the first time, in the same way: I plotted something *adjacent* to
the point instead of the point.

The tone panels were spectrograms, but two tones 20 Hz apart beat at 20 Hz, and the
beating dominated the picture so thoroughly that no panel answered the actual question.
Swapping to a single spectrum slice answered it instantly. The leakage panel was plotting
the head and tail of the chunk on shared axes, which looks the same whether or not there's
a discontinuity; splicing the tail onto the head and marking the seam is the plot that
shows it.

Lesson: "I made a figure about X" and "I made a figure that shows X" are different
achievements, and only looking at it carefully tells you which one you have.

## Resources

- Meinard Müller, *Fundamentals of Music Processing*, Ch. 2 — https://www.audiolabs-erlangen.de/resources/MIR/FMP/C2/C2.html
- 3Blue1Brown, "But what is the Fourier Transform?"
- Julius O. Smith, *Spectral Audio Signal Processing* — https://ccrma.stanford.edu/~jos/sasp/
- Harris, "On the Use of Windows for Harmonic Analysis with the DFT," Proc. IEEE, 1978
- Cooley and Tukey, "An Algorithm for the Machine Calculation of Complex Fourier Series," 1965

## My code

- https://github.com/candpixie/auracle/tree/main/labs/day-02-fft

## Post

**Hook:** you can't know *when* and *what* at the same time
**Artifact:** `out/uncertainty.png`, left column vs right column
