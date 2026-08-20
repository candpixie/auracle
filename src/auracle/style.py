"""
Shared look for every Auracle figure and video card.

matplotlib's defaults (DejaVu Sans, blue-orange-green) are instantly recognisable
as untouched defaults. One import here keeps every card in the project on the same
typeface and palette.

Usage, from anywhere in the repo:

    import sys; from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from auracle.style import apply, BG, FG, ACCENT

    apply()                 # dark cards, the default
    apply(theme="light")    # white-background figures for the README
"""

from cycler import cycler
from matplotlib import font_manager, rcParams

# --- palette -----------------------------------------------------------------
BG = "#0d0b14"          # near-black with a violet cast
FG = "#f2eef7"
DIM = "#8b82a6"
ACCENT = "#b39cff"      # violet, the project colour
GOOD = "#6ee7a8"
BAD = "#ff6b8a"
WARM = "#ffb86b"

SERIES = [ACCENT, BAD, GOOD, WARM, "#7fd4ff", DIM]

# --- type --------------------------------------------------------------------
# Didot is the high-contrast didone this project uses for display type. The
# fallbacks are the same shape family, so a machine without Didot still gets a
# serif rather than dropping to DejaVu Sans.
DISPLAY = ["Didot", "Bodoni 72", "Baskerville", "Hoefler Text", "Times New Roman"]

# Didot's thin strokes disappear at small sizes on a dark background, so numbers,
# tick labels and dense tables use a sturdier old-style serif instead.
TEXT = ["Iowan Old Style", "Charter", "Palatino", "Georgia", "Times New Roman"]

# No dingbats in any of the serifs above, and the Unicode fallbacks map U+2713 /
# U+2717 to unrelated glyphs (airplanes, in the case of Arial Unicode MS). Cards
# in this project signal pass/fail with colour and wording instead of marks.

_AVAILABLE = {f.name for f in font_manager.fontManager.ttflist}


def _first_present(candidates):
    for name in candidates:
        if name in _AVAILABLE:
            return name
    return "serif"


DISPLAY_FONT = _first_present(DISPLAY)
TEXT_FONT = _first_present(TEXT)


def apply(theme="dark"):
    """Set rcParams for the whole process. Call once, at the top of a script."""
    bg, fg, dim = (BG, FG, DIM) if theme == "dark" else ("#ffffff", "#1a1626", "#6b6480")

    rcParams.update({
        "font.family": "serif",
        "font.serif": [TEXT_FONT] + TEXT,
        "font.size": 17,

        "figure.facecolor": bg,
        "savefig.facecolor": bg,
        "axes.facecolor": bg,
        "axes.edgecolor": "#3a3350" if theme == "dark" else "#d8d3e4",
        "axes.labelcolor": fg,
        "axes.titlecolor": fg,
        "text.color": fg,
        "xtick.color": fg,
        "ytick.color": fg,
        "grid.color": "#3a3350" if theme == "dark" else "#e6e2ee",
        "grid.alpha": 0.35,

        "axes.prop_cycle": cycler(color=SERIES),

        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 100,
    })
    return {"bg": bg, "fg": fg, "dim": dim}


def display(size, weight=None):
    """
    kwargs for display type: titles, big numbers, punchlines.

    fontweight is omitted unless asked for, because matplotlib treats `weight` and
    `fontweight` as aliases and raises if a call supplies both.
    """
    kw = {"fontfamily": DISPLAY_FONT, "fontsize": size}
    if weight is not None:
        kw["fontweight"] = weight
    return kw


def text(size, weight=None):
    """kwargs for body type: labels, table cells, captions."""
    kw = {"fontfamily": TEXT_FONT, "fontsize": size}
    if weight is not None:
        kw["fontweight"] = weight
    return kw


if __name__ == "__main__":
    print(f"display font : {DISPLAY_FONT}")
    print(f"text font    : {TEXT_FONT}")
    missing = [n for n in DISPLAY + TEXT if n not in _AVAILABLE]
    if missing:
        print(f"not installed: {', '.join(missing)}")
