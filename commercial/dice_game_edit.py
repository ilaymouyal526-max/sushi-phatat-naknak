"""Assemble the Yoko Ono dice-game spot (9:16, 1080x1920, <=20s) from AI clips.

Usage: python3 commercial/dice_game_edit.py <clips_dir> <out.mp4>
clips_dir must hold: shot1.mp4 shot2.mp4 bill.mp4 chef.mp4 surprise.mp4 shot6.mp4 shot7.mp4
Run from the repo root (uses commercial/assets/terms_card_v2.png and fonts). Free: ffmpeg + Pillow only.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CLIPS, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
FONT = "commercial/assets/fonts/Heebo.ttf"
CARD = "commercial/assets/terms_card_v2.png"
GOLD, CREAM = (240, 214, 150), (255, 248, 235)

# (file, src_start, duration, caption or None)
SHOTS = [
    ("shot1.mp4",    0.0, 3.0, None),
    ("shot2.mp4",    0.0, 3.0, None),
    ("bill.mp4",     0.6, 2.0, None),
    ("chef.mp4",     0.4, 2.5, "לא לא, בואו איתי!"),
    ("surprise.mp4", 0.6, 2.0, "יש לכם סיכוי לזכות בארוחה חינם!"),
    ("shot6.mp4",    0.6, 3.0, "דאבל!"),
    ("shot7.mp4",    0.0, 2.0, "מזל טוב, תגיעו שוב!"),
]
CARD_DUR = 2.4  # terms card; total = 17.5 + 2.4 = 19.9s


def caption_png(text, path, size=78, color=CREAM):
    while True:  # shrink until it fits inside the safe width
        f = ImageFont.truetype(FONT, size); f.set_variation_by_axes([850])
        if ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f, direction="rtl", language="he") <= W - 140:
            break
        size -= 2
    im = Image.new("RGBA", (W, size * 2 + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    kw = dict(font=f, anchor="mm", direction="rtl", language="he")
    pos = (W / 2, im.height / 2)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pos[0] + 4, pos[1] + 6), text, fill=(0, 0, 0, 200), stroke_width=10, stroke_fill=(0, 0, 0, 200), **kw)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.text(pos, text, fill=color, stroke_width=6, stroke_fill=(40, 22, 8), **kw)
    im.save(path)


tmp = tempfile.mkdtemp()
inputs, filters, labels = [], [], []
for i, (f, ss, dur, cap) in enumerate(SHOTS):
    inputs += ["-ss", str(ss), "-t", str(dur), "-i", os.path.join(CLIPS, f)]
    filters.append(f"[{i}:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                   f"crop={W}:{H},setsar=1,eq=contrast=1.04:saturation=1.08,trim=duration={dur},setpts=PTS-STARTPTS[v{i}]")
n = len(SHOTS)
# terms card with slow push-in
inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(CARD_DUR), "-i", CARD]
frames = int(CARD_DUR * FPS)
filters.append(f"[{n}:v]scale={W * 2}:{H * 2},zoompan=z='1+0.04*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
               f":d=1:s={W}x{H}:fps={FPS},setsar=1,fade=in:st=0:d=0.25,trim=duration={CARD_DUR}[v{n}]")
filters.append("".join(f"[v{i}]" for i in range(n + 1)) + f"concat=n={n + 1}:v=1:a=0[base]")

# captions, timed on the concatenated timeline
t, last, k = 0.0, "base", n + 1
for i, (f, ss, dur, cap) in enumerate(SHOTS):
    if cap:
        p = os.path.join(tmp, f"cap{i}.png")
        caption_png(cap, p, size=110 if cap == "דאבל!" else 76, color=GOLD if cap == "דאבל!" else CREAM)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", "20", "-i", p]
        a, b = t + 0.15, t + dur - 0.05
        if cap == "דאבל!":
            a = t + dur - 1.0  # pop in once the dice land
        y = 1660 if cap == "דאבל!" else 1330
        filters.append(f"[{k}:v]format=rgba,fade=in:st={a:.2f}:d=0.15:alpha=1[c{k}];"
                       f"[{last}][c{k}]overlay=0:{y}:shortest=0:eof_action=pass:enable='between(t,{a:.2f},{b:.2f})'[o{k}]")
        last = f"o{k}"; k += 1
    t += dur
filters.append(f"[{last}]format=yuv420p[v]")

cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[v]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print("done", OUT, f"{t + CARD_DUR:.2f}s")
