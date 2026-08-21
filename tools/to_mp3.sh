#!/usr/bin/env bash
# Convert every generated .wav in labs/*/out/ to .mp3 alongside it.
# The labs write .wav because that is lossless and what soundfile produces;
# editors and phones want .mp3. Both are gitignored, so this is local only.
set -euo pipefail
cd "$(dirname "$0")/.."
n=0
for f in labs/*/out/*.wav; do
  [ -e "$f" ] || continue
  ffmpeg -y -loglevel error -i "$f" -codec:a libmp3lame -b:a 192k "${f%.wav}.mp3"
  n=$((n + 1))
done
echo "converted $n files"
