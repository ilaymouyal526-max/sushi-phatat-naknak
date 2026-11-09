"""Prep reference/start/end-card images for the Golden Dragon Wok spot.

Usage: python3 prep.py <noodle_frame_540x960> <yoko_dragon_photo> <out_dir>
Outputs: dragon_ref.png, noodles_ref.png, start_frame.png (1080x1920), menu_card_1080.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

NOODLE, DRAGON, OUT = sys.argv[1:4]
W, H = 1080, 1920

# --- dragon disc from the bar-sign photo (sign is slightly elliptical from the low camera angle)
DISC = (398, 578, 1112, 1212)  # left, top, right, bottom of the sign's metal rim
src = Image.open(DRAGON).convert("RGB")
d = src.crop(DISC)
side = max(d.size)
d = d.resize((side, side), Image.LANCZOS)  # un-squash the ellipse
a = np.asarray(d).astype(np.float32)
# neutralise the red bar lighting: grey-world balance on the disc interior, then gentle contrast
m = a[side // 6: -side // 6, side // 6: -side // 6].reshape(-1, 3).mean(0)
a = np.clip(a * (m.mean() / m) ** 0.45, 0, 255)  # partial: keep the sign's violet/orange
d = ImageOps.autocontrast(Image.fromarray(a.astype(np.uint8)), cutoff=0.5)
inset = int(side * 0.025)  # drop the metal rim
mask = Image.new("L", (side, side), 0)
ImageDraw.Draw(mask).ellipse((inset, inset, side - inset, side - inset), fill=255)
dragon = Image.new("RGBA", (side, side), (0, 0, 0, 0))
dragon.paste(d, (0, 0), mask.filter(ImageFilter.GaussianBlur(2)))
dragon.resize((1024, 1024), Image.LANCZOS).save(f"{OUT}/dragon_ref.png")

# --- noodle photo window from the menu card
card = Image.open(NOODLE).convert("RGB")
WINDOW = (41, 125, 499, 557)  # inside the thin gold frame
noodles = card.crop(WINDOW).resize(((WINDOW[2] - WINDOW[0]) * 2, (WINDOW[3] - WINDOW[1]) * 2), Image.LANCZOS)
noodles = noodles.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
noodles.save(f"{OUT}/noodles_ref.png")

# --- 9:16 start frame: photo centred on near-black, edges feathered into the background
bg_col = tuple(int(v) for v in np.asarray(noodles)[:12, :, :].reshape(-1, 3).mean(0))  # dark top rows
start = Image.new("RGB", (W, H), bg_col)
PW = int(W * 1.3)  # bowl fills more of the 9:16 frame; sides fall off into black
ph = noodles.resize((PW, int(noodles.height * PW / noodles.width)), Image.LANCZOS)
fm = Image.new("L", ph.size, 0)
f = 70
ImageDraw.Draw(fm).rectangle((f, f, ph.width - f, ph.height - f), fill=255)
fm = fm.filter(ImageFilter.GaussianBlur(f * 0.6))
y = (H - ph.height) // 2 + 60
start.paste(ph, ((W - PW) // 2, y), fm)
# soft vignette
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - (y + ph.height / 2)) / (H * 0.6)) ** 2)
v = np.clip(1.15 - r, 0.35, 1.0)[..., None]
Image.fromarray((np.asarray(start) * v).astype(np.uint8)).save(f"{OUT}/start_frame.png")

# --- end card: whole menu card upscaled to 1080x1920
card.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=2)).save(f"{OUT}/menu_card_1080.png")
print("ok")
