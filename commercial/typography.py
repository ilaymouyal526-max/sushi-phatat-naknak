"""Sumi (墨) type system for the sushi spot: one source of truth for every super in every cut.

Minimal Japanese layout: a vertical Shippori Mincho kanji column with kana, a red hanko seal,
a hairline gold rule and one widely tracked Montserrat Light word on a single shared baseline.

Motion:
  enter  (0.8s)  kanji brush-wipes in top to bottom; Latin letters rise and fade in one after another;
                 the rule draws out from the centre; the hanko stamps down (scale 1.35 -> 1).
  hold           slow 4px upward drift while the tracking "breathes" .45 -> .47em.
  exit   (0.3s)  fade, 8px rise and a soft blur.

Python:  import typography as T;  img = T.compose(img_rgb, "dish", t, dur)
CLI:     python3 typography.py --preview OUTDIR          contact sheet + motion test (stand-in plates)
         python3 typography.py --overlay KEY OUT.mov [--fps 24 --start S --length L]   RGBA overlay clip
         python3 typography.py --png KEY OUT.png         settled still, 1080x1920 RGBA
         python3 typography.py --check                   safe-area + glyph checks for every super
         python3 typography.py --kanji                   CJK characters used (for font subsetting)
"""
import argparse, os, subprocess, sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIR = Path(__file__).resolve().parent / "fonts"
LATIN_FONT, MINCHO, MINCHO_BOLD = "Montserrat-Light.ttf", "ShipporiMincho-Medium-subset.ttf", "ShipporiMincho-Bold-subset.ttf"

W, H = 1080, 1920
GOLD, PAPER, RED = (214, 178, 110), (236, 228, 212), (178, 34, 30)

# The whole type scale. Nothing else gets a size.
LATIN_PX, KANJI_PX, KANA_PX = 42, 88, 30
TRACK = .45                 # Latin tracking, in em
BASELINE = 1440             # top of the Latin line: the same for every super (4:5 and TikTok safe)
RULE_W, RULE_GAP = 140, 34  # hairline above the Latin word
COL_X = 170                 # kanji column centre: left side, clear of the TikTok right rail
HANKO_PX = 58
SAFE = (120, 285, 940, 1600)  # x0, y0, x1, y1 — inside the 4:5 crop, clear of TikTok rail and caption

ENTER, EXIT = .8, .3

# key: (latin, kanji, kana, layout).  "column" = vertical kanji column; "center" = end-card stack.
COPY = {
    "fire":     ("FIRE", "火", "炙り", "column"),
    "craft":    ("CRAFT", "技", "手仕事", "column"),
    "dish":     ("RED DRAGON TATAKI", "赤龍", "たたき", "column"),
    "fresh":    ("FRESH", "鮮", "新鮮", "column"),
    "handmade": ("HANDMADE", "手", "手仕事", "column"),
    "made":     ("MADE FOR YOU", "心", "おもてなし", "column"),
    "cta":      ("ORDER NOW", "今すぐ注文", "", "center"),
}


@lru_cache(None)
def font(name, px):
    p = FONT_DIR / name
    if not p.exists():
        raise SystemExit(f"typography: font missing: {p} (see fonts/README.md). Refusing to fall back to another face.")
    return ImageFont.truetype(str(p), px)


def _render(f, c):
    im = Image.new("L", (96, 96)); ImageDraw.Draw(im).text((8, 8), c, font=f, fill=255)
    return im.tobytes()


def _missing(f, text):
    notdef = _render(f, "")  # private-use codepoint: renders the font's .notdef box
    return sorted({c for c in text if not c.isspace() and _render(f, c) == notdef})


def check_glyphs():
    bad = []
    for key, (latin, kanji, kana, _) in COPY.items():
        for name, txt in ((LATIN_FONT, latin), (MINCHO, kanji + kana), (MINCHO_BOLD, "龍")):
            m = _missing(font(name, 40), txt)
            if m:
                bad.append(f"{key}: {name} has no glyph for {' '.join(m)}")
    if bad:
        raise SystemExit("typography: " + "; ".join(bad) + " (re-subset the font, see fonts/README.md)")


def _clip(x):
    return float(min(max(x, 0.), 1.))


def _out3(u):
    return 1 - (1 - u) ** 3


def _span(e, a, b):
    return _out3(_clip((e - a) / (b - a)))


@lru_cache(None)
def hanko(px=HANKO_PX, ch="龍"):
    """Red seal: rounded square, paper-coloured bold mincho, a slight hand-set tilt."""
    s = 2 * px  # supersample
    im = Image.new("RGBA", (s, s)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=s // 9, fill=RED + (238,))
    f = font(MINCHO_BOLD, int(s * .66)); bb = d.textbbox((0, 0), ch, font=f)
    d.text(((s - bb[2] - bb[0]) / 2, (s - bb[3] - bb[1]) / 2), ch, font=f, fill=PAPER + (255,))
    return im.resize((px, px), Image.LANCZOS).rotate(-3, Image.BICUBIC, expand=True)


def _glyph(d, cx, y, ch, f, fill):
    bb = d.textbbox((0, 0), ch, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y - bb[1]), ch, font=f, fill=fill)


