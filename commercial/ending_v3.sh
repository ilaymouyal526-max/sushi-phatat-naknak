#!/usr/bin/env bash
# v3: v2 cut up to the logo drum hit (frame 255 = 10.625s) + the painting ending from the new AI clip
# (13.65-17.0s: logo on black -> ink-mountain painting), reframed 9:16, gold ORDER NOW kept.
# Usage: ending_v3.sh v2_9x16.mp4 painting_16x9.mp4 cta.png out.mp4   (cta.png: 1080x1920 RGBA, rule y=1420, text y=1446)
set -e
ffmpeg -v error -y -i "$1" -i "$2" -loop 1 -framerate 24 -i "$3" -filter_complex "\
[0:v]trim=end_frame=255,setpts=PTS-STARTPTS,setsar=1[a];\
[1:v]trim=start=13.65:end=17.0,setpts=PTS-STARTPTS,fps=24,split[p1][p2];\
[p1]scale=-2:1920,crop=1080:1920:0:0,gblur=sigma=14,eq=brightness=-0.04[bg];\
[p2]scale=1500:-2,crop=1080:ih,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,min(Y,H-Y)/130)'[fg];\
[bg][fg]overlay=0:458,format=yuv444p,noise=c0s=10:c0f=t:c1s=4:c1f=t:c2s=4:c2f=t,vignette=angle=PI/5,format=yuva444p[e0];\
[2:v]format=rgba,fade=in:st=1.3:d=0.4:alpha=1[cta];\
[e0][cta]overlay=0:0:shortest=1,fade=out:st=2.95:d=0.4,format=yuv420p,setsar=1[e];\
[a][e]concat=n=2:v=1:a=0[v];\
[0:a]apad=whole_dur=13.975,atrim=end=13.975,afade=out:st=13.35:d=0.62[au]" \
-map "[v]" -map "[au]" -c:v libx264 -crf 19 -tune grain -maxrate 30M -bufsize 60M -pix_fmt yuv420p \
-c:a aac -b:a 192k -movflags +faststart "$4"
