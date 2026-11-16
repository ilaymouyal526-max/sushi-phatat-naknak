"""Yoko Ono dice-game terms card v2 (1080x1920). Run from the repo root."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

FD = "commercial/assets/fonts"  # Heebo + Suez One (Google Fonts, SIL OFL)
OUT = sys.argv[1] if len(sys.argv) > 1 else "commercial/assets/terms_card_v2.png"
W, H = 1080, 1920
BG = (20, 16, 11)
GOLD = (214, 178, 110); GOLD_HI = (240, 214, 150); GOLD_LO = (160, 122, 62)
CREAM = (238, 226, 204); RED = (176, 34, 28); RED_DK = (120, 20, 16); IVORY = (246, 238, 222)
R = W - 150          # right text edge (RTL)
L = 150


def heebo(size, weight):
    f = ImageFont.truetype(f"{FD}/Heebo.ttf", size)
    f.set_variation_by_axes([weight])
    return f


SUEZ = lambda s: ImageFont.truetype(f"{FD}/SuezOne.ttf", s)
HE = dict(direction="rtl", language="he")

# ---------- background: seigaiha waves + warm glow ----------
im = Image.new("RGB", (W, H), BG)
pat = ImageDraw.Draw(im)
r0, line = 46, (31, 25, 17)
for row, y in enumerate(range(-r0, H + r0, r0 // 2)):
    off = 0 if row % 2 == 0 else r0
    for x in range(-2 * r0 + off, W + 2 * r0, 2 * r0):
        for k, rr in enumerate((r0, r0 - 11, r0 - 22, r0 - 33)):
            pat.ellipse([x - rr, y - rr, x + rr, y + rr], fill=BG if k == 0 else None, outline=line, width=2)
yy, xx = np.mgrid[0:H, 0:W]
glow = np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - 330) / 420) ** 2))[..., None] * np.array([70, 48, 20])
vign = 1 - 0.55 * np.clip((((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2), 0, 1)[..., None]
im = Image.fromarray(np.clip((np.asarray(im, float) + glow) * vign, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(im)

# ---------- frame with corner ornaments ----------
d.rectangle([34, 34, W - 34, H - 34], outline=GOLD_LO, width=3)
d.rectangle([50, 50, W - 50, H - 50], outline=(92, 72, 42), width=1)
for cx, cy, sx, sy in [(50, 50, 1, 1), (W - 50, 50, -1, 1), (50, H - 50, 1, -1), (W - 50, H - 50, -1, -1)]:
    d.line([cx, cy + sy * 70, cx, cy, cx + sx * 70, cy], fill=GOLD, width=5)
    d.polygon([(cx + sx * 18, cy + sy * 6), (cx + sx * 30, cy + sy * 18), (cx + sx * 18, cy + sy * 30), (cx + sx * 6, cy + sy * 18)], fill=RED)

# ---------- logo ----------
logo = Image.open("commercial/assets/yoko_logo.png").convert("RGBA")
logo.thumbnail((300, 300))
im.paste(logo, ((W - logo.width) // 2, 92), logo)
d = ImageDraw.Draw(im)


# ---------- helpers ----------
def gold_text(text, font, y, center=True, x=None):
    """Text filled with a vertical gold gradient + soft shadow."""
    bbox = d.textbbox((0, 0), text, font=font, **HE)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    mask = Image.new("L", (w + 20, h + 30), 0)
    ImageDraw.Draw(mask).text((10 - bbox[0], 10 - bbox[1]), text, font=font, fill=255, **HE)
    gy = np.linspace(0, 1, mask.height)[:, None, None]
    grad = (np.array(GOLD_HI) * (1 - gy) + np.array(GOLD_LO) * gy) * np.ones((1, mask.width, 1))
    layer = Image.fromarray(grad.astype(np.uint8))
    px = (W - mask.width) // 2 if center else x - mask.width
    sh = mask.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .8))
    im.paste((0, 0, 0), (px + 3, y + 5), sh)
    im.paste(layer, (px, y), mask)
    return y + mask.height


def wrap(text, font, max_w):
    lines, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font, **HE) <= max_w: cur = t
        else: lines.append(cur); cur = w_
    return lines + [cur]


def die(x, y, s, n):
    """Ivory die with Asian-style pips (1 and 4 red)."""
    d.rounded_rectangle([x + 3, y + 5, x + s + 3, y + s + 5], radius=s // 5, fill=(0, 0, 0))
    d.rounded_rectangle([x, y, x + s, y + s], radius=s // 5, fill=IVORY, outline=(200, 186, 160), width=2)
    c = {1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 3: [(.25, .25), (.5, .5), (.75, .75)],
         4: [(.28, .28), (.72, .28), (.28, .72), (.72, .72)], 5: [(.26, .26), (.74, .26), (.5, .5), (.26, .74), (.74, .74)],
         6: [(.28, .24), (.72, .24), (.28, .5), (.72, .5), (.28, .76), (.72, .76)]}[n]
    pr = s * (.13 if n == 1 else .085)
    for u, v in c:
        d.ellipse([x + u * s - pr, y + v * s - pr, x + u * s + pr, y + v * s + pr], fill=RED if n in (1, 4) else (24, 20, 16))


# ---------- title ----------
y = gold_text("תקנון המשחק", SUEZ(104), 408)
sub = heebo(28, 300)
st = "R U L E S   O F   T H E   G A M E"
tw = d.textlength(st, font=sub)
d.text(((W - tw) / 2, y + 4), st, font=sub, fill=GOLD)
ly = y + 22
d.line([L, ly, (W - tw) / 2 - 26, ly], fill=GOLD_LO, width=2); d.line([(W + tw) / 2 + 26, ly, R, ly], fill=GOLD_LO, width=2)
y += 74

# ---------- numbered rules ----------
HEAD, BODY, NUM = heebo(42, 700), heebo(35, 400), heebo(34, 700)


def rule(n, head, body, y):
    cx, cy = R + 2, y + 26
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=GOLD, width=3)
    d.text((cx, cy + 1), str(n), font=NUM, fill=GOLD, anchor="mm")
    tx = R - 48
    d.text((tx, y), head, font=HEAD, fill=GOLD_HI, anchor="ra", **HE)
    y += 54
    for ln in wrap(body, BODY, tx - L):
        d.text((tx, y), ln, font=BODY, fill=CREAM, anchor="ra", **HE)
        y += 46
    return y + 20


y = rule(1, "רגע האמת", "המשחק מתקיים רק בסוף הארוחה, בזמן התשלום.", y)
y = rule(2, "הזדמנות אחת", "לכל השולחן יש הטלה אחת בלבד.", y)
y = rule(3, "שחקן אחד", "רק אדם אחד מטיל את הקוביות בשם כל השולחן.", y)
y = rule(4, "ההטלה המושלמת", "שתי הקוביות חייבות לקפוץ מהקיר שמולן.", y)

# ---------- prize boxes ----------
y += 6
bw, bh, gap = 372, 262, 36
bx_r = R + 28 - bw                    # right box (read first in RTL)
bx_l = bx_r - gap - bw
PH, PB, PS = heebo(40, 800), heebo(31, 500), SUEZ(64)
for bx, dice, big, head, body, hot in [
    (bx_r, (3, 3), "50%", "דאבל 1 · 2 · 3", "הנחה על כל החשבון", False),
    (bx_l, (6, 6), "חינם!", "דאבל 4 · 5 · 6", "ג'קפוט! הארוחה על הבית", True),
]:
    fill = (58, 18, 14) if hot else (34, 27, 19)
    d.rounded_rectangle([bx, y, bx + bw, y + bh], radius=22, fill=fill, outline=GOLD if hot else GOLD_LO, width=4 if hot else 2)
    mid = bx + bw / 2
    die(int(mid - 70), y + 22, 60, dice[0]); die(int(mid + 10), y + 22, 60, dice[1])
    d.text((mid, y + 104), head, font=PH, fill=GOLD_HI, anchor="mt", **HE)
    d.text((mid, y + 150), big, font=PS, fill=(255, 92, 70) if hot else GOLD, anchor="mt", **HE)
    lines = wrap(body, PB, bw - 40)
    d.text((mid, y + 222), body, font=heebo(28, 500), fill=CREAM, anchor="mt", **HE)
y += bh + 34

# ---------- remaining rules ----------
y = rule(5, "השירות", "הטיפ אינו כלול בהטבה ונשאר למלצר.", y)
y = rule(6, "חייכו, מצלמים!", "בהשתתפות ובזכייה מאשרים לצוות יוקו אונו לצלם את הרגע ולשתף אותו ברשתות החברתיות.", y)

# ---------- footer banner ----------
fy = max(y + 6, 1716)
d.rounded_rectangle([L - 20, fy, R + 20, fy + 104], radius=18, fill=RED_DK, outline=RED, width=3)
d.text((W / 2, fy + 52), "הכל כפוף לתקנון · חובה לקרוא לפני המשחק!", font=heebo(40, 800), fill=IVORY, anchor="mm", **HE)
print("rules end", y, "footer", fy)
im.save(OUT, optimize=True)
