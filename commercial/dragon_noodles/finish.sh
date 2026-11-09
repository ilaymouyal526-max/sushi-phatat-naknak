#!/usr/bin/env bash
# Golden Dragon Wok: finish the generated dragon clip into the 9:16 social master.
# Grade + grain + vignette on the AI clip, then a crossfade into the real menu card (slow push-in),
# generated audio faded and loudness-normalised (~-15 LUFS). Free: local ffmpeg only.
# Usage: finish.sh <dragon_clip.mp4> <menu_card_1080.png> <out.mp4>
set -e
CLIP=$1; CARD=$2; OUT=$3
FPS=24; XF=0.8; HOLD=3.0
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
OFF=$(python3 -c "print(round($DUR - $XF, 3))")
TOTAL=$(python3 -c "print(round($DUR + $HOLD, 3))")
HAS_A=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$CLIP" | head -1)
NF=$(python3 -c "print(int(($HOLD + $XF) * $FPS) + 1)")
F="[0:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=$FPS,setsar=1,\
eq=contrast=1.06:saturation=1.12:gamma=0.98,colorbalance=rs=0.03:bs=0.04:rh=0.04:bh=-0.03,\
unsharp=5:5:0.5,noise=c0s=7:c0f=t,vignette=angle=PI/5,format=yuv420p[v0];\
[1:v]scale=2160:3840:flags=lanczos,zoompan=z='1+0.04*on/$NF':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=$NF:s=1080x1920:fps=$FPS,\
setsar=1,format=yuv420p[v1];\
[v0][v1]xfade=transition=fade:duration=$XF:offset=$OFF,format=yuv420p[v]"
if [ -n "$HAS_A" ]; then
  F+=";[0:a]apad=whole_dur=$TOTAL,atrim=end=$TOTAL,afade=t=out:st=$(python3 -c "print(round($DUR - 0.6, 3))"):d=$(python3 -c "print(round($HOLD + 0.6, 3))"),loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]"
  MAP=(-map "[v]" -map "[a]" -c:a aac -b:a 192k)
else
  MAP=(-map "[v]")
fi
ffmpeg -v error -y -i "$CLIP" -loop 1 -framerate $FPS -t $(python3 -c "print($HOLD + $XF)") -i "$CARD" \
  -filter_complex "$F" "${MAP[@]}" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -t $TOTAL -movflags +faststart "$OUT"
echo "wrote $OUT"
