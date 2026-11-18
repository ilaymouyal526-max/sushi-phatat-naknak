#!/usr/bin/env python3
"""Put the gold Yoko Ono logo (and "SUSHI PUSH POP") on the blank tube label in the v5 panels.

The generated panels show the push pop with an empty round label (gold rim). This composites the
same gold logo used in the sticker header into that circle, so the product matches the brand.

- The logo is painted only over dark tube pixels, so hands/fingers in front of the tube stay on top.
- A cylinder warp + the tube's own shading and grain make it read as printed on the tube.

Usage:
  python3 brand_tube.py --panels sticker/v5/panels --fonts <dir with ShipporiB1-800.ttf>
Writes <name>_branded.jpg next to each source image (originals untouched).
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageFilter, ImageFont

from compose_v5 import GOLD_BOT, GOLD_TOP, RED_BOT, RED_TOP, gold_text, tint

# Measured on the 2048px panels (hero: 1024px). cx, cy = label centre; r = label radius (x);
# tube = (left, right) edge of the tube at the label's height; tilt = degrees the tube's top leans
# right (clockwise); text = draw "SUSHI PUSH POP" under the circle (only where the tube is free).
CONF = {
    "panel1": dict(cx=1002, cy=1273, r=117, tube=(879, 1163), tilt=0, text=True),
    "panel2": dict(cx=903, cy=1280, r=105, tube=(771, 1031), tilt=0, text=False),
    "panel3": dict(cx=1046, cy=1280, r=135, tube=(896, 1218), tilt=0, text=True),
    "panel4": dict(cx=1057, cy=1070, r=108, tube=(935, 1205), tilt=11, text=False),
    "hero": dict(cx=373, cy=503, r=40, tube=(322, 420), tilt=0, text=False),
}
LOGO_FILL = 0.78   # logo width as a share of the label diameter
OPACITY = 0.93


def cylinder_warp(img, tube_r):
    """Horizontally compress toward the edges as if wrapped on a cylinder of radius tube_r (px)."""
    w, h = img.size
    half = w / 2
    out_half = tube_r * math.sin(min(half / tube_r, math.pi / 2 - 0.05))
    ow = max(2, int(round(out_half * 2)))
    xs = np.arange(ow) - ow / 2 + 0.5
    src = tube_r * np.arcsin(np.clip(xs / tube_r, -1, 1)) + half
    src = np.clip(np.round(src).astype(int), 0, w - 1)
    arr = np.array(img)
    return Image.fromarray(arr[:, src])


def paint(base, layer, dark_thresh=95):
    """Composite an RGBA layer onto base only where base is dark tube, with tube shading + grain."""
    b = np.array(base).astype(float)
    l = np.array(layer).astype(float)
    a = l[..., 3:4] / 255 * OPACITY
    lum = b.mean(axis=2, keepdims=True)
    # only over dark tube surface (soft edge so anti-aliasing stays clean)
    occl = np.clip((dark_thresh - lum) / 25, 0, 1)
    # tube shading: brighter/darker than the tube's typical tone modulates the gold
    tube_px = lum[(a[..., 0] > 0.3) & (occl[..., 0] > 0.9)]
    ref = np.median(tube_px) if tube_px.size else 35
    shade = np.clip((lum + 20) / (ref + 20), 0.65, 1.35) ** 0.6
    # fine grain from the tube's own texture
    blur = np.array(Image.fromarray(lum[..., 0].astype("uint8")).filter(ImageFilter.GaussianBlur(3)), float)[..., None]
    grain = (lum - blur) * 1.4
    col = np.clip(l[..., :3] * shade + grain, 0, 255)
    A = a * occl
    out = b * (1 - A) + col * A
    return Image.fromarray(out.astype("uint8"))


def recolor_rim(img, c, top, bot):
    """Turn the gold label ring into the theme colour (keeps its shading)."""
    a = np.array(img).astype(float)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - c["cx"], yy - c["cy"]) / c["r"]
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    gold = (d > 0.85) & (d < 1.18) & (R - B > 35) & (R > 80) & (R - G < 80)
    lum = a.mean(axis=2)
    k = np.clip(lum / 150, 0, 1.4)[..., None]
    col = np.array(top, float) * k
    soft = np.clip((R - B - 35) / 25, 0, 1)[..., None] * gold[..., None]
    a = a * (1 - soft) + col * soft
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def brand(img, c, logo, font_path, colors=(GOLD_TOP, GOLD_BOT)):
    if colors != (GOLD_TOP, GOLD_BOT):
        img = recolor_rim(img, c, *colors)
    W, H = img.size
    tube_r = (c["tube"][1] - c["tube"][0]) / 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # logo, scaled into the circle, wrapped on the tube
    lw = int(2 * c["r"] * LOGO_FILL)
    lh = int(logo.height * lw / logo.width)
    lg = cylinder_warp(logo.resize((lw, lh), Image.LANCZOS), tube_r)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.paste(lg, (int(c["cx"] - lg.width / 2), int(c["cy"] - lg.height / 2 + c["r"] * 0.01)), lg)
    layer = Image.alpha_composite(layer, tmp)

    if c["text"]:
        tw = (c["tube"][1] - c["tube"][0]) * 0.78
        size = 10
        f = ImageFont.truetype(font_path, size)
        while f.getlength("SUSHI PUSH POP") + 13 * size * 0.05 < tw:
            size += 1
            f = ImageFont.truetype(font_path, size)
        txt = Image.new("RGB", (W, H), (0, 0, 0))
        y = c["cy"] + c["r"] * 1.12 + size
        gold_text(txt, (c["cx"], y), "SUSHI PUSH POP", f, anchor="ms", tracking=size * 0.05, colors=colors)
        m = Image.new("L", (W, H), 0)
        md = Image.new("RGB", (W, H), (0, 0, 0))
        # mask = where text was drawn
        from PIL import ImageDraw
        dm = ImageDraw.Draw(m)
        x = c["cx"] - (sum(dm.textlength(ch, font=f) for ch in "SUSHI PUSH POP") + size * 0.05 * 13) / 2
        for ch in "SUSHI PUSH POP":
            dm.text((x, y), ch, font=f, fill=255, anchor="ls")
            x += dm.textlength(ch, font=f) + size * 0.05
        trgba = txt.convert("RGBA")
        trgba.putalpha(m)
        # wrap text too: crop its band, warp, paste back
        bb = m.getbbox()
        if bb:
            band = trgba.crop((int(c["cx"] - tube_r), bb[1], int(c["cx"] + tube_r), bb[3]))
            src_w = band.width
            warped = cylinder_warp(band, tube_r * 1.0) if src_w < 2 * tube_r * 1.5 else band
            t2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            t2.paste(warped, (int(c["cx"] - warped.width / 2), bb[1]), warped)
            layer = Image.alpha_composite(layer, t2)

    if c["tilt"]:
        # rotate the whole label layer around the circle centre to follow the tube
        layer = layer.rotate(-c["tilt"], resample=Image.BICUBIC, center=(c["cx"], c["cy"]))
    return paint(img, layer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panels", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--theme", choices=["black", "red"], default="black")
    args = ap.parse_args()
    logo = Image.open(os.path.join(args.panels, "logo_gold.png")).convert("RGBA")
    colors, sfx = (GOLD_TOP, GOLD_BOT), ""
    if args.theme == "red":
        colors, sfx = ((228, 64, 52), (186, 40, 32)), "_red"  # a touch brighter than print red so it reads on the black tube
        logo = tint(logo, *colors)
    font = os.path.join(args.fonts, "ShipporiB1-800.ttf")
    for name, c in CONF.items():
        src = os.path.join(args.panels, name + ".jpg")
        out = brand(Image.open(src).convert("RGB"), c, logo, font, colors)
        out.save(os.path.join(args.panels, name + "_branded" + sfx + ".jpg"), quality=93)
        print("wrote", name + "_branded" + sfx + ".jpg")


if __name__ == "__main__":
    main()
