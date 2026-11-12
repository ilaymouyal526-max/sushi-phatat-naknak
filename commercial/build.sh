#!/usr/bin/env bash
# Builds the 9:16 social cut from raw clips. Usage: commercial/build.sh <clips_dir> <out.mp4>
set -e
FF=${FFMPEG:-ffmpeg}; D=$1; OUT=${2:-commercial/sushi_cut_v1.mp4}
A=$D/*WA0024_1.mp4; B=$D/*WA0024_2_1.mp4; C=$D/*WA0023.mp4
A=$(ls $A); B=$(ls $B); C=$(ls $C)
HERE=$(cd "$(dirname "$0")" && pwd)
# clip list: file start dur
SHOTS=(
"$B 8.0 1.6"    # hook: flame hits tuna
"$B 9.6 1.2"    # flame burst close
"$B 0.5 1.6"    # torch sear
"$B 19.0 2.2"   # knife dicing
"$A 1.0 2.4"    # rolling avocado roll
"$A 8.5 1.5"    # knife beside roll
"$C 0.3 2.0"    # topping close-up
"$C 6.0 1.6"    # sauced roll
"$C 12.0 2.0"   # sesame sprinkle
"$C 13.3 3.5"   # hero plate / CTA
)
IN=(); F=""; i=0
for s in "${SHOTS[@]}"; do read f ss d <<<"$s"; IN+=(-ss $ss -t $d -i $f)
 F+="[$i:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,eq=contrast=1.08:saturation=1.25,unsharp=5:5:0.6[v$i];"; i=$((i+1)); done
CAT=""; for j in $(seq 0 $((i-1))); do CAT+="[v$j]"; done
TXT=$(mktemp -d); trap 'rm -rf "$TXT"' EXIT
# Supers: Sumi type system (typography.py), animated RGBA overlays. key start end (end="-" holds to the end)
OV=("fire 0 1.6" "fresh 1.6 4.4" "handmade 4.4 10.3" "made 16.1 17.3" "cta 17.3 -")
F+="${CAT}concat=n=$i:v=1:a=0[b0];"; k=0
for o in "${OV[@]}"; do read n t0 t1 <<<"$o"
 if [ "$t1" = "-" ]; then python3 "$HERE/typography.py" --overlay $n $TXT/$n.mov --fps 30 --length 2.3
 else python3 "$HERE/typography.py" --overlay $n $TXT/$n.mov --fps 30 --dur $(python3 -c "print($t1-$t0)"); fi
 IN+=(-itsoffset $t0 -i $TXT/$n.mov)
 F+="[$((i+k)):v]format=rgba[o$k];[b$k][o$k]overlay=0:0:eof_action=pass[b$((k+1))];"; k=$((k+1)); done
F+="[b$k]fade=t=out:st=19.1:d=0.5[v]"
$FF -y -v error "${IN[@]}" -filter_complex "$F" -map "[v]" -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -movflags +faststart "$OUT"
