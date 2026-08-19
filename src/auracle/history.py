"""
Load the Spotify Extended Streaming History export.

PRIVACY: this reads a minute-by-minute record of years of private behaviour, and
every record carries an `ip_addr`. Nothing here writes to disk. Nothing derived
from it is ever committed; `data/` is gitignored wholesale. `ip_addr` is dropped
the moment a file is parsed, so it never reaches a DataFrame, a plot, or a repl
transcript.

The export has a trap: the files OVERLAP. A year can appear as `..._2025.json`
and again split across `..._2025_1.json` and `..._2025_2.json`. Concatenating
them naively double counts. This dedupes on the full play identity.

Usage:
    from auracle.history import load
    df = load()
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HISTORY_DIR = ROOT / "data" / "raw" / "spotify_history"

# never let these into memory beyond the parse
DROP = ["ip_addr"]

# what makes two rows the same play
KEY = ["ts", "ms_played", "spotify_track_uri", "master_metadata_track_name"]


def load(directory=HISTORY_DIR, verbose=True):
    files = sorted(directory.glob("Streaming_History_Audio_*.json"))
    if not files:
        raise SystemExit(
            f"no history files in {directory}\n"
            "copy Streaming_History_Audio_*.json from the Spotify export there.")

    frames, seen_total = [], 0
    for f in files:
        rows = json.loads(f.read_text())
        for r in rows:
            for k in DROP:
                r.pop(k, None)
        seen_total += len(rows)
        df = pd.DataFrame(rows)
        df["_source_file"] = f.name
        frames.append(df)
        if verbose:
            print(f"  {f.name:<40} {len(rows):>7,} rows")

    df = pd.concat(frames, ignore_index=True)
    before = len(df)
    df = df.drop_duplicates(subset=KEY, keep="first").reset_index(drop=True)

    if verbose:
        dropped = before - len(df)
        print(f"\n  {before:>7,} rows read")
        print(f"  {dropped:>7,} duplicates dropped "
              f"({dropped / before:.0%} of the export was overlapping files)")
        print(f"  {len(df):>7,} unique plays")

    df["ts"] = pd.to_datetime(df["ts"], format="ISO8601", utc=True)
    df = df.sort_values("ts").reset_index(drop=True)

    # music only: the export also carries podcasts and audiobooks
    df["is_music"] = df["spotify_track_uri"].notna()

    df["minutes"] = df["ms_played"] / 60_000
    df["artist"] = df["master_metadata_album_artist_name"]
    df["track"] = df["master_metadata_track_name"]

    return df


def summary(df):
    music = df[df["is_music"]]
    span = (music["ts"].max() - music["ts"].min()).days
    lines = [
        f"span            {music['ts'].min():%Y-%m-%d} to {music['ts'].max():%Y-%m-%d}  ({span:,} days)",
        f"plays           {len(music):,}",
        f"listening time  {music['minutes'].sum() / 60:,.0f} hours",
        f"distinct tracks {music['track'].nunique():,}",
        f"distinct artists{music['artist'].nunique():>,}",
        f"non-music rows  {(~df['is_music']).sum():,} (podcasts, audiobooks)",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print("loading:\n")
    df = load()
    print("\n" + summary(df))
