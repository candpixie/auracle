"""
Pull your own listening data from the Spotify Web API.

What still works after the November 2024 deprecation:
    /me/top/artists, /me/top/tracks, /me/tracks, and artist objects (which carry
    a `genres` array). That is everything this project needs.

What does NOT work for any app created after 2024-11-27:
    audio-features, audio-analysis, recommendations, related-artists, 30 s preview
    URLs. Those return 403 no matter what scopes you hold. This script probes for
    them and reports honestly rather than pretending.

Setup (one time):

    1. developer.spotify.com/dashboard -> Create app
    2. Redirect URI must be exactly:   http://127.0.0.1:8888/callback
       Spotify no longer accepts the hostname "localhost". Use the IP.
    3. Copy the Client ID and Client Secret, then:

        export SPOTIPY_CLIENT_ID=...
        export SPOTIPY_CLIENT_SECRET=...
        export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

Run:  python src/auracle/spotify_pull.py

Writes raw JSON to data/raw/ (gitignored) and aggregates to data/derived/.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

SCOPES = "user-top-read user-library-read"
RANGES = {"short_term": "last 4 weeks",
          "medium_term": "last 6 months",
          "long_term": "several years"}


def client():
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    missing = [v for v in ("SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET",
                           "SPOTIPY_REDIRECT_URI") if not os.environ.get(v)]
    if missing:
        sys.exit("missing env vars: " + ", ".join(missing) +
                 "\nsee the setup notes at the top of this file.")

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPES,
        cache_path=str(RAW / ".spotify-token-cache"),
        open_browser=True,
    ))


def page(fn, limit=50, cap=200, **kw):
    """Walk a paged endpoint up to cap items."""
    out, offset = [], 0
    while len(out) < cap:
        batch = fn(limit=limit, offset=offset, **kw)
        items = batch.get("items", [])
        if not items:
            break
        out.extend(items)
        offset += len(items)
        if len(items) < limit:
            break
    return out[:cap]


def probe_deprecated(sp, track_id):
    """Check whether this app still has the endpoints killed in Nov 2024."""
    import spotipy
    try:
        sp.audio_features([track_id])
        return True, "audio-features works (app predates the Nov 2024 cutoff)"
    except spotipy.SpotifyException as e:
        if e.http_status in (403, 404):
            return False, (f"audio-features returns {e.http_status}, as expected for "
                           "an app created after 2024-11-27. days 5 and 6 of this "
                           "project extract those features locally instead.")
        raise


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)

    sp = client()
    me = sp.current_user()
    print(f"signed in as {me.get('display_name') or me['id']}\n")

    data = {"artists": {}, "tracks": {}}

    for rng, label in RANGES.items():
        artists = page(sp.current_user_top_artists, cap=100, time_range=rng)
        tracks = page(sp.current_user_top_tracks, cap=100, time_range=rng)
        data["artists"][rng] = artists
        data["tracks"][rng] = tracks
        print(f"{label:>16}: {len(artists):>3} artists, {len(tracks):>3} tracks")

    saved = page(sp.current_user_saved_tracks, cap=500)
    data["saved"] = saved
    print(f"{'saved tracks':>16}: {len(saved):>3}\n")

    (RAW / "spotify_raw.json").write_text(json.dumps(data, indent=2))

    # ---- genre distribution, which is the actual feature for now ----
    genres = Counter()
    seen = set()
    for rng in RANGES:
        for a in data["artists"][rng]:
            if a["id"] in seen:
                continue
            seen.add(a["id"])
            genres.update(a.get("genres", []))

    top_artists = [
        {"name": a["name"], "genres": a.get("genres", []),
         "popularity": a.get("popularity")}
        for a in data["artists"]["medium_term"]
    ]

    (DERIVED / "genre_counts.json").write_text(
        json.dumps(dict(genres.most_common()), indent=2))
    (DERIVED / "top_artists.json").write_text(json.dumps(top_artists, indent=2))

    print(f"{len(seen)} distinct artists, {len(genres)} distinct genres\n")
    print("your top 15 genres:")
    width = max((len(g) for g, _ in genres.most_common(15)), default=10)
    for g, c in genres.most_common(15):
        print(f"  {g:<{width}}  {'#' * c}  {c}")

    if not genres:
        print("  (none. spotify's genre tags are per-ARTIST and can be sparse.)")

    # ---- the deprecation, checked rather than assumed ----
    print()
    any_track = next((t["id"] for t in data["tracks"]["medium_term"] if t.get("id")), None)
    if any_track:
        works, msg = probe_deprecated(sp, any_track)
        print(("OK   " if works else "note ") + msg)

    print(f"\nraw     -> {RAW / 'spotify_raw.json'}  (gitignored)")
    print(f"derived -> {DERIVED}")


if __name__ == "__main__":
    main()
