# Spotify pull

## One-time setup

1. Go to **developer.spotify.com/dashboard** and create an app. Any name.
2. Set the **Redirect URI** to exactly:

   ```
   http://127.0.0.1:8888/callback
   ```

   Spotify stopped accepting the hostname `localhost` in 2025. It must be the IP,
   and it must match character for character or you get INVALID_CLIENT.
3. Copy the Client ID and Client Secret from the app's settings, then in your shell:

   ```bash
   export SPOTIPY_CLIENT_ID=your_id_here
   export SPOTIPY_CLIENT_SECRET=your_secret_here
   export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

   Put those three lines in `~/.zshrc` if you want them to persist. **Do not commit
   them.** The secret is a credential.

## Run

```bash
cd ~/auracle && source .venv/bin/activate
python src/auracle/spotify_pull.py
```

A browser opens once for you to approve. After that the token is cached in
`data/raw/.spotify-token-cache`, which is gitignored.

## What you get

| file | contents | committed? |
|------|----------|------------|
| `data/raw/spotify_raw.json` | everything, verbatim | no, gitignored |
| `data/derived/genre_counts.json` | genre histogram | safe to commit |
| `data/derived/top_artists.json` | artist names, genres, popularity | your call |

Raw listening data is more revealing than it looks, so `data/raw/` never gets
committed. Only aggregates leave the machine.

## What works and what doesn't

Still fine: `/me/top/artists`, `/me/top/tracks`, `/me/tracks`, and artist objects
carrying a `genres` array.

Dead for any app created after **2024-11-27**: `audio-features`, `audio-analysis`,
`recommendations`, `related-artists`, and 30-second preview URLs. They return 403
regardless of scopes. The script probes for this and reports what it finds instead
of assuming.

That deprecation is the reason days 5 and 6 exist. Instead of asking Spotify for
timbre and brightness, this project extracts them from audio directly.

## Known gotcha

Spotify's genre tags are attached to **artists**, not tracks, and plenty of artists
have an empty `genres` array, especially smaller or non-Western ones. If your
histogram comes back thin, that is the data, not a bug. It is also exactly the
weakness that motivates using real audio features later.

---

# Figure style

Every figure and video card in this project imports one style module, so they
share a typeface and palette instead of each script picking its own.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from auracle.style import ACCENT, BG, FG, GOOD, BAD, DIM, apply, display, text

apply()                      # dark cards, the default
apply(theme="light")         # white background, for README figures
```

**Type.** `display()` is Didot, a high-contrast didone, for headlines and big
numbers. `text()` is Iowan Old Style, sturdier, for labels, tick marks and table
cells. The split matters: below about 30pt Didot's hairlines break up on a dark
background, and `345 Hz` starts reading as `345 IIz`.

Both fall back through a chain of similar faces, so a machine without Didot gets
another serif rather than dropping to matplotlib's DejaVu Sans.

**Marks.** Cards signal pass/fail with colour and wording, never with `✓` / `✗`.
None of the serifs carry dingbats, and the Unicode fallbacks map those codepoints
to unrelated glyphs (Arial Unicode MS renders them as airplanes).

**Palette.** Violet `#b39cff` is the project colour, on a near-black `#0d0b14`
with a violet cast. Green and red are reserved for verdicts.

## Safe area

Instagram Reels and TikTok overlay their own UI on a 1080x1920 frame, and some
surfaces crop or zoom on top of that. `style.SAFE` marks the region that always
survives:

| edge | fraction | pixels on 1080x1920 |
|------|----------|---------------------|
| left | 0.09 | 97 |
| right | 0.91 | 983 |
| top | 0.85 | 288 from the top |
| bottom | 0.21 | 1517 from the top |

Usable area: **886 x 1229 px**.

**Keep every word inside it.** Backgrounds and artwork may bleed past; text may
not. Titles are the easiest thing to get wrong, because a title at `y=0.95` looks
correct in a preview and gets covered by the username in the app.

```python
ax = safe_axes(fig, 0.0, 0.46, 1.0, 0.42)   # positions in SAFE fractions
fig.text(0.5, safe_y(0.99), "title", ...)   # y as a fraction up the safe box
draw_safe_guides(fig)                        # debug: outline the box
```
