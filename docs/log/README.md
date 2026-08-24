# Auracle — field notes

**17 days of machine listening.** Aug 16 to Sep 1, 2026.

---

## The question

> Can a machine hear what a person hears?

I'm a musician and a computer science student, and those two things have never really
touched each other in my work. Summer classes ate my summer, so I have 17 days before
school starts, and I'm spending them on the one place those two things meet.

Not a course. One question, and whatever I have to learn to answer it.

## How to read this

Every entry is the same three beats:

**The ear does this. → The machine does this. → Here is where the machine fails.**

The third one is the point. Every learning log has resources and code. Almost none of
them say what didn't work, which means almost none of them tell you anything you
couldn't have gotten from the documentation.

Resources are at the bottom of each entry, deliberately. They're not the content.

## The scoreboard

Every claim I make in these 17 days gets tested against a shuffled-label null on day 16.
Anything that doesn't survive gets retracted here, in public, with a line through it.

| Claim | Day | Beat chance? |
|-------|-----|--------------|
| *pending day 16* | | |

## The days

| Day | Title | The failure |
|-----|-------|-------------|
| [01](day-01.md) | Air pressure becomes a number | aliasing: the machine hears a note nobody played |
| [02](day-02.md) | Frequency becomes pitch | you can't know *when* and *what* at the same time |
| [03](day-03.md) | Amplitude becomes loudness | every loudness meter is a guess about a person |
| [04](day-04.md) | The perceptual frequency axis | "mel spectrogram" names two different scales that disagree by 2x |
| [05](day-05.md) | Timbre | mean-pooled MFCCs cannot see time reversal at all |
| [06](day-06.md) | Pitch that isn't there | the octave error is a coin flip lost by 0.0001 |
| [07](day-07.md) | The beat is not in the signal | it locks to the hi-hat, half a beat off the beat |
| [08](day-08.md) | The cocktail party problem | consonance is harmonic overlap, so music defeats the cue |
| 09 | Source separation | |
| 10 | Tonality and key | it can't tell major from minor |
| 11 | Repetition and structure | it finds acoustic repetition, not musical form |
| 12 | DSP in C++ | everything Python was hiding |
| 13 | Auto-tagging | genre is a social category, not an acoustic one |
| 14 | Deep machine listening | |
| 15 | The original question | the published effect sizes are small and I have no labels |
| 16 | Did any of it beat chance? | |
| 17 | Ship | |

Failures listed before I got there are predictions. If one turns out wrong, that gets
noted too.

## The code

Everything is at **github.com/candpixie/auracle**, one folder per day, all of it runnable.

## Sources

Built from primary sources: papers, library docs, and the canonical books. The backbone
is Meinard Müller's *Fundamentals of Music Processing* (the FMP notebooks are free and
executable). Per-day citations sit at the bottom of each entry.

Resource lists that aggregate other people's aggregations are how everyone ends up
learning the same six things in the same order. I wanted the primary stuff.
