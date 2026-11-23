#!/usr/bin/env python3
"""Put the REAL Yoko Ono logo on the round label of every push pop (free, local).

The AI-drawn logos were inconsistent and garbled. For each panel this script:
  1. finds the AI label (gold pixels inside a search box) and the tube edges on that row,
  2. paints over it with the tube's own colour and column shading,
  3. draws one uniform thin gold ring and the original logo file inside it,
  4. keeps anything in front of the tube (fingers) on top.
Writes assets/panels/<ID>_label.png and copies it to <ID>.png for the layout.

  python3 scripts/brand_labels.py [--debug]
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
P = os.path.join(ROOT, "assets", "panels")
LOGO = os.path.join(ROOT, "assets", "yoko-ono-logo-gold.png")
RING = (212, 156, 91)   # design-system gold-deep #D49C5B

# Geometry measured by eye on gridded crops (pixels of the source panel):
#   tube = (left, right) edge of the tube on the label row
#   ai   = (cx, cy, rx, ry) ellipse covering the AI-drawn label/logo (repainted)
#   label centre = ai centre; label diameter = 0.82 x tube width (same proportion in every panel)
PANELS = {
    "A5": ("A5_v2_final.png", (588, 684), (636, 336, 50, 62)),
    "A6": ("A6_v3.png",       (338, 409), (376, 701, 34, 40)),
    "B1": ("B1_clean.png",    (337, 449), (392, 768, 56, 66)),
    "B2": ("B2_clean.png",    (348, 462), (405, 753, 37, 63)),
    "B3": ("B3_clean.png",    (340, 479), (411, 816, 70, 74)),
    "B4": ("B4_v3.png",       (425, 528), (475, 727, 52, 57)),
}
LABEL_RATIO = 0.82
FINGERS_OVER_LABEL = {"B3", "B4"}   # only here something sits in front of the label


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def brand(pid, src, tube, ai, debug=False):
    img = Image.open(os.path.join(P, src)).convert("RGB")
    a = np.array(img).astype(float)
    H, W, _ = a.shape
    left, right = tube
    acx, acy, arx, ary = ai
    cx, cy = acx, acy
    D = LABEL_RATIO * (right - left)
    rad = D / 2
    yy, xx = np.mgrid[0:H, 0:W]
    cover = (((xx - acx) / (arx + 3)) ** 2 + ((yy - acy) / (ary + 3)) ** 2 <= 1)
    cover |= ((xx - cx) ** 2 + (yy - cy) ** 2) <= (rad + 3) ** 2
    cover &= (xx > left + 2) & (xx < right - 2)
    cy_cov, ry_cov = acy, max(ary, rad) + 3
    L = lum(a)
    tube_w = right - left

    # protect things in front of the tube (skin = light pixels), dilated a little
    skin = (L > 140) & (a[..., 2] > 0.72 * a[..., 0])   # cream skin/paper, not gold (gold has low blue)
    protect = ndimage.binary_dilation(skin, iterations=3) if pid in FINGERS_OVER_LABEL else np.zeros_like(skin)
    protect &= (yy > cy + 0.15 * rad) & (xx > cx)   # fingers only reach the lower right of the label
    repaint = cover & ~protect

    # tube colour per column, from bands just above and below the covered area
    top = int(max(0, cy_cov - ry_cov - 18)); bot = int(min(H, cy_cov + ry_cov + 18))
    ref_rows = list(range(max(0, top - 14), top)) + list(range(bot, min(H, bot + 14)))
    out = a.copy()
    for x in range(left + 2, right - 1):
        col = a[ref_rows, x]
        col = col[(lum(col) < 90) & (col[:, 0] < col[:, 1] * 1.35 + 8)]   # dark tube, not the red cushion
        c = np.median(col, axis=0) if len(col) > 3 else np.array([24, 22, 20], float)
        rows = repaint[:, x]
        out[rows, x] = c
    noise = np.random.default_rng(1).normal(0, 2.2, (H, W, 1))
    out = np.where(repaint[..., None], np.clip(out + noise, 0, 255), out)

    # gold ring + logo, on a transparent layer, shaded like the tube columns
    S = 4  # supersample
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rw = max(1.0, D * 0.025) * S
    d.ellipse(((cx - rad) * S, (cy - rad) * S, (cx + rad) * S, (cy + rad) * S), outline=RING + (255,), width=int(round(rw)))
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(0.80 * D * S)
    lh = int(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    layer.alpha_composite(logo, (int(cx * S - lw / 2), int(cy * S - lh / 2)))
    layer = layer.resize((W, H), Image.LANCZOS)
    la = np.array(layer).astype(float)
    alpha = la[..., 3:4] / 255.0
    # cylinder shading: scale by the column brightness relative to the brightest tube column
    colL = np.array([lum(out[cy:cy + 1, x])[0] for x in range(W)])
    tube_cols = np.zeros(W); tube_cols[left:right] = colL[left:right]
    peak = np.percentile(tube_cols[left:right], 90) if right > left else 1
    shade = np.clip(0.8 + 0.2 * (tube_cols / max(peak, 1)), 0.8, 1.0)[None, :, None]
    alpha = alpha * (~protect)[..., None] * ((xx > left + 1) & (xx < right - 1))[..., None]
    out = out * (1 - alpha) + la[..., :3] * shade * alpha

    res = Image.fromarray(out.clip(0, 255).astype("uint8"))
    res.save(os.path.join(P, f"{pid}_label.png"))
    res.save(os.path.join(P, f"{pid}.png"))
    print(f"{pid}: tube x {left}-{right} ({tube_w}px), label centre ({cx:.0f},{cy}), D {D:.0f}px, "
          f"repainted {int(repaint.sum())} px")
    if debug:
        dbg = res.copy(); dd = ImageDraw.Draw(dbg)
        dd.line((left, cy, right, cy), fill=(0, 255, 255))
        return dbg.crop((left - 40, int(cy - rad - 60), right + 40, int(cy + rad + 60)))
    return res.crop((left - 40, int(cy - rad - 60), right + 40, int(cy + rad + 60)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--debug", action="store_true"); ap.add_argument("--sheet")
    args = ap.parse_args()
    crops = [brand(k, s, t, ai, args.debug) for k, (s, t, ai) in PANELS.items()]
    if args.sheet:
        crops = [c.resize((int(c.width * 320 / c.height), 320), Image.LANCZOS) for c in crops]
        sheet = Image.new("RGB", (sum(c.width for c in crops) + 10 * len(crops), 320))
        x = 0
        for c in crops:
            sheet.paste(c, (x, 0)); x += c.width + 10
        sheet.save(args.sheet)
