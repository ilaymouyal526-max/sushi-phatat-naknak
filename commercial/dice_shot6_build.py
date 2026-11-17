"""Build the engineered dice-roll shot (shot 6) from micro-clips. Free: ffmpeg only.

Usage: python3 commercial/dice_shot6_build.py <clips_dir> <out.mp4>
clips_dir must hold: d6a_throw.mp4 d6b_slowmo.mp4 d6c_rail.mp4 d6d_roll_out.mp4 shot6.mp4 (old take, for the celebration tail)

Tricks:
- 6b is slowed with motion-compensated interpolation (true slow motion, not frame repeats).
- 6c is sped up for impact.
- 6d was generated as "dice roll AWAY from 6-6 on the logo"; it is reversed here, so the dice
  roll in and stop exactly on double six on the logo.
"""
import os, subprocess, sys

CLIPS, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
BASE = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,eq=contrast=1.04:saturation=1.08"

# (file, src_start, src_dur, speed, reverse, hold_end_s)
#   speed < 1 = slow motion (interpolated); out duration = src_dur / speed (+ hold)
PARTS = [
    ("d6a_throw.mp4",    0.45, 0.35, 1.0,  False, 0.0),   # blow on the fist for luck
    ("d6a_throw.mp4",    0.80, 1.40, 7.0,  False, 0.0),   # speed ramp through the wind-up (0.2s)
    ("d6a_throw.mp4",    2.20, 0.45, 1.0,  False, 0.0),   # the throw
    ("d6b_slowmo.mp4",   0.10, 0.45, 0.5,  False, 0.0),   # hero slow-mo tumble (0.9s on screen)
    ("d6c_rail.mp4",     0.00, 1.20, 1.5,  False, 0.0),   # slam into the rail, fast (0.8s)
    ("d6d_roll_out.mp4", 0.00, 2.60, 2.0,  True,  0.25),  # reversed: roll in from the top, stop on 6-6 on the logo + hold
    ("shot6.mp4",        3.20, 0.35, 1.0,  False, 0.0),   # old take tail: couple celebrating
]


def part_filter(i, f, ss, dur, speed, rev, hold):
    chain = [f"[{i}:v]trim=start={ss}:duration={dur},setpts=PTS-STARTPTS", f"fps={FPS}", BASE]
    if rev:
        chain.append("reverse")
    if speed < 1:
        # interpolate to FPS/speed, then stretch time: every new frame becomes a real 1/FPS frame
        chain.append(f"minterpolate=fps={int(FPS / speed)}:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
    chain.append(f"setpts=PTS/{speed}")
    chain.append(f"fps={FPS}")
    if hold > 0:
        chain.append(f"tpad=stop_mode=clone:stop_duration={hold}")
    return ",".join(chain) + f"[p{i}]"


inputs, filters = [], []
for i, (f, ss, dur, speed, rev, hold) in enumerate(PARTS):
    inputs += ["-i", os.path.join(CLIPS, f)]
    filters.append(part_filter(i, f, ss, dur, speed, rev, hold))
n = len(PARTS)
filters.append("".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[v]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", str(FPS), OUT], check=True)
total = sum(d / s + h for _, _, d, s, _, h in PARTS)
print("done", OUT, f"~{total:.2f}s")
