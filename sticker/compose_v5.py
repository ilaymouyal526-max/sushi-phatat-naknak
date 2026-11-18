#!/usr/bin/env python3
"""Sushi Push Pop sticker v5: seinen-manga ink style ("Ink Ronin").

Composes the four generated step panels into:
  - a 3:4 how-to sticker (master 2400x3200)
  - a wrap-around tube label (master 3600x2160, same zones as wrap_v1)
and exports print files at 300 DPI with bleed and a CutContour line.

All text is set with real fonts here; the image model draws no text.

Usage:
  python3 compose_v5.py --assets DIR --fonts DIR --out DIR
      [--sticker-mm 90x120] [--wrap-mm 0x0] [--bleed-mm 2]

DIR layout expected in --assets:
  panel1.png .. panel4.png   step panels (square, cream washi background)
  hero.png                   character hero image (square) for the wrap front
  logo_gold.png              logo with alpha (gold)
Fonts in --fonts: ShipporiB1-500.ttf, ShipporiB1-800.ttf
"""
import argparse
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

INK = (26, 23, 21)
PAPER = (241, 233, 218)
VERMILION = (176, 36, 28)
GOLD_TOP = (228, 199, 132)
GOLD_BOT = (172, 131, 60)
CREAM = (244, 236, 220)

STEPS = ["Remove the soy sauce", "Open the lid", "Add soy sauce", "Push up & enjoy"]

rng = random.Random(7)
nrng = np.random.default_rng(7)


