# Auracle: 17 Days of Machine Listening

**Dates:** Sun Aug 16 2026 to Tue Sep 01 2026 (17 consecutive days)
**Author:** candpixie
**Status:** approved design, not yet started

---

## The name

**Auracle** = *aura* + *oracle*, landing on **auricle**, the outer ear. The project is about
what the ear reveals, and about a machine trying to do the same job.

## The question

> Can a machine hear what a person hears, and if so, does what you listen to say who you are?

Two halves, deliberately. The first half is the field (machine listening). The second half is the
application (the personality question that started this). The first half is the 17 days. The second
half is day 15, where it belongs: as an application of a real skill, not as the thing you flail at
for two weeks without labels.

## The thesis

Machine listening is not "machine learning with audio examples." It is a field with its own canon,
its own conference (ISMIR), its own textbook (Müller's *Fundamentals of Music Processing*), and its
own founding problem (Bregman's auditory scene analysis, 1990). Every day of this curriculum is
built on the field's own organizing logic, not on an ML syllabus.

---

## The spine

Every single day follows the same three-beat structure:

> **1. The ear does this.  2. The machine does this.  3. Here is where the machine fails.**

That third beat is non-negotiable. It is the difference between "I used librosa" and "I understand
why this is hard." It is also, not incidentally, the thing that makes each day postable: the failure
is the story.

## Ground rules

1. **Primary sources only.** Papers, the FMP notebooks, library documentation, and the two canonical
   books. No aggregator lists, no "top 10 ML videos" roundups. If a YouTube video earns a place it
   is because it is *the* explanation of that concept (3Blue1Brown on the Fourier transform,
   Karpathy on backprop), not because it was convenient.
2. **The curriculum is derived from the field, not borrowed from a syllabus.** Overlap with intro-ML
   courses is minimal by construction, because this is ordered by the auditory pipeline (pressure →
   frequency → loudness → pitch → timbre → grouping → structure → meaning), not by model complexity.
3. **Every day ships a committed artifact.** A notebook, a script, a figure, or an audio file. A day
   with no commit did not happen.
4. **Every day names its failure.** The writeup for each day must contain a section titled
   "where this breaks."
5. **No AI attribution in any commit, PR, or doc.** Sole author, sole co-author.

---

## The 17 days

### Phase 1: signal (days 1 to 4)

Getting from air pressure to a representation a human would recognize.

---

#### Day 1 (Sun Aug 16) — Air pressure becomes a number

**Ear:** The eardrum is a transducer. It converts pressure variation into mechanical motion, and the
cochlea converts that into neural firing. It is a continuous system all the way down.

**Machine:** Sampling and quantization. Nyquist-Shannon. Bit depth and dynamic range. Load a file,
look at the raw waveform, understand what the numbers physically are.

**Where it breaks:** Aliasing. Sample too slowly and a high frequency comes back as a low one, and it
is unrecoverable. Demo it deliberately: synthesize a sweep, undersample it, listen to the ghost.

**Artifact:** `labs/day-01-sampling/` — waveform plots, a deliberately aliased sweep (write out the
`.wav`), and a short note on why 44.1 kHz is 44.1 kHz.

**Resources:**
- Julius O. Smith, *Mathematics of the DFT*, CCRMA Stanford (free online: `ccrma.stanford.edu/~jos/mdft/`)
- Müller, *Fundamentals of Music Processing*, Chapter 2 (FMP notebooks: `audiolabs-erlangen.de/resources/MIR/FMP/C2/C2.html`)
- librosa `load`, `resample` documentation

**Also today, time-critical:** request the Spotify GDPR **Extended Streaming History** export
(Account → Privacy Settings). Official SLA is up to 30 days, so it may not arrive inside this sprint.
Request it anyway, it costs one minute, and nothing in this plan depends on it.

---

#### Day 2 (Mon Aug 17) — Frequency becomes pitch

**Ear:** The basilar membrane is a mechanical frequency analyzer. Position along it maps to
frequency, which is **tonotopy**, and that map is preserved all the way into auditory cortex.

**Machine:** The DFT and FFT. Windowing (Hann, Hamming) and why a rectangular window ruins your
spectrum. The STFT and the spectrogram.

**Where it breaks:** The time-frequency uncertainty principle. Narrow window means good time
resolution and bad frequency resolution, and you cannot have both. The ear cheats by using different
effective window lengths at different frequencies, and the STFT does not.

**Artifact:** `labs/day-02-fft/` — STFT implemented once by hand, then compared to librosa. Same
signal at three window sizes, side by side, showing the tradeoff visually.

**Head start:** you already have `~/fft-visualizer`. Reuse it.

**Resources:**
- 3Blue1Brown, "But what is the Fourier Transform? A visual introduction"
- Müller FMP Chapter 2, sections 2.1 to 2.5
- Julius O. Smith, *Spectral Audio Signal Processing* (`ccrma.stanford.edu/~jos/sasp/`)

---

#### Day 3 (Tue Aug 18) — Amplitude becomes loudness

**Ear:** Loudness is not amplitude. Sensitivity is frequency-dependent and level-dependent, which is
what the equal-loudness contours describe. A 60 dB tone at 100 Hz and a 60 dB tone at 3 kHz are not
equally loud.

**Machine:** Decibels, RMS energy, A-weighting, and LUFS (ITU-R BS.1770), which is the standard every
streaming platform normalizes to.

**Where it breaks:** Peak meters lie. RMS lies differently. Loudness is perceptual and every meter is
an approximation of a psychoacoustic model.

**Artifact:** `labs/day-03-loudness/` — measure the same track with peak, RMS, A-weighted, and LUFS.
Show that they disagree, and by how much. Then run it across your own top 50 tracks and see whether
your taste skews loud.

**Resources:**
- ISO 226:2003 equal-loudness contours (the figure is widely reproduced; the standard itself is paywalled)
- ITU-R BS.1770 loudness recommendation (free from the ITU)
- Fletcher and Munson (1933), the original curves

---

#### Day 4 (Wed Aug 19) — The perceptual frequency axis

**Ear:** Pitch perception is roughly logarithmic. An octave is a doubling, and it feels like a
constant step regardless of register. Critical bands (Bark scale) describe how the cochlea groups
nearby frequencies.

**Machine:** The mel scale (Stevens, Volkmann and Newman, 1937), the Bark scale (Zwicker, 1961), the
mel spectrogram, and the **constant-Q transform** (Brown, 1991).

**Where it breaks:** Mel is an engineer's compromise fit to speech data. CQT is the musician's
transform because log-spaced bins mean every octave is the same distance, but it is more expensive
and has worse time resolution at low frequencies. Neither is the cochlea.

**Artifact:** `labs/day-04-scales/` — the same piano chromatic scale rendered as linear spectrogram,
mel spectrogram, and CQT. In the CQT the semitones are evenly spaced and in the linear one they are
not. That single figure is the whole lesson, and it is a good post.

**Resources:**
- Judith C. Brown, "Calculation of a constant Q spectral transform," JASA 1991
- Müller FMP Chapter 3
- librosa `cqt`, `melspectrogram` docs

---

### Phase 2: perception (days 5 to 8)

The four things human hearing does that are genuinely hard to reproduce.

---

#### Day 5 (Thu Aug 20) — Timbre, or why a violin is not a flute

**Ear:** You identify an instrument in well under a second, from the attack transient alone, before
a single full pitch period has elapsed. Timbre is defined negatively in the literature: everything
that is not pitch, loudness, or duration.

**Machine:** Spectral centroid, spread, flux, rolloff, flatness, zero-crossing rate. Then MFCCs
(Davis and Mermelstein, 1980) and the whole cepstral idea.

**Where it breaks:** **MFCCs discard pitch on purpose.** They were designed for speech recognition,
where who is speaking and at what pitch is noise. For music that is often exactly backwards, and half
the MIR field uses them anyway out of habit. This is the best "the tool was built for a different
problem" story in the whole curriculum.

**Artifact:** `labs/day-05-timbre/` — same melody on three instruments. Show that MFCCs cluster by
instrument and ignore the notes, while chroma does the reverse. Two clustering plots, one point.

**Resources:**
- Davis and Mermelstein (1980), IEEE TASSP, the original MFCC paper
- Müller FMP Chapter 1, section on timbre
- Sethares, *Tuning, Timbre, Spectrum, Scale* (book, optional but excellent)

---

#### Day 6 (Fri Aug 21) — Pitch that isn't there

**Ear:** The **missing fundamental**. Play the 2nd, 3rd and 4th harmonics of 100 Hz with no energy at
100 Hz at all, and you hear a 100 Hz pitch. The pitch you perceive is not present in the signal. It
is inferred.

**Machine:** f0 estimation. Autocorrelation, YIN (de Cheveigné and Kawahara, 2002), pYIN (Mauch and
Dixon, 2014), and CREPE (Kim, Salamon, Li and Bello, 2018), which is a neural approach and is out of
**NYU MARL**.

**Where it breaks:** Octave errors, everywhere, in every algorithm. And polyphony, which is still not
solved. Run YIN on a solo voice and it is fine. Run it on a full mix and watch it fall apart.

**Artifact:** `labs/day-06-pitch/` — synthesize a missing-fundamental stimulus and render it to
`.wav` so people can hear the illusion themselves. This is the single most shareable artifact in the
17 days. Then compare autocorrelation vs YIN vs CREPE on monophonic and polyphonic input.

**Resources:**
- de Cheveigné and Kawahara, "YIN, a fundamental frequency estimator for speech and music," JASA 2002
- Kim, Salamon, Li, Bello, "CREPE: A Convolutional Representation for Pitch Estimation," ICASSP 2018 (arXiv:1802.06182)
- Müller FMP Chapter 8

---

#### Day 7 (Sat Aug 22) — The beat is not in the signal

**Ear:** Beat is inferred, not present. You entrain to a pulse that may have no onset at that moment,
and you can keep time through a rest. Metrical structure is a perceptual construction.

**Machine:** Onset detection functions (spectral flux, complex domain), tempograms, autocorrelation
of the onset envelope, and dynamic-programming beat tracking (Ellis, 2007).

**Where it breaks:** **Octave errors in tempo.** The machine reports 70 BPM for a 140 BPM track,
constantly. It has no idea which level of the metrical hierarchy is the one humans would tap.

**Artifact:** `labs/day-07-rhythm/` — beat-track a set of your own music, render click tracks over
the audio, and *listen* to where it fails. Include at least one track where it locks to half-time.

**Resources:**
- Bello, Daudet, Abdallah, Duxbury, Davies, Sandler, "A Tutorial on Onset Detection in Music Signals," IEEE TSAP 2005 (Bello, again NYU MARL)
- Ellis, "Beat Tracking by Dynamic Programming," Journal of New Music Research 2007
- Müller FMP Chapter 6
- `madmom` library, which is state of the art for beat tracking

---

#### Day 8 (Sun Aug 23) — The cocktail party problem

**Ear:** Bregman's **auditory scene analysis**. You separate a mixture into streams using grouping
cues: common onset, harmonicity, spatial location, continuity, and good continuation. You do it
effortlessly and it is arguably the hardest thing your auditory system does.

**Machine:** Computational auditory scene analysis (CASA). Rule-based grouping in the tradition of
Wang and Brown.

**Where it breaks:** Almost everywhere, which is why the field eventually gave up on hand-coded
grouping rules and went to learned separation. That historical pivot is tomorrow.

**This is the keystone day.** It is the field's founding problem and the clean joint where music
cognition and machine listening are the same subject.

**Artifact:** `labs/day-08-asa/` — implement two grouping cues by hand (common onset and harmonicity)
on a two-source mixture. It will work badly. Document exactly how badly. That is the point.

**Resources:**
- Bregman, *Auditory Scene Analysis: The Perceptual Organization of Sound*, MIT Press 1990 (book, the foundational text; NYU library has it)
- Wang and Brown, *Computational Auditory Scene Analysis*, Wiley/IEEE 2006

---

### Phase 3: structure (days 9 to 12)

From "what sounds are present" to "what is this piece of music."

---

#### Day 9 (Mon Aug 24) — Source separation, the learned answer

**Ear:** You hear the singer apart from the band without effort or training.

**Machine:** Harmonic-percussive source separation (median filtering, Fitzgerald 2010), non-negative
matrix factorization (Lee and Seung, 1999), then the modern learned systems: Open-Unmix and Demucs.

**Where it breaks:** Artifacts. Listen to a separated vocal stem closely and you hear the smearing,
the phase problems, the bleed. Metrics like SDR reward things the ear does not care about.

**Artifact:** `labs/day-09-separation/` — separate one of your own covers into stems with HPSS, NMF,
and Demucs. Three versions, listen to all three, write down what each one gets wrong. Rendered audio
is the deliverable.

**Resources:**
- Fitzgerald, "Harmonic/Percussive Separation using Median Filtering," DAFx 2010
- Lee and Seung, "Learning the parts of objects by non-negative matrix factorization," Nature 1999
- Défossez et al., Demucs (`github.com/facebookresearch/demucs`)
- Open-Unmix (`github.com/sigsep/open-unmix-pytorch`)
- Müller FMP Chapter 8

---

#### Day 10 (Tue Aug 25) — Tonality and key

**Ear:** Krumhansl's probe-tone experiments established the tonal hierarchy empirically: within an
established key, listeners rate some pitches as fitting better than others, and the profile is
remarkably stable across listeners.

**Machine:** Chroma features (pitch class profiles), and Krumhansl-Schmuckler key finding, which is
literally correlating your chroma vector against the empirical human ratings.

**Where it breaks:** Relative major and minor share a pitch-class set, so the algorithm confuses them
constantly. Modulation destroys the global estimate. And the whole approach assumes 12-tone equal
temperament, which is a culturally specific assumption pretending to be a universal one.

**Direct link to `~/cantojam`:** Cantonese is a tone language, so melodic contour and lexical tone
interact. Chroma and pitch contour extraction are the same tools your tone-melody work needs. This
day should feed cantojam.

**Artifact:** `labs/day-10-tonality/` — key detection over your own listening, plus a chroma-based
look at tone-melody alignment in one Cantopop track.

**Resources:**
- Krumhansl, *Cognitive Foundations of Musical Pitch*, Oxford 1990 (book)
- Müller FMP Chapter 5 (chord recognition and chroma)
- Temperley's critique of Krumhansl-Schmuckler

---

#### Day 11 (Wed Aug 26) — Repetition, structure, and expectation

**Ear:** You recognize the chorus returning instantly. Huron's argument in *Sweet Anticipation* is
that musical pleasure is largely a prediction phenomenon: expectation, violation, and resolution.

**Machine:** Self-similarity matrices (Foote, 1999), novelty curves, checkerboard kernels, and
structure segmentation into verse/chorus/bridge.

**Where it breaks:** SSMs find *acoustic* repetition, not *musical* form. A key change makes the same
chorus look like a different section. Human listeners are unbothered.

**Artifact:** `labs/day-11-structure/` — SSM plots for five tracks you know intimately, with your own
hand-labeled sections overlaid. Where does the machine's segmentation disagree with your ear?

**Resources:**
- Foote, "Visualizing music and audio using self-similarity," ACM Multimedia 1999
- Huron, *Sweet Anticipation: Music and the Psychology of Expectation*, MIT Press 2006 (book)
- Müller FMP Chapter 4

---

#### Day 12 (Thu Aug 27) — DSP in C++

**Why:** Real audio DSP lives in C++, not Python. Essentia is C++, aubio is C, JUCE is C++, and every
plugin and every real-time audio system on earth is native code. Python is the research layer sitting
on top of it.

**Do:** Implement a radix-2 FFT and a spectral-flux onset detector in C++ from scratch. Read a WAV,
write out the onset times, verify against librosa's output on the same file.

**Where it breaks:** Everything Python hid from you. Memory layout, real vs complex packing, in-place
transforms, off-by-one in the bit-reversal permutation, and the fact that a naive DFT is O(n²) and
you will feel it.

**Double-dip:** this is your CS2124 sprint (Aug 12 to Sep 1) doing double duty. Same language, same
weeks, and this is more interesting than another linked list.

**Artifact:** `labs/day-12-cpp-dsp/` — `fft.cpp`, `onset.cpp`, a Makefile, and a verification
notebook showing your C++ output matching librosa's within tolerance.

**Resources:**
- `github.com/mborgerding/kissfft` (read it, do not copy it)
- Essentia source (`github.com/MTG/essentia`) for how a production C++ MIR library is structured
- Julius O. Smith, *Mathematics of the DFT*, again, now for the implementation details

---

### Phase 4: meaning (days 13 to 17)

Where machine learning finally enters, and it enters late and on purpose.

---

#### Day 13 (Fri Aug 28) — Auto-tagging: from features to labels

**Ear:** You label a song's mood and genre in about two seconds, from a fragment.

**Machine:** Classical MIR classification. Take the features from days 4 to 11, feed them to a
classifier, predict tags. This is the first day that is recognizably "machine learning," and it works
because you spent twelve days building the features it eats.

**Where it breaks:** Genre is not a property of audio. It is a social and historical category. Any
model that predicts genre from a spectrogram is learning production conventions of an era, not
musical content. Evaluate properly with `mir_eval` and be honest about label noise.

**Artifact:** `labs/day-13-tagging/` — a tag classifier over your own feature pipeline, with a
confusion matrix and an explicit section on which confusions are actually the *labels* being wrong
rather than the model.

**Resources:**
- `mir_eval` (`craffel.github.io/mir_eval/`), the standard MIR evaluation library
- Sturm, "A Simple Method to Determine if a Music Information Retrieval System is a Horse" (essential and skeptical)
- ISMIR proceedings, open access at `archives.ismir.net`

---

#### Day 14 (Sat Aug 29) — Deep machine listening

**Ear:** Recognizes a song from a fragment of a few hundred milliseconds.

**Machine:** Spectrogram CNNs. Treat the mel spectrogram as an image, but understand why that
analogy is partly wrong (the axes are not interchangeable, translation invariance in frequency is not
the same as in time). Then pretrained audio embeddings: VGGish, PANNs (Kong et al., 2020), CLAP.
Also worth reading: Wang's 2003 Shazam paper, which solves recognition with no learning at all.

**Where it breaks:** Pretrained audio models are trained on AudioSet, which is YouTube, which is
mostly speech and environmental sound. Their music representations are weaker than people assume.

**Artifact:** `labs/day-14-deep/` — a small spectrogram CNN trained from scratch, then the same task
with PANNs embeddings plus a linear probe. Compare. The pretrained one probably wins with a fraction
of the effort, and that is a lesson about the current state of the field.

**Resources:**
- Kong et al., "PANNs: Large-Scale Pretrained Audio Neural Networks," arXiv:1912.10211
- Wang, "An Industrial-Strength Audio Search Algorithm," ISMIR 2003 (the Shazam paper)
- `torchaudio` documentation

---

#### Day 15 (Sun Aug 30) — The original question

**The question you started with:** does what you listen to say who you are?

**Now you can actually attack it,** because you have audio features you extracted yourself rather
than an API Spotify deprecated in November 2024.

**Do:** Read the actual literature and extract every reported effect size into one table:
- Rentfrow and Gosling (2003), "The Do Re Mi's of Everyday Life," JPSP (the STOMP instrument)
- Greenberg et al. (2016), "The Song Is You," SPPS (the MUSIC model)
- Nave et al. (2018), "Musical Preferences Predict Personality," *Psychological Science*
- Anderson et al. (2021), "Just the Way You Are: Linking Music Listening on Spotify and Personality," SPPS

Then implement their scoring on your own listening data and report it with *their* error bars.

**Where it breaks:** The published correlations are small. Openness lands around r ≈ 0.3 and the
other four traits sit near r ≈ 0.1 to 0.2. And you have no labels of your own, so you cannot train a
supervised model. Say all of that out loud.

**Artifact:** `labs/day-15-personality/` — the effect size table, the literature-based scorer run on
your data, and a clear statement of what would be required to do better (a labeled dataset you do not
have).

---

#### Day 16 (Mon Aug 31) — Did any of it beat chance?

**Do:** Permutation tests, cross-validation done correctly, confidence intervals, effect sizes rather
than accuracy points. Go back through days 13, 14 and 15 and test every claim against a shuffled-label
null.

**Where it breaks:** This is where a real fraction of published results would break too, and knowing
that is most of what separates someone who can run `model.fit` from someone who can be trusted with a
result.

**Artifact:** `labs/day-16-evaluation/` — a null-model comparison for every claim in the repo. Any
result that does not survive gets retracted in the README, visibly.

**This is your best content day of the 17.** "I spent two weeks building this and then tested whether
it beat random" is a video almost nobody in this space makes.

---

#### Day 17 (Tue Sep 01) — Ship

- Deploy the demo (upload audio → see its features, its key, its structure, its predicted tags).
- Finish the public writeup with the honest conclusion, including everything that failed.
- Publish the Google Doc learning log.
- Final video.
- Draft the MARL email (see below). Do not send it yet.

---

## Deliberately excluded

| Excluded | Why |
|---|---|
| RNNs and LSTMs | Sequence models need many sequences. You have one listener. Saying that shows more understanding than a half-working LSTM would. |
| Transformers and audio LLMs | Genuinely interesting, genuinely a different sprint. Nothing here needs them. |
| Music generation | A whole separate field. Scope discipline. |
| Real-time and low-latency audio | Belongs with the C++ track if you continue it, not in 17 days. |
| Speech recognition | Adjacent field, different literature, would eat four days. |
| Collecting a personality dataset via a quiz app | Requires recruiting, consent handling, and weeks of collection. Correct call is to name it as future work, not to half-build it. |

---

## Repo layout

```
auracle/
  README.md              # the question, the 17 days, the honest results table
  docs/
    plans/2026-08-16-auracle-design.md
    log/day-01.md ... day-17.md      # source of truth for the Google Doc
  labs/
    day-01-sampling/
    day-02-fft/
    ...
    day-17-ship/
  src/auracle/           # the reusable feature pipeline that accretes across days
  cpp/                   # day 12
  data/
    raw/                 # GITIGNORED. never committed.
    derived/             # aggregates only, safe to commit
  .gitignore
```

**Environment:** install `uv` (not currently on this machine), then
`uv venv && uv pip install librosa numpy scipy matplotlib pandas scikit-learn soundfile torch torchaudio jupyter`.
`madmom` and `demucs` get added on the days that need them.

---

## Privacy rules

- `data/raw/` is gitignored, permanently. The Spotify export and any raw audio never get committed.
- Only derived aggregates go in `data/derived/`: genre counts, feature matrices, summary statistics.
- Your play-by-play listening history is more revealing than it looks, and GitHub is indexed forever.
- No unreleased original lyrics, drafts, or legal name anywhere in this repo. Use commercially
  released tracks for every demo.

---

## The Google Doc

One entry per day, mirroring `docs/log/day-NN.md`:

```
Day N (Title) — <date>

The ear:      one paragraph
The machine:  one paragraph
Where it breaks: one paragraph, the part worth reading

Resources
  - primary sources, with links

My code
  - github.com/candpixie/auracle/tree/main/labs/day-NN-...
```

The "where it breaks" section is the differentiator. Every learning log on the internet has resources
and code. Almost none of them say what did not work.

---

## Content cadence

17 daily feed posts contradicts your own charter (2 per week, Pillar 2). Proposal:

- **Daily to stories.** Low effort, builds the "she is actually doing this" narrative.
- **Five feed videos**, at days 4, 6, 8, 12, 16.
  - Day 4: the CQT figure where semitones become evenly spaced. Purely visual, no explanation needed.
  - Day 6: the missing fundamental. People can hear a pitch that is not there. This is the viral one.
  - Day 8: the cocktail party problem, the hardest thing your ears do without you noticing.
  - Day 12: writing DSP in C++ during a data structures sprint.
  - Day 16: "I tested whether any of it beat random guessing."

This fits Pillar 2 (building in public, honest version) and can be scored with your own covers,
which remains the thing nobody else in this space can do.

---

## The October move

MARL, the Music and Audio Research Laboratory, is at NYU Steinhardt, directed by Juan Pablo Bello.
Brian McFee, the author of librosa, is NYU faculty. Days 6, 7 and 13 of this curriculum cite papers
by people who work on your campus, and every day of it uses a library one of them wrote.

Finishing this and emailing it to MARL in October is a materially different outcome than posting it
and moving on. Build the 17 days with that email in mind: it wants one deployed artifact, one honest
writeup, and one specific question you could not answer alone.

This also feeds `~/o1-ladder` directly. Self-directed field-specific work with a public artifact is
evidence.

---

## Risks

| Risk | Mitigation |
|---|---|
| Day 2 (FFT) eats a week. DSP math is genuinely deep. | Timebox to the day. `fft-visualizer` is a head start. Understanding beats rigor here; the rigor comes on day 12. |
| CS2124 sprint runs Aug 12 to Sep 1, the exact same window. | Day 12 is designed to serve both. Accept that some days are half-days. Half a lab still ships. |
| 17 consecutive days is a burnout pattern you have hit before. | The day is done when the commit lands, not when the lab is perfect. A three-line day with an honest "where it breaks" is a completed day. |
| The Spotify export never arrives. | Nothing depends on it. Day 15 works from top artists and tracks via the Web API, which was not deprecated. |
| Books (Bregman, Huron, Krumhansl) are expensive. | NYU library. All three are standard holdings. Request early for days 8, 10 and 11. |

---

## Success criteria

By Sep 1:

1. One public repo with 17 committed labs, each with a "where it breaks" section.
2. One deployed demo that takes audio and returns real analysis.
3. One public writeup that states plainly what failed and what did not beat chance.
4. One Google Doc learning log, built from primary sources, that is genuinely yours.
5. A drafted MARL email.

Not a success criterion: a model that predicts personality well. It will not, and the literature
already says so. Reporting that clearly *is* the result.
