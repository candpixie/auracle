"""
Day 8: implement two of Bregman's grouping cues, and watch them not be enough.

Auditory scene analysis says you separate a mixture into streams using cues:
common onset, harmonicity, common fate, continuity, spatial location. Rule-based
computational ASA tries to code those up directly.

Two are implemented here, on a mixture of two harmonic voices:

  harmonicity   assign each spectral peak to whichever voice it is closest to a
                harmonic of.
  common onset  partials that start together probably belong together.

Then the honest scoring: of the energy assigned to voice A, how much really came
from voice A? The cues are given the true f0s for free, which no real system gets,
so this is a generous upper bound on how well the rule-based approach can do.

Run:  python labs/day-08-asa/grouping.py
"""

import sys
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BAD, BG, DIM, FG, GOOD, apply, display, text

apply()
OUT = Path(__file__).parent / "out"

SR = 22_050
DUR = 1.6
N_FFT = 4096

VOICES = {"A": 220.0, "B": 277.18}          # A3 and C#4, a major third apart

# the same two-voice test at three intervals. the ordering matters: these get
# MORE consonant going down, and consonance is defined by harmonic overlap.
INTERVALS = [("major third", 220.0, 277.18),
             ("perfect fifth", 220.0, 330.0),
             ("octave", 220.0, 440.0)]
N_HARM = 12
TOL_HZ = 12.0                                # how close counts as "a harmonic of"


def voice(f0, n_harm=N_HARM, sr=SR, dur=DUR, onset=0.0):
    t = np.arange(int(sr * dur)) / sr
    x = np.zeros_like(t)
    for h in range(1, n_harm + 1):
        if f0 * h >= sr / 2:
            break
        x += np.sin(2 * np.pi * f0 * h * t) / h
    if onset > 0:
        x[:int(onset * sr)] = 0.0
    n = int(sr * 0.02)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return 0.4 * x / np.abs(x).max()


def harmonic_of(freq, f0, tol=TOL_HZ):
    """Is freq within tol of any harmonic of f0?"""
    h = round(freq / f0)
    return h >= 1 and abs(freq - h * f0) <= tol


