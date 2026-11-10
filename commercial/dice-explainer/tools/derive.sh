#!/usr/bin/env bash
# Builds the deliverables from the raw render (free, local ffmpeg). Run from commercial/dice-explainer after:
#   npx -y hyperframes@0.8.226 render --quality delivery -o renders/master-raw.mp4
# It writes into renders/:
#   yoko-dice-reels-master.mp4   the Reels master: the same picture, the sound levelled to about -16 LUFS
#   yoko-dice-screen-loop.mp4    the full film, silent, for the restaurant screen (loops end -> start)
#   yoko-dice-15s.mp4            a 15 s cut for Stories: the chef, the perfect throw, -50%, the jackpot, the end card
#   *-send.mp4                   compressed copies to send in chat
set -euo pipefail
RAW=${1:-renders/master-raw.mp4}
M=renders/yoko-dice-reels-master.mp4
TARGET=-16

# 1. the master: measure the integrated loudness, then apply one fixed gain (no compression: the effects keep
#    their dynamics) and a true-peak ceiling at -1.5 dBFS.
I=$(ffmpeg -hide_banner -nostats -i "$RAW" -af ebur128 -f null - 2>&1 | awk '/Integrated loudness/{f=1} f && /I:/{print $2; exit}')
GAIN=$(python3 -c "print(round($TARGET - ($I), 2))")
echo "raw loudness $I LUFS, gain $GAIN dB"
ffmpeg -loglevel error -y -i "$RAW" -c:v copy -af "volume=${GAIN}dB,alimiter=limit=0.84:level=false" -c:a aac -b:a 256k -movflags +faststart "$M"

# 2. the silent screen loop
ffmpeg -loglevel error -y -i "$M" -an -c:v copy -movflags +faststart renders/yoko-dice-screen-loop.mp4

# 3. the 15 s Stories cut. (start, end) in seconds of the film, all on beats; each piece gets 2-frame audio fades
#    so the cuts don't click. Beats: chef 5-11, perfect throw 55-60, -50% 65-70, jackpot 73-77, end card 99-103.
SEGS=("3.125 6.875" "34.375 37.5" "40.625 43.75" "45.625 48.125" "61.875 64.375")
F=""; L=""
for i in "${!SEGS[@]}"; do
  read -r a b <<<"${SEGS[$i]}"
  o=$(python3 -c "print(round($b-$a-0.083,3))")
  F+="[0:v]trim=$a:$b,setpts=PTS-STARTPTS[v$i];[0:a]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:d=0.083,afade=t=out:st=$o:d=0.083[a$i];"
  L+="[v$i][a$i]"
done
ffmpeg -loglevel error -y -i "$M" -filter_complex "${F}${L}concat=n=${#SEGS[@]}:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -r 24 -c:a aac -b:a 192k -movflags +faststart renders/yoko-dice-15s.mp4

# 4. compressed copies for chat
for f in yoko-dice-reels-master yoko-dice-15s; do
  ffmpeg -loglevel error -y -i "renders/$f.mp4" -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "renders/$f-send.mp4"
done
ffmpeg -loglevel error -y -i renders/yoko-dice-screen-loop.mp4 -an -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart renders/yoko-dice-screen-loop-send.mp4

for f in renders/yoko-dice-*.mp4; do
  printf "%-46s %6.2f s  %5.1f MB\n" "$f" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")" "$(python3 -c "import os;print(os.path.getsize('$f')/1e6)")"
done
ffmpeg -hide_banner -nostats -i "$M" -af ebur128=peak=true -f null - 2>&1 | awk '/Integrated loudness/{f=1} f && /I:/{print "master:", $0} /Peak:/{p=$0} END{print "master:", p}'