def _latin(d, text, y, track_em, e, alpha):
    f = font(LATIN_FONT, LATIN_PX); tr = track_em * LATIN_PX
    widths = [f.getlength(c) for c in text]
    x = (W - sum(widths) - tr * (len(text) - 1)) / 2; n = len(text)
    for i, (c, w) in enumerate(zip(text, widths)):
        a0 = .2 + .35 * i / max(n - 1, 1); u = _span(e, a0, a0 + .3)
        if u > 0 and not c.isspace():
            d.text((x, y + round(18 * (1 - u))), c, font=f, fill=GOLD + (int(255 * u * alpha),))
        x += w + tr


def _stamp(L, cx, cy, u, alpha):
    if u <= 0:
        return
    hk = hanko(); sc = 1.35 - .35 * u
    hs = hk.resize((max(1, int(hk.width * sc)), max(1, int(hk.height * sc))), Image.BICUBIC)
    hs.putalpha(hs.getchannel("A").point(lambda v: int(v * u * alpha)))
    L.alpha_composite(hs, (int(cx - hs.width / 2), int(cy - hs.height / 2)))


def layer(key, t, dur=None):
    """RGBA W×H overlay for super `key`, t seconds after it starts entering.
    dur = total time on screen including the exit (None: enter, then hold forever)."""
    latin, kanji, kana, layout = COPY[key]
    L = Image.new("RGBA", (W, H))
    if t < 0 or (dur is not None and t >= dur):
        return L
    e = _clip(t / ENTER)
    hold = (dur - ENTER - EXIT) if dur else 2.5
    hu = _clip((t - ENTER) / max(hold, 1e-3)); hu = hu * hu * (3 - 2 * hu)
    x = _clip((t - (dur - EXIT)) / EXIT) if dur else 0.
    xo = _out3(x); alpha = 1 - xo
    dy = round(-4 * hu - 8 * xo)
    d = ImageDraw.Draw(L)
    y_lat = BASELINE + dy

    # hairline rule, drawn out from the centre
    ru = _span(e, .35, .8); half = RULE_W / 2 * ru
    if ru > 0:
        d.rectangle([W / 2 - half, y_lat - RULE_GAP, W / 2 + half, y_lat - RULE_GAP + 1], fill=GOLD + (int(220 * alpha),))
    _latin(d, latin, y_lat, TRACK * (1 + .045 * hu), e, alpha)

    if layout == "column":
        fk, fs = font(MINCHO, KANJI_PX), font(MINCHO, KANA_PX)
        steps = [(c, fk, KANJI_PX * 1.08, PAPER) for c in kanji]
        col_h = sum(s for *_, s, _ in steps) + 14 + len(kana) * KANA_PX * 1.15
        hk_cy = y_lat - 60 - HANKO_PX / 2
        y0 = int(hk_cy - HANKO_PX / 2 - 22 - col_h)
        col = Image.new("RGBA", (KANJI_PX * 2, int(col_h) + 40)); cd = ImageDraw.Draw(col)
        y = 10
        for c in kanji:
            _glyph(cd, KANJI_PX, y, c, fk, PAPER + (240,)); y += KANJI_PX * 1.08
        y += 14
        for c in kana:
            _glyph(cd, KANJI_PX, y, c, fs, GOLD + (235,)); y += KANA_PX * 1.15
        # brush wipe: soft 40px leading edge travelling top -> bottom
        cut = (col.height + 40) * _span(e, 0, .6)
        ramp = np.clip((cut - np.arange(col.height)) / 40, 0, 1)[:, None]
        a = np.asarray(col.getchannel("A"), np.float32) * ramp * alpha
        col.putalpha(Image.fromarray(a.astype(np.uint8)))
        L.alpha_composite(col, (COL_X - KANJI_PX, y0 - 10))
        _stamp(L, COL_X, hk_cy, _span(e, .45, .7), alpha)
    else:  # centre stack: hanko / rule / LATIN / caption
        cu = _span(e, .5, .85)
        if cu > 0:
            f = font(MINCHO, KANA_PX); cap = kanji + kana; w = d.textlength(cap, font=f)
            d.text(((W - w) / 2, y_lat + 74 + round(10 * (1 - cu))), cap, font=f, fill=GOLD + (int(235 * cu * alpha),))
        _stamp(L, W / 2, y_lat - RULE_GAP - 30 - HANKO_PX / 2, _span(e, .6, .85), alpha)

    bb = L.getbbox()
    if not bb:
        return L
    pad = 30; bb = (max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, W), min(bb[3] + pad, H))
    region = L.crop(bb)
    if x > 0:
        region = region.filter(ImageFilter.GaussianBlur(4 * x))
    sh = Image.new("RGBA", region.size)
    sh.putalpha(region.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .65)))
    sh.alpha_composite(region)
    out = Image.new("RGBA", (W, H)); out.paste(sh, bb[:2])
    return out