def main():
    OUT.mkdir(exist_ok=True)

    a, b = voice(VOICES["A"]), voice(VOICES["B"])
    mix = 0.5 * (a + b)
    for name, sig in (("voice_A", a), ("voice_B", b), ("mixture", mix)):
        sf.write(OUT / f"{name}.wav", sig, SR)

    freqs = np.fft.rfftfreq(len(mix), 1 / SR)
    spec_a = np.abs(np.fft.rfft(a * np.hanning(len(a))))
    spec_b = np.abs(np.fft.rfft(b * np.hanning(len(b))))
    spec_m = np.abs(np.fft.rfft(mix * np.hanning(len(mix))))

    # only look where there is meaningful energy
    live = spec_m > spec_m.max() * 1e-3

    claim_a = np.array([harmonic_of(f, VOICES["A"]) for f in freqs]) & live
    claim_b = np.array([harmonic_of(f, VOICES["B"]) for f in freqs]) & live
    both = claim_a & claim_b
    neither = live & ~claim_a & ~claim_b

    print("harmonicity cue, handed the true f0s for free.\n")
    print(f"voice A = {VOICES['A']:.1f} Hz, voice B = {VOICES['B']:.2f} Hz "
          f"(a major third)\n")
    print(f"{'bins with real energy':<32} {live.sum():>6}")
    print(f"{'claimed by A only':<32} {(claim_a & ~both).sum():>6}")
    print(f"{'claimed by B only':<32} {(claim_b & ~both).sum():>6}")
    print(f"{'claimed by BOTH':<32} {both.sum():>6}   <- ambiguous")
    print(f"{'claimed by neither':<32} {neither.sum():>6}   <- unassignable")

    # how pure is the energy the cue hands to voice A?
    def purity(mask, target, other):
        e_t = float((target[mask] ** 2).sum())
        e_o = float((other[mask] ** 2).sum())
        return e_t / (e_t + e_o + 1e-20)

    pa = purity(claim_a & ~both, spec_a, spec_b)
    pb = purity(claim_b & ~both, spec_b, spec_a)
    print()
    print(f"of the energy handed to voice A, {pa:.1%} actually came from A.")
    print(f"of the energy handed to voice B, {pb:.1%} actually came from B.")

    unclaimed = float((spec_m[neither] ** 2).sum() / (spec_m[live] ** 2).sum())
    shared = float((spec_m[both] ** 2).sum() / (spec_m[live] ** 2).sum())
    print()
    print(f"{shared:.1%} of the energy is claimed by both voices at once.")
    print(f"{unclaimed:.1%} is claimed by neither.")

    # ---- common onset ----
    print()
    print("-" * 62)
    print("common onset cue: delay voice B by 60 ms and see if it pops out.\n")
    b_late = voice(VOICES["B"], onset=0.060)
    mix_late = 0.5 * (a + b_late)
    sf.write(OUT / "mixture_staggered.wav", mix_late, SR)

    early = mix_late[:int(SR * 0.055)]
    spec_e = np.abs(np.fft.rfft(early * np.hanning(len(early))))
    f_e = np.fft.rfftfreq(len(early), 1 / SR)
    live_e = spec_e > spec_e.max() * 1e-2
    only_a = np.array([harmonic_of(f, VOICES["A"]) for f in f_e]) & live_e
    only_b = np.array([harmonic_of(f, VOICES["B"]) for f in f_e]) & live_e
    print(f"in the first 55 ms, before B enters:")
    print(f"  bins matching A's harmonics: {only_a.sum()}")
    print(f"  bins matching B's harmonics: {only_b.sum()}")
    print()
    print("that window is genuinely informative and a real system should use it.")
    print("but it only exists because I staggered the onsets by hand. two notes")
    print("struck together, which is most music, give you nothing here.")

    print()
    print("-" * 62)
    print("so the cue WORKS. now watch what happens as the interval gets nicer.")
    print("-" * 62 + "\n")
    print(f"{'interval':<16} {'bins only B owns':>18} {'shared':>9}   separable?")
    for label, fa, fb in INTERVALS:
        va, vb = voice(fa), voice(fb)
        m = 0.5 * (va + vb)
        fr = np.fft.rfftfreq(len(m), 1 / SR)
        sm = np.abs(np.fft.rfft(m * np.hanning(len(m))))
        lv = sm > sm.max() * 1e-3
        ca = np.array([harmonic_of(f, fa) for f in fr]) & lv
        cb = np.array([harmonic_of(f, fb) for f in fr]) & lv
        bo = int((cb & ~(ca & cb)).sum())
        print(f"{label:<16} {bo:>18} {int((ca & cb).sum()):>9}   "
              f"{'yes' if bo > 10 else 'barely' if bo else 'IMPOSSIBLE'}")

    print()
    print("at the octave, voice B owns ZERO bins of its own. every harmonic of 440")
    print("is also a harmonic of 220. harmonicity is not bad at octaves, it is")
    print("structurally incapable of them, and no amount of tuning changes that.")
    print()
    print("and notice the direction. a third is easy, a fifth is halfway, an octave")
    print("is impossible. those are the intervals in order of CONSONANCE, because")
    print("consonance IS harmonic overlap. music is built out of precisely the")
    print("cases that defeat this cue.")

    print()
    print("-" * 62)
    print("and the part that actually kills it")
    print("-" * 62)
    est = float(np.median(librosa.yin(mix, fmin=100, fmax=800, sr=SR)))
    print(f"every number above assumed I already knew both f0s. asking for them:")
    print()
    print(f"  YIN on the mixture      {est:>7.1f} Hz")
    print(f"  the notes actually there  {VOICES['A']:.1f} and {VOICES['B']:.1f} Hz")
    print()
    print("neither. day 6 showed why: YIN models one periodic source and returns")
    print("one number.")
    print()
    print("so: to use harmonicity you need the f0s. to get the f0s you need the")
    print("voices separated. that is a loop with no entry point, and it is why")
    print("rule-based ASA stalled. every cue here is real, and the whole system")
    print("still cannot start.")
    print()
    print("the field stopped writing the rules and started learning the separation")
    print("instead. that is tomorrow.")

    # ---- the picture ----
    fig, ax = plt.subplots(figsize=(13, 5.5))
    band = freqs < 2600
    ax.plot(freqs[band], spec_m[band] / spec_m.max(), lw=1.0, color=DIM,
            label="the mixture")
    for f0, colour, lab in ((VOICES["A"], ACCENT, "A's harmonics"),
                            (VOICES["B"], GOOD, "B's harmonics")):
        for h in range(1, N_HARM + 1):
            if f0 * h < 2600:
                ax.axvline(f0 * h, color=colour, lw=1.4, alpha=0.55,
                           label=lab if h == 1 else None)
    for f in freqs[both]:
        if f < 2600:
            ax.axvspan(f - 6, f + 6, color=BAD, alpha=0.35)
    ax.set_xlabel("Hz", **text(14), color=FG)
    ax.set_ylabel("magnitude", **text(14), color=FG)
    ax.set_yticks([])
    ax.legend(fontsize=12)
    ax.set_title("two voices a major third apart. red = a partial both voices claim.",
                 **display(17), color=FG)
    fig.tight_layout()
    fig.savefig(OUT / "grouping.png", dpi=150, facecolor=BG)
    print(f"\nwrote {OUT / 'grouping.png'}")


if __name__ == "__main__":
    main()
