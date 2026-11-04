#!/usr/bin/env bash
# Builds the two derived deliverables from the Reels master (free, local ffmpeg):
#   renders/yoko-dice-screen-loop.mp4  the full film, silent, for the restaurant screen (loops end -> start)
#   renders/yoko-dice-15s.mp4          a 15 s cut for Stories: the chef, the perfect throw, -50%, jackpot, end card
# Run from commercial/dice-explainer after rendering renders/yoko-dice-reels-master.mp4.
set -euo pipefail
M=renders/yoko-dice-reels-master.mp4

ffmpeg -loglevel error -y -i "$M" -an -c:v copy -movflags +faststart renders/yoko-dice-screen-loop.mp4

# (start, end) in seconds of the film; each piece gets 2-frame audio fades so the cuts don't click.
SEGS=("3.125 6.875" "34.375 37.375" "40.625 43.625" "45.625 48.125" "61.875 64.625")
F=""; L=""
for i in "${!SEGS[@]}"; do
  read -r a b <<<"${SEGS[$i]}"
  d=$(python3 -c "print(round($b-$a,3))"); o=$(python3 -c "print(round($b-$a-0.083,3))")
  F+="[0:v]trim=$a:$b,setpts=PTS-STARTPTS[v$i];[0:a]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:d=0.083,afade=t=out:st=$o:d=0.083[a$i];"
  L+="[v$i][a$i]"
done
ffmpeg -loglevel error -y -i "$M" -filter_complex "${F}${L}concat=n=${#SEGS[@]}:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -r 24 -c:a aac -b:a 192k -movflags +faststart renders/yoko-dice-15s.mp4
