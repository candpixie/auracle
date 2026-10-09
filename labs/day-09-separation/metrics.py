"""
Day 9: score a perfect separation, then break it on purpose.

Every separation paper reports SDR. The number has an obvious reading: higher
is a better separation. This lab checks that reading by handing the metric the
true stem, unaltered, and then damaging it in ways I can describe in plain
language, so the ranking the metric produces can be compared against a ranking
anyone can hear.

Two definitions of SDR are scored side by side, because the field uses both:

  SI-SDR         the estimate may be scaled. Nothing else is forgiven.
  bss_eval SDR   the estimate may be the reference through any 512-tap FIR
                 filter. Delays, EQ and phase rotations are all filters, so
                 all three are forgiven.

Every damaged version is written to out/ as a wav. Listen before reading the
table, and decide the ranking yourself first.

Run:  python labs/day-09-separation/metrics.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import lfilter

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from auracle.style import ACCENT, BAD, DIM, GOOD, WARM, apply, display, text
import synth

apply()
OUT = Path(__file__).parent / "out"


def identity(x):
    return x.copy()


def delay_one_sample(x):
    return np.concatenate([[0.0], x[:-1]])


def louder_6db(x):
    return x * 2.0


def polarity_flip(x):
    return -x


def eq_tilt(x):
    return lfilter([1.0, -0.3], [1.0], x)


def hiss_30db(x, seed=1):
    rng = np.random.default_rng(seed)
    rms = np.sqrt(np.mean(x ** 2))
    return x + rng.standard_normal(x.size) * rms * 10 ** (-30 / 20)


def dropout_100ms(x):
    y = x.copy()
    mid = y.size // 2
    n = int(synth.SR * 0.1)
    y[mid:mid + n] = 0.0
    return y


DAMAGE = [
    ("nothing, the true stem", identity, "inaudible"),
    ("delayed by 1 sample (45 us)", delay_one_sample, "inaudible"),
    ("polarity flipped", polarity_flip, "inaudible alone"),
    ("6 dB too loud", louder_6db, "obvious"),
    ("mild EQ tilt", eq_tilt, "audible"),
    ("hiss added at -30 dB", hiss_30db, "audible"),
    ("100 ms of silence punched in", dropout_100ms, "glaring"),
]


def db(x):
    """
    Anything above 100 dB means the residual is float rounding error, not a
    difference anybody could measure. Printing 224.2 invites a reader to
    compare it against 230.3 as though that gap meant something.
    """
    return "  perfect" if x > 100 else f"{x:9.1f}"


def main():
    OUT.mkdir(exist_ok=True)
    h, p, m = synth.mix(synth.harmonic(0.5), synth.percussive(0.02))

    rows = []
    for name, fn, verdict in DAMAGE:
        est = fn(h)
        rows.append((name, verdict, synth.si_sdr(est, h), synth.filtered_sdr(est, h)))
        slug = name.split(",")[0].replace(" ", "_").replace("-", "").replace("(", "").replace(")", "")
        sf.write(OUT / f"damaged_{slug}.wav", est / max(np.abs(est).max(), 1.0), synth.SR)

    print("The estimate IS the true stem, damaged one way at a time.")
    print("Both columns are SDR in dB. Higher is supposed to mean better.")
    print("Over 100 dB prints as 'perfect': the residual there is float noise.\n")
    print(f"{'what I did to it':<32} {'ear':<16} {'SI-SDR':>9} {'bss_eval':>10}")
    print("-" * 70)
    for name, verdict, si, fl in rows:
        print(f"{name:<32} {verdict:<16} {db(si):>9} {db(fl):>10}")

    print("\nMeasured EQ tilt, so 'mild' is not just a word:")
    w = np.fft.rfftfreq(2048, 1 / synth.SR)
    H = np.abs(np.fft.rfft(np.concatenate([[1.0, -0.3], np.zeros(2046)])))
    print(f"  {20 * np.log10(H[1]):.1f} dB at {w[1]:.0f} Hz, "
          f"{20 * np.log10(H[-1]):+.1f} dB at {w[-1] / 1000:.1f} kHz, "
          f"a {20 * np.log10(H[-1] / H[1]):.1f} dB swing across the band")

    print("\nAnd the one that matters, because a stem is not the deliverable.")
    print("Put each damaged harmonic stem back with the untouched percussive")
    print("stem and compare the result against the mixture it came from:\n")
    print(f"{'what I did to it':<32} {'remix SI-SDR':>13}")
    print("-" * 47)
    remix = []
    for name, fn, _ in DAMAGE:
        r = fn(h) + p
        d = synth.si_sdr(r, m)
        remix.append((name, d))
        print(f"{name:<32} {db(d):>13}")

    figure(rows, remix)
    print(f"\nwrote {OUT / 'metrics.png'}")
    print(f"listen: {OUT}/damaged_*.wav")


def figure(rows, remix):
    """
    Bars are clipped at 40 dB. The honest values up there are 220-odd, which is
    float noise pretending to be a measurement, and plotting them to scale
    squashes everything a reader is supposed to compare into one pixel.
    """
    CAP = 40.0
    names = [r[0] for r in rows]
    y = np.arange(len(names))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.8), sharey=True)

    def clipped(ax, vals, offset, height, colour, label=None):
        drawn = [min(v, CAP) if v > 0 else max(v, -CAP) for v in vals]
        ax.barh(y + offset, drawn, height, color=colour, label=label)
        for yi, v, d in zip(y + offset, vals, drawn):
            if v > CAP:
                ax.text(CAP + 0.7, yi, "perfect", va="center", color=colour, **text(13))
            elif v < -CAP:
                ax.text(-CAP - 1.5, yi, "cancels out", va="center", ha="right",
                        color=BAD, **text(13))

    ax = axes[0]
    clipped(ax, [r[2] for r in rows], 0.19, 0.36, ACCENT, "SI-SDR")
    clipped(ax, [r[3] for r in rows], -0.19, 0.36, WARM, "bss_eval SDR")
    ax.set_yticks(y)
    ax.set_yticklabels(names, **text(14))
    ax.set_xlim(0, CAP + 13)
    ax.set_xticks([0, 10, 20, 30, 40])
    ax.set_xlabel("SDR (dB), higher is better")
    ax.set_title("The estimate is the true stem, damaged", **display(20))
    ax.legend(loc="lower right")
    ax.grid(True, axis="x")

    ax = axes[1]
    clipped(ax, [r[1] for r in remix], 0.0, 0.5, GOOD)
    ax.axvline(0, color=DIM, lw=1.2)
    ax.set_xlim(-CAP - 22, CAP + 13)
    ax.set_xticks([-40, -20, 0, 20, 40])
    ax.set_xlabel("SI-SDR of the remix against the mixture (dB)")
    ax.set_title("Scored on the mix instead of the stem", **display(20))
    ax.grid(True, axis="x")

    fig.suptitle("Both metrics certify a polarity flip as a flawless separation",
                 **display(25))
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(OUT / "metrics.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
