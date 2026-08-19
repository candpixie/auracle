# Auracle

**17 days of machine listening.** Timeline: Aug 16 to Sep 1, 2026.

> Can a machine hear what a person hears?

*Auracle* = aura + oracle, landing on **auricle**, the outer ear.

---

## The structure

Every day follows the same three beats:

> **1. The ear does this.  2. The machine does this.  3. Here is where the machine fails.**

The third beat is the main goal. Every learning log on the internet has resources and code.
However, not all of them explain why it fails from a humanistic perspective.

## The 17 days

| Day | Title | Status |
|-----|-------|--------|
| [01](labs/day-01-sampling/) | Air pressure becomes a number | done |
| [02](labs/day-02-fft/) | Frequency becomes pitch | done |
| [03](labs/day-03-loudness/) | Amplitude becomes loudness | done |
| [04](labs/day-04-scales/) | The perceptual frequency axis | done |
| 05 | Timbre, or why a violin is not a flute | |
| 06 | Pitch that isn't there | |
| 07 | The beat is not in the signal | |
| 08 | The cocktail party problem | |
| 09 | Source separation, the learned answer | |
| 10 | Tonality and key | |
| 11 | Repetition, structure, and expectation | |
| 12 | DSP in C++ | |
| 13 | Auto-tagging: from features to labels | |
| 14 | Deep machine listening | |
| 15 | The original question | |
| 16 | Did any of it beat chance? | |
| 17 | Ship | |

Full plan: [`docs/plans/2026-08-16-auracle-design.md`](docs/plans/2026-08-16-auracle-design.md)
Daily logs: [`docs/log/`](docs/log/)

## Results

Filled in on day 16, after every claim in this repo is tested against a shuffled-label null.
Anything that does not survive gets retracted here, visibly.

| Claim | Day | Beat chance? |
|-------|-----|--------------|
| *pending* | | |

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Running a lab

```bash
source .venv/bin/activate
python labs/day-01-sampling/aliasing.py
```

## Sources

Built from primary sources: papers, library documentation, and the canonical texts.
The backbone reference is Meinard Müller, *Fundamentals of Music Processing*
([FMP notebooks](https://www.audiolabs-erlangen.de/resources/MIR/FMP/C0/C0.html), free and executable).
Per-day citations live in each daily log.

## License

MIT for the code. Written notes are the author's.