# ---------- textures ----------
def washi(w, h):
    """Cream washi paper: soft blotches + fine grain + a few long fibers."""
    base = np.ones((h, w, 3)) * np.array(PAPER, float)
    small = nrng.normal(0, 1, (h // 40 + 2, w // 40 + 2))
    blotch = np.array(Image.fromarray(((small - small.min()) / np.ptp(small) * 255).astype("uint8"))
                      .resize((w, h), Image.BICUBIC), float) / 255 - 0.5
    grain = nrng.normal(0, 1, (h, w))
    lum = blotch * 10 + grain * 3.2
    img = np.clip(base + lum[..., None], 0, 255).astype("uint8")
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(int(w * h / 9000)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        L, a = rng.uniform(20, 90), rng.uniform(0, math.pi)
        pts = [(x + math.cos(a) * t + rng.uniform(-3, 3), y + math.sin(a) * t + rng.uniform(-3, 3))
               for t in np.linspace(0, L, 6)]
        d.line(pts, fill=(205, 192, 168, rng.randint(30, 70)), width=1)
    return im


def rough_mask(w, h, edge=28, seed=0, dry=True, amp=0.9):
    """Rectangle mask with brushed, torn edges (for ink slabs)."""
    r = np.random.default_rng(seed)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([edge, edge, w - edge, h - edge], fill=255)
    noise = r.normal(0, 1, (h // 6 + 2, w // 6 + 2))
    noise = np.array(Image.fromarray(((noise - noise.min()) / np.ptp(noise) * 255).astype("uint8"))
                     .resize((w, h), Image.BICUBIC), float)
    blur = np.array(m.filter(ImageFilter.GaussianBlur(edge * 0.8)), float)
    out = ((blur + (noise - 128) * amp) > 128).astype(float) * 255
    if dry:  # horizontal dry-brush streaks
        streak = r.normal(0, 1, (h, 1)) * np.ones((1, w))
        streak = np.array(Image.fromarray(((streak - streak.min()) / np.ptp(streak) * 255).astype("uint8"))
                          .filter(ImageFilter.GaussianBlur(1)), float)
        out = np.where((streak > 225) & (r.random((h, w)) > 0.35), out * 0.15, out)
    return Image.fromarray(out.astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))


def brush_line(draw, p0, p1, width, color=INK):
    """One brush stroke: tapered, slightly wobbly, with dry gaps."""
    n = max(12, int(math.dist(p0, p1) / 14))
    pts = []
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        nx, ny = -(p1[1] - p0[1]), p1[0] - p0[0]
        L = math.hypot(nx, ny) or 1
        off = math.sin(t * math.pi * rng.uniform(1, 3)) * rng.uniform(0.5, 2.5)
        pts.append((x + nx / L * off, y + ny / L * off))
    for i in range(n):
        t = i / n
        taper = min(1, t * 6, (1 - t) * 6) * 0.6 + 0.4
        wv = max(2, int(width * taper * rng.uniform(0.75, 1.15)))
        if rng.random() < 0.06:  # dry gap
            continue
        c = color + (rng.randint(225, 255),)
        draw.line([pts[i], pts[i + 1]], fill=c, width=wv)
        r = wv / 2
        draw.ellipse([pts[i + 1][0] - r, pts[i + 1][1] - r, pts[i + 1][0] + r, pts[i + 1][1] + r], fill=c)


def ink_frame(img, box, width=16):
    """Hand-brushed manga panel border, two passes for an uneven edge."""
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    for k in range(2):
        j = lambda: rng.uniform(-5, 5)
        w = width if k == 0 else int(width * 0.45)
        corners = [(x0 + j(), y0 + j()), (x1 + j(), y0 + j()), (x1 + j(), y1 + j()), (x0 + j(), y1 + j())]
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            # overshoot past corners like a real brush
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            ov = rng.uniform(6, 22)
            a2 = (a[0] - dx / L * ov, a[1] - dy / L * ov)
            b2 = (b[0] + dx / L * ov * 0.5, b[1] + dy / L * ov * 0.5)
            brush_line(d, a2, b2, w)


def gold_text(img, xy, text, font, anchor="la", tracking=0):
    """Gold-gradient text with an optional letter spacing."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    if tracking:
        x, y = xy
        total = sum(md.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)
        if anchor[0] == "m":
            x -= total / 2
        for c in text:
            md.text((x, y), c, font=font, fill=255, anchor="l" + anchor[1])
            x += md.textlength(c, font=font) + tracking
    else:
        md.text(xy, text, font=font, fill=255, anchor=anchor)
    bb = mask.getbbox()
    if not bb:
        return
    grad = Image.new("RGB", (w, h))
    gy = np.linspace(0, 1, bb[3] - bb[1])[:, None]
    g = (np.array(GOLD_TOP) * (1 - gy) + np.array(GOLD_BOT) * gy)
    strip = np.repeat(g[:, None, :], bb[2] - bb[0], axis=1).astype("uint8")
    grad.paste(Image.fromarray(strip), (bb[0], bb[1]))
    img.paste(grad, (0, 0), mask)


def tracked_text(draw, xy, text, font, fill, tracking=0, anchor="ms"):
    x, y = xy
    total = sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)
    if anchor[0] == "m":
        x -= total / 2
    for c in text:
        draw.text((x, y), c, font=font, fill=fill, anchor="l" + anchor[1])
        x += draw.textlength(c, font=font) + tracking


def hanko(n, size, font_path):
    """Red seal square with eroded edges and a number in cream."""
    pad = 12
    s = size + pad * 2
    m = rough_mask(s, s, edge=pad + 2, seed=100 + n, dry=False, amp=0.35)
    seal = Image.new("RGBA", (s, s), VERMILION + (0,))
    # mottled ink coverage like a real stamp
    cover = nrng.random((s, s))
    cover = np.array(Image.fromarray((cover * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2)), float)
    alpha = np.array(m, float) * np.clip(0.8 + (cover - 128) / 120, 0.86, 1.0)
    seal.putalpha(Image.fromarray(alpha.astype("uint8")))
    d = ImageDraw.Draw(seal)
    f = ImageFont.truetype(font_path, int(size * 0.72))
    d.text((s / 2, s / 2 + size * 0.03), str(n), font=f, fill=CREAM + (255,), anchor="mm")
    return seal.rotate(rng.uniform(-4, 4), resample=Image.BICUBIC, expand=True)


def splatter(img, box, count=40, scale=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    for _ in range(count):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = abs(rng.gauss(0, 5 * scale)) + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=INK + (rng.randint(150, 240),))


def place_logo(img, logo, cx, top, height):
    lw = int(logo.width * height / logo.height)
    lg = logo.resize((lw, height), Image.LANCZOS)
    img.paste(lg, (int(cx - lw / 2), int(top)), lg)
    return lw


# ---------- layouts ----------
def build_sticker(a, f):
    W, H = 2400, 3200
    img = washi(W, H).convert("RGB")

    # header: sumi ink slab with gold logo + title
    slab_h = 660
    slab = rough_mask(W + 80, slab_h, edge=36, seed=1)
    img.paste(Image.new("RGB", slab.size, INK), (-40, -40), slab)
    splatter(img, (40, slab_h - 70, W - 40, slab_h + 30), count=55, scale=1.3)

    logo_h = 520
    lw = place_logo(img, a["logo"], 120 + 225, 40, logo_h)
    tx = 120 + 450 + 80
    title_cx = tx + (W - 110 - tx) / 2
    gold_text(img, (title_cx, 250), "HOW TO ENJOY YOUR", f["f500_64"], anchor="ms", tracking=14)
    gold_text(img, (title_cx, 430), "SUSHI PUSH POP", f["f800_150"], anchor="ms", tracking=6)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(title_cx - 330, 300), (title_cx + 330, 300)], fill=GOLD_BOT + (200,), width=3)

    # 2x2 panels
    M, G, P, CAP = 115, 70, 1050, 140
    tops = [740, 740 + P + CAP]
    for i in range(4):
        col, row = i % 2, i // 2
        x0 = M + col * (P + G)
        y0 = tops[row]
        panel = a["panels"][i].resize((P, P), Image.LANCZOS)
        img.paste(panel, (x0, y0))
        ink_frame(img, (x0, y0, x0 + P, y0 + P), width=18)
        seal = hanko(i + 1, 150, f["p800"])
        img.paste(seal, (x0 + 26, y0 + 26), seal)
        d = ImageDraw.Draw(img)
        tracked_text(d, (x0 + P / 2, y0 + P + 95), STEPS[i], f["f500_66"], INK, tracking=3)
    return img


def build_wrap(a, f):
    """Same zones as wrap_v1 (1200x720) at 3x: seam | front | soy-clip side | back | seam."""
    W, H = 3600, 2160
    img = washi(W, H).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    FRONT = (144, 1440)
    SIDE = (1440, 1764)
    BACK = (1764, 3456)

    # thin gold rules top and bottom (as wrap_v1)
    for y in (54, H - 54):
        d.line([(0, y), (W, y)], fill=GOLD_BOT + (230,), width=5)

    # FRONT: ink slab with logo + title, ronin hero below
    fw = FRONT[1] - FRONT[0]
    slab_h = 980
    slab = rough_mask(fw + 60, slab_h, edge=34, seed=3)
    img.paste(Image.new("RGB", slab.size, INK), (FRONT[0] - 30, 70), slab)
    place_logo(img, a["logo"], FRONT[0] + fw / 2, 130, 600)
    gold_text(img, (FRONT[0] + fw / 2, 900), "SUSHI PUSH POP", f["f800_100"], anchor="ms", tracking=4)
    hero = a["hero"]
    hs = fw
    hero = hero.resize((hs, hs), Image.LANCZOS)
    top = 1000
    crop_h = H - 70 - top
    hero = hero.crop((0, (hs - crop_h) // 3, hs, (hs - crop_h) // 3 + crop_h))
    # feather hero top into the paper
    fm = Image.new("L", hero.size, 255)
    grad = np.clip(np.linspace(0, 1.6, 140), 0, 1)
    fa = np.array(fm, float)
    fa[:140, :] *= grad[:, None]
    hero_mask = Image.fromarray(fa.astype("uint8"))
    img.paste(hero, (FRONT[0], top), hero_mask)
    splatter(img, (FRONT[0], 960, FRONT[1], 1100), count=40, scale=1.2)
    # PUSH hint + brand seal
    d = ImageDraw.Draw(img, "RGBA")
    # PUSH hint on a small torn washi patch at the bottom of the front, near the base
    patch = rough_mask(400, 150, edge=14, seed=77, dry=False)
    img.paste(washi(400, 150).convert("RGB"), (FRONT[0] + 60, H - 250), patch)
    d = ImageDraw.Draw(img, "RGBA")
    px, py = FRONT[0] + 110, H - 150
    d.text((px, py), "PUSH", font=f["f800_60"], fill=INK, anchor="ls")
    ax = px + d.textlength("PUSH", font=f["f800_60"]) + 30
    d.line([(ax, py), (ax, py - 70)], fill=INK, width=8)
    d.polygon([(ax - 18, py - 58), (ax + 18, py - 58), (ax, py - 88)], fill=INK)
    sm = rough_mask(150, 150, edge=10, seed=55, dry=False, amp=0.35)
    s_img = Image.new("RGBA", (150, 150), VERMILION + (255,))
    s_img.putalpha(sm)
    ImageDraw.Draw(s_img).text((75, 78), "YO", font=f["f800_60"], fill=CREAM, anchor="mm")
    img.paste(s_img, (FRONT[1] - 230, H - 250), s_img)

    # SIDE (soy clip zone): vertical katakana of the brand name, thin ink rule
    sx = (SIDE[0] + SIDE[1]) / 2
    d = ImageDraw.Draw(img, "RGBA")
    y = 380
    for ch in "ヨーコ・オノ":
        if ch == "ー":  # vertical long-vowel mark
            d.line([(sx, y - 60), (sx, y + 10)], fill=INK, width=9)
        else:
            d.text((sx, y), ch, font=f["p500_110"], fill=INK, anchor="ms")
        y += 150
    brush_line(d, (sx, 1300), (sx, 1820), 10)

    # BACK: title + 2x2 panels
    bw = BACK[1] - BACK[0]
    bcx = BACK[0] + bw / 2
    tracked_text(d, (bcx, 180), "HOW TO ENJOY YOUR", f["f500_60"], INK, tracking=12)
    tracked_text(d, (bcx, 310), "SUSHI PUSH POP", f["f800_120"], INK, tracking=5)
    M, G, P = 70, 60, 720
    tops = [380, 380 + P + 105]
    for i in range(4):
        col, row = i % 2, i // 2
        x0 = int(BACK[0] + M + col * (P + G) + (bw - 2 * M - 2 * P - G) / 2)
        y0 = tops[row]
        img.paste(a["panels"][i].resize((P, P), Image.LANCZOS), (x0, y0))
        ink_frame(img, (x0, y0, x0 + P, y0 + P), width=14)
        seal = hanko(i + 1, 110, f["p800"])
        img.paste(seal, (x0 + 18, y0 + 18), seal)
        dd = ImageDraw.Draw(img)
        tracked_text(dd, (x0 + P / 2, y0 + P + 70), STEPS[i], f["f500_54"], INK, tracking=2)
    return img


def build_wrap_guides(wrap):
    g = wrap.copy()
    d = ImageDraw.Draw(g)
    for x, label in [(144, "seam/overlap"), (1440, "front | side"), (1764, "side | back"), (3456, "seam")]:
        for y in range(0, g.height, 40):
            d.line([(x, y), (x, y + 20)], fill=(30, 160, 220), width=4)
        d.text((x + 12, g.height - 90), label, fill=(30, 160, 220), font=ImageFont.load_default(40))
    d.text((1452, 900), "soy\nclip\nzone", fill=(30, 160, 220), font=ImageFont.load_default(44))
    return g


# ---------- print export ----------
def export_print(img, trim_mm, bleed_mm, radius_mm, out_base):
    """Scale to trim size at 300 DPI, add mirrored bleed, write PNG + PDF + SVG with a CutContour path."""
    from reportlab.lib.colors import CMYKColorSep
    from reportlab.pdfgen import canvas

    dpi = 300
    mm2px = dpi / 25.4
    tw, th = round(trim_mm[0] * mm2px), round(trim_mm[1] * mm2px)
    b = round(bleed_mm * mm2px)
    art = img.resize((tw, th), Image.LANCZOS)
    arr = np.array(art)
    arr = np.pad(arr, ((b, b), (b, b), (0, 0)), mode="reflect")
    full = Image.fromarray(arr)
    full.save(out_base + "_print.png", dpi=(dpi, dpi))

    W_mm, H_mm = trim_mm[0] + 2 * bleed_mm, trim_mm[1] + 2 * bleed_mm
    # SVG: artwork reference + CutContour path at the trim line
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W_mm}mm" height="{H_mm}mm" viewBox="0 0 {W_mm} {H_mm}">
  <image id="artwork" x="0" y="0" width="{W_mm}" height="{H_mm}" xlink:href="{os.path.basename(out_base)}_print.png"/>
  <g id="CutContour"><rect x="{bleed_mm}" y="{bleed_mm}" width="{trim_mm[0]}" height="{trim_mm[1]}" rx="{radius_mm}" ry="{radius_mm}" fill="none" stroke="#FF00FF" stroke-width="0.25"/></g>
</svg>'''
    open(out_base + "_cut.svg", "w").write(svg)

    # PDF: artwork + CutContour as a spot-colour stroke (what most print shops read)
    pt = 72 / 25.4
    c = canvas.Canvas(out_base + "_print.pdf", pagesize=(W_mm * pt, H_mm * pt))
    c.drawImage(out_base + "_print.png", 0, 0, W_mm * pt, H_mm * pt)
    cut = CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1)
    c.setStrokeColor(cut)
    c.setLineWidth(0.25 * pt)
    c.roundRect(bleed_mm * pt, bleed_mm * pt, trim_mm[0] * pt, trim_mm[1] * pt, radius_mm * pt, stroke=1, fill=0)
    c.showPage()
    c.save()
    return full.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sticker-mm", default="90x120")
    ap.add_argument("--wrap-mm", default="", help="WxH of the wrap in mm; skip wrap print export if empty")
    ap.add_argument("--bleed-mm", type=float, default=2)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    A = args.assets

    def find(name):
        for ext in (".png", ".jpg", ".webp"):
            if os.path.exists(os.path.join(A, name + ext)):
                return os.path.join(A, name + ext)
        raise FileNotFoundError(name)

    assets = {
        "panels": [Image.open(find(f"panel{i}")).convert("RGB") for i in range(1, 5)],
        "hero": Image.open(find("hero")).convert("RGB"),
        "logo": Image.open(os.path.join(A, "logo_gold.png")).convert("RGBA"),
    }
    p5 = os.path.join(args.fonts, "ShipporiB1-500.ttf")
    p8 = os.path.join(args.fonts, "ShipporiB1-800.ttf")
    F = lambda p, s: ImageFont.truetype(p, s)
    fonts = {
        "p800": p8,
        "f500_64": F(p5, 64), "f500_66": F(p5, 66), "f500_60": F(p5, 60), "f500_54": F(p5, 54),
        "f800_150": F(p8, 150), "f800_100": F(p8, 100), "f800_128": F(p8, 128), "f800_120": F(p8, 120), "f800_60": F(p8, 60),
        "p500_110": F(p5, 110),
    }

    sticker = build_sticker(assets, fonts)
    sticker.save(os.path.join(args.out, "sticker_v5_master.png"))
    sticker.resize((900, 1200), Image.LANCZOS).save(os.path.join(args.out, "sticker_v5_preview.jpg"), quality=90)
    sw, sh = (float(v) for v in args.sticker_mm.split("x"))
    export_print(sticker, (sw, sh), args.bleed_mm, 3, os.path.join(args.out, "sticker_v5"))

    wrap = build_wrap(assets, fonts)
    wrap.save(os.path.join(args.out, "wrap_v5_flat.png"))
    wrap.resize((1200, 720), Image.LANCZOS).save(os.path.join(args.out, "wrap_v5_preview.jpg"), quality=90)
    build_wrap_guides(wrap).resize((1200, 720), Image.LANCZOS).save(os.path.join(args.out, "wrap_v5_guides.jpg"), quality=90)
    if args.wrap_mm:
        ww, wh = (float(v) for v in args.wrap_mm.split("x"))
        export_print(wrap, (ww, wh), args.bleed_mm, 0, os.path.join(args.out, "wrap_v5"))


if __name__ == "__main__":
    main()
