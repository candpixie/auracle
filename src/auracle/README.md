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
