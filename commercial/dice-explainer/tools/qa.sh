#!/usr/bin/env bash
# QA on a render (free, local ffmpeg). Run from commercial/dice-explainer:
#   tools/qa.sh renders/draft-v6.mp4
# It writes into renders/qa/:
#   freeze.txt     every stretch where the picture does not change for 3 s or more (must be empty)
#   cards.jpg      one frame from the middle of every card
#   throw-*.jpg    every frame of each throw, to check the tumbles frame by frame
#   loudness.txt   integrated loudness and true peak
set -euo pipefail
M=${1:-renders/draft-v6.mp4}
Q=renders/qa
mkdir -p "$Q"

# 1. freezes of 3 s or more (the opening clips and the cards must all keep moving)
ffmpeg -hide_banner -nostats -i "$M" -vf "freezedetect=n=-60dB:d=3" -map 0:v -f null - 2>&1 | grep freeze_ > "$Q/freeze.txt" || true
echo "freezes of 3 s or more: $(grep -c freeze_start "$Q/freeze.txt" || true)"

# 2. the middle of every card (the same times as the stills sheets)
T=(1.6 5.0 7.5 8.9 10.6 13.75 17.5 21.25 25 28.75 33.9 38 43.6 48.1 51.9 55 59.4 65)
rm -f "$Q"/card-*.jpg
for i in "${!T[@]}"; do ffmpeg -loglevel error -y -ss "${T[$i]}" -i "$M" -frames:v 1 -vf scale=360:-1 "$Q/card-$(printf %02d "$i").jpg"; done
ffmpeg -loglevel error -y -pattern_type glob -i "$Q/card-*.jpg" -vf "tile=6x3:padding=6:color=0x0b0907" -frames:v 1 "$Q/cards.jpg"
rm -f "$Q"/card-*.jpg

# 3. every frame of each throw: name, start (s), frames
THROWS=("hook 9.375 60" "brand 11.875 36" "one-chance 23.125 36" "miss 30.625 54" "perfect 34.375 60" "doubles 40.625 42" "jackpot 45.625 42" "no-double 50.625 36" "coin 53.125 36" "end 61.875 48")
for t in "${THROWS[@]}"; do
  read -r name ss n <<<"$t"
  ffmpeg -loglevel error -y -ss "$ss" -i "$M" -frames:v 1 -vf "select='lt(n\,$n)',scale=180:-1,tile=12x$(( (n + 11) / 12 )):padding=2:color=0x0b0907" -fps_mode vfr "$Q/throw-$name.jpg"
done

# 4. loudness
ffmpeg -hide_banner -nostats -i "$M" -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary" > "$Q/loudness.txt" || true
grep -E "I:|Peak:" "$Q/loudness.txt" || true
echo "wrote $Q/"