def compose(img, key, t, dur=None):
    """Composite super `key` onto an RGB PIL frame, returning a new RGB frame."""
    L = layer(key, t, dur); bb = L.getbbox()
    if not bb:
        return img
    base = img.crop(bb).convert("RGBA"); base.alpha_composite(L.crop(bb))
    img = img.copy(); img.paste(base.convert("RGB"), bb[:2])
    return img


def write_overlay(key, out, fps=24, start=0., length=None, dur=None):
    """RGBA overlay clip (PNG-in-MOV): transparent until `start`, then the super animates in."""
    length = length if length is not None else start + (dur or ENTER + 1.5)
    n = int(round(length * fps))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-c:v", "png", "-pix_fmt", "rgba", str(out)], stdin=subprocess.PIPE)
    for k in range(n):
        enc.stdin.write(layer(key, k / fps - start, dur).tobytes())
    enc.stdin.close()
    if enc.wait():
        raise SystemExit(f"typography: ffmpeg failed writing {out}")


def check_safe():
    x0, y0, x1, y1 = SAFE; bad = []
    for key in COPY:
        for t in (.3, ENTER, ENTER + 1.0, ENTER + 2.4):
            bb = layer(key, t, ENTER + 2.7).getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
            if bb and (bb[0] < x0 or bb[1] < y0 or bb[2] > x1 or bb[3] > y1):
                bad.append(f"{key}@{t:.1f}s bbox={bb}")
    return bad


# ---------- preview on stand-in plates (no footage needed) ----------
def _plate(seed, hue):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    g = np.exp(-((xx - rng.uniform(.35, .65)) ** 2 * 3 + (yy - rng.uniform(.35, .5)) ** 2 * 1.4) / .08)
    a = np.array([.05, .045, .05]) + g[..., None] * np.array(hue) * .75
    vig = 1 - .75 * np.clip(((xx - .5) ** 2 + (yy - .45) ** 2 * .6) / .35, 0, 1)
    a = a * vig[..., None] + rng.normal(0, .025, (H, W, 1))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def preview(outdir):
    os.makedirs(outdir, exist_ok=True)
    keys = ["fire", "craft", "dish", "cta"]
    hues = [(1, .45, .15), (.9, .55, .3), (.85, .2, .15), (.7, .55, .35)]
    plates = [_plate(i, h) for i, h in enumerate(hues)]
    th = 640; tw = int(W * th / H)
    sheet = Image.new("RGB", (tw * 4 + 50, th + 20), (18, 18, 18))
    for c, (k, p) in enumerate(zip(keys, plates)):
        im = compose(p, k, ENTER + .5); im.save(f"{outdir}/sumi_{k}.jpg", quality=92)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (10 + c * (tw + 10), 10))
    sheet.save(f"{outdir}/sumi_contact_sheet.png")
    fps, each = 24, 2.6
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                            "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            f"{outdir}/sumi_motion_test.mp4"], stdin=subprocess.PIPE)
    for k, p in zip(keys, plates):
        dur = None if k == "cta" else each
        for i in range(int(each * fps)):
            s = 1 + .025 * i / (each * fps)  # slow push so the plate isn't frozen
            bg = p.resize((int(W * s), int(H * s)), Image.BILINEAR).crop((0, 0, W, H))
            enc.stdin.write(compose(bg, k, i / fps - .15, dur).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", metavar="OUTDIR")
    ap.add_argument("--overlay", nargs=2, metavar=("KEY", "OUT.mov"))
    ap.add_argument("--png", nargs=2, metavar=("KEY", "OUT.png"))
    ap.add_argument("--fps", type=float, default=24)
    ap.add_argument("--start", type=float, default=0.)
    ap.add_argument("--length", type=float)
    ap.add_argument("--dur", type=float, help="time on screen incl. exit; omit to hold")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--kanji", action="store_true")
    a = ap.parse_args()
    if a.kanji:
        print("".join(sorted({c for v in COPY.values() for c in v[1] + v[2] + "龍" if ord(c) > 0x2E80})))
        sys.exit()
    check_glyphs()
    if a.check:
        bad = check_safe()
        print("safe-area: OK" if not bad else "safe-area FAIL: " + "; ".join(bad))
        sys.exit(1 if bad else 0)
    if a.png:
        layer(a.png[0], ENTER + 1.0).save(a.png[1])
    if a.overlay:
        write_overlay(a.overlay[0], a.overlay[1], a.fps, a.start, a.length, a.dur)
    if a.preview:
        preview(a.preview)
