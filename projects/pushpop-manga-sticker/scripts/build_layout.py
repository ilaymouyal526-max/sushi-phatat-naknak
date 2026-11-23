#!/usr/bin/env python3
"""Build the sticker layouts as HTML pages of SVGs in millimetres.

Side A (8-panel manga story, read right to left) comes from layout/side_a.json (panels, focal
points, sound effects). Side B (logo + 4 steps) is defined below and is unchanged.
Each side: 50x100 mm trim + 2 mm bleed = 54x104 mm page. The wrap-around label puts side B on the
LEFT and side A on the RIGHT: 100x100 mm trim + 2 mm bleed = 104x104 mm.
Sound effects (Dela Gothic One) and the real logo are added here, never by the image model.
Panel art: assets/panels/<ID>.png, any pixel size (read at build time), so a final image is just
dropped in at that path. A missing file renders as a labelled blank panel.

  python3 scripts/build_layout.py [--guides]     # writes layout/sticker[_guides].html and wrap[_guides].html
  python3 scripts/build_layout.py --placeholders A3 A3b A3c A6   # 1024x1024 washi placeholders
"""
import argparse, json, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TRIM_W, TRIM_H, BLEED = 50.0, 100.0, 2.0
PAGE_W, PAGE_H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
PX_W, PX_H = 638, 1228            # 54 x 104 mm at 300 DPI (rounded to whole pixels)
WRAP_TRIM_W = 2 * TRIM_W          # wrap-around label: B (left) + A (right)
WRAP_PAGE_W = WRAP_TRIM_W + 2 * BLEED
WRAP_PX_W = 1228                  # 104 mm at 300 DPI
MARGIN, GUTTER = 2.5, 1.6         # from trim edge; between panels
SAFE = 3.0                        # keep sounds, seals and logo this far inside the trim
CUT_RADIUS = 2.0

INK, PAPER, BG = "#14110f", "#f1e9da", "#0a0a0a"   # BG = design-system token bg

LOGO_W = 26.0                     # design system: min 25 mm in print
LOGO_AR = 660 / 694               # height / width of assets/yoko-ono-logo-gold.png
LOGO_CLEAR = 0.15 * LOGO_W        # design system: 15% of logo width on every side

SIDE_A_JSON = os.path.join(ROOT, "layout", "side_a.json")
PANEL_DIR = os.path.join(ROOT, "assets", "panels")


def x0():
    return BLEED + MARGIN


def usable_w():
    return TRIM_W - 2 * MARGIN


# ---------------------------------------------------------------- panels as data
class Panel:
    """A panel in PAGE coordinates (mm, bleed included). shape = rect or polygon."""

    def __init__(self, pid, pts, focal=(0.5, 0.5), zoom=1.0, img=None, beat=""):
        self.id, self.pts, self.focal, self.zoom, self.beat = pid, pts, tuple(focal), zoom, beat
        self.img = img or os.path.join(PANEL_DIR, f"{pid}.png")
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.x, self.y = min(xs), min(ys)
        self.w, self.h = max(xs) - self.x, max(ys) - self.y
        self.is_rect = len(pts) == 4 and len(set(xs)) == 2 and len(set(ys)) == 2

    @property
    def box(self):
        return self.x, self.y, self.w, self.h

    def crop(self):
        """Image placement (ix, iy, dw, dh) in mm: cover the bounding box, centre the focal point."""
        iw, ih = image_size(self.img)
        s = max(self.w / iw, self.h / ih) * self.zoom
        dw, dh = iw * s, ih * s
        fx, fy = self.focal
        ix = min(self.x, max(self.x + self.w - dw, self.x + self.w / 2 - fx * dw))
        iy = min(self.y, max(self.y + self.h - dh, self.y + self.h / 2 - fy * dh))
        return ix, iy, dw, dh

    def visible_fraction(self):
        """Part of the source image inside the bounding box: (x0, y0, x1, y1) as 0..1."""
        ix, iy, dw, dh = self.crop()
        return ((self.x - ix) / dw, (self.y - iy) / dh,
                (self.x + self.w - ix) / dw, (self.y + self.h - iy) / dh)


def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


_SIZES = {}


def image_size(path):
    if path not in _SIZES:
        try:
            from PIL import Image
            with Image.open(path) as im:
                _SIZES[path] = im.size
        except (OSError, ImportError):
            _SIZES[path] = None
    return _SIZES[path] or (1000, 1000)


def load_side_a(path=SIDE_A_JSON):
    """Read layout/side_a.json (trim coordinates) and return (panels, sfx) in page coordinates."""
    d = json.load(open(path, encoding="utf-8"))
    panels = []
    for p in d["panels"]:
        if "poly" in p:
            pts = [(BLEED + x, BLEED + y) for x, y in p["poly"]]
        else:
            x, y, w, h = p["box"]
            pts = rect_pts(BLEED + x, BLEED + y, w, h)
        img = os.path.join(ROOT, p["img"]) if p.get("img") else None
        panels.append(Panel(p["id"], pts, p.get("focal", (0.5, 0.5)), p.get("zoom", 1.0), img, p.get("beat", "")))
    return panels, d.get("sfx", [])


def side_a():
    return load_side_a()[0]


def side_b():
    W, g = usable_w(), GUTTER
    half = (W - g) / 2
    logo_top = BLEED + SAFE + 1.4
    logo_h = LOGO_W * LOGO_AR
    top = logo_top + logo_h + LOGO_CLEAR
    bottom = BLEED + TRIM_H - MARGIN
    h = (bottom - top - g) / 2
    X = x0()
    # unchanged grid; the old renderer snapped "50% 45%" to a centred crop, so focal = centre
    panels = [Panel("B1", rect_pts(X + half + g, top, half, h)),
              Panel("B2", rect_pts(X, top, half, h)),
              Panel("B3", rect_pts(X + half + g, top + h + g, half, h)),
              Panel("B4", rect_pts(X, top + h + g, half, h))]
    logo = ((PAGE_W - LOGO_W) / 2, logo_top, LOGO_W, logo_h)
    return panels, logo


# ---------------------------------------------------------------- SVG pieces
def rect_d(x, y, w, h, r):
    return (f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} "
            f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} "
            f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z")


def shape_svg(p, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    if p.is_rect:
        return f'<rect x="{p.x:.3f}" y="{p.y:.3f}" width="{p.w:.3f}" height="{p.h:.3f}" {a}/>'
    pts = " ".join(f"{x:.3f},{y:.3f}" for x, y in p.pts)
    return f'<polygon points="{pts}" {a}/>'


def panel_svg(p, uid):
    href = os.path.relpath(p.img, os.path.join(ROOT, "layout"))
    cid = f"c{uid}{p.id}"
    if image_size(p.img) is None or not os.path.exists(p.img):
        art = (f'<text x="{p.x + p.w / 2:.3f}" y="{p.y + p.h / 2:.3f}" font-size="3" fill="{INK}" '
               f'text-anchor="middle" dominant-baseline="central" font-family="sans-serif">{p.id} missing</text>')
    else:
        ix, iy, dw, dh = p.crop()
        art = (f'<image href="{href}" x="{ix:.3f}" y="{iy:.3f}" width="{dw:.3f}" height="{dh:.3f}" '
               f'preserveAspectRatio="none" clip-path="url(#{cid})"/>')
    return f"""
  <g class="panel" id="p{uid}{p.id}">
    <clipPath id="{cid}">{shape_svg(p)}</clipPath>
    {shape_svg(p, fill=PAPER)}
    {art}
    {shape_svg(p, fill="none", stroke=INK, stroke_width="0.75", stroke_linejoin="round", filter="url(#rough)")}
  </g>"""


def sfx_svg(s, box):
    x, y, w, h = box
    fx, fy = s["at"]
    cx, cy = x + fx * w, y + fy * h
    style = "writing-mode: vertical-rl; text-orientation: upright;" if s.get("vertical") else ""
    return f"""
  <g class="sfxg" data-text="{s['text']}" data-panel="{s['panel']}"
     transform="translate({cx:.3f},{cy:.3f}) rotate({s.get('rot', 0)})" filter="url(#roughText)">
    <text class="sfx" x="0" y="0" font-size="{s['size']}" style="{style}"
          text-anchor="middle" dominant-baseline="central">{s['text']}</text>
  </g>"""


def seal_svg(n, box):
    x, y, w, h = box
    r = 2.7
    cx, cy = x + w - r - 1.1, y + r + 1.1
    return f"""
  <g filter="url(#rough)">
    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r}" fill="{INK}"/>
  </g>
  <text class="num" x="{cx:.3f}" y="{cy + 0.15:.3f}" font-size="3.4" text-anchor="middle"
        dominant-baseline="central">{n}</text>"""


DEFS = f"""
  <defs>
    <filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4"/>
      <feDisplacementMap in="SourceGraphic" scale="0.45" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <filter id="roughText" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="1" seed="9"/>
      <feDisplacementMap in="SourceGraphic" scale="0.22" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>"""


def guides_svg(trim_w=TRIM_W, seams=()):
    b, t = BLEED, SAFE
    out = f"""
  <g class="guides">
    <path d="{rect_d(b, b, trim_w, TRIM_H, CUT_RADIUS)}" fill="none" stroke="#ff00ff" stroke-width="0.2"/>"""
    # safe zone per 50 mm side (the wrap seam is not a cut, but each side keeps its own safe box)
    for i in range(int(round(trim_w / TRIM_W))):
        out += f"""
    <rect x="{b + i * TRIM_W + t}" y="{b + t}" width="{TRIM_W - 2 * t}" height="{TRIM_H - 2 * t}" fill="none"
          stroke="#00b7ff" stroke-width="0.15" stroke-dasharray="0.8 0.6"/>"""
    for sx in seams:
        out += f"""
    <line x1="{sx}" y1="0" x2="{sx}" y2="{PAGE_H}" stroke="#ffd400" stroke-width="0.15" stroke-dasharray="1.2 0.8"/>"""
    return out + "\n  </g>"


def side_bodies(uid=""):
    """Artwork of each side (no background, no defs), in that side's own 54x104 page coordinates."""
    a_panels, a_sfx = load_side_a()
    body_a = "".join(panel_svg(p, uid + "A") for p in a_panels)
    boxes = {p.id: p.box for p in a_panels}
    body_a += "".join(sfx_svg(s, boxes[s["panel"]]) for s in a_sfx)

    b_panels, (lx, ly, lw, lh) = side_b()
    body_b = "".join(panel_svg(p, uid + "B") for p in b_panels)
    body_b += "".join(seal_svg(i + 1, p.box) for i, p in enumerate(b_panels))
    body_b += f"""
  <image href="../assets/yoko-ono-logo-gold.png" x="{lx:.3f}" y="{ly:.3f}" width="{lw:.3f}" height="{lh:.3f}"/>"""
    return body_a, body_b


def page(side, body, guides):
    return f"""<svg class="side" id="side{side}" xmlns="http://www.w3.org/2000/svg"
     width="{PX_W}" height="{PX_H}" viewBox="0 0 {PAGE_W} {PAGE_H}">{DEFS}
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="{BG}"/>{body}{guides_svg() if guides else ""}
</svg>"""


def wrap_page(body_a, body_b, guides):
    """One 100x100 mm label: side B on the LEFT, side A on the RIGHT (read right to left)."""
    seam = BLEED + TRIM_W
    return f"""<svg class="side" id="sideW" xmlns="http://www.w3.org/2000/svg"
     width="{WRAP_PX_W}" height="{PX_H}" viewBox="0 0 {WRAP_PAGE_W} {PAGE_H}">{DEFS}
  <clipPath id="wrapL"><rect x="0" y="0" width="{seam}" height="{PAGE_H}"/></clipPath>
  <clipPath id="wrapR"><rect x="{seam}" y="0" width="{WRAP_PAGE_W - seam}" height="{PAGE_H}"/></clipPath>
  <rect width="{WRAP_PAGE_W}" height="{PAGE_H}" fill="{BG}"/>
  <g clip-path="url(#wrapL)">{body_b}
  </g>
  <g clip-path="url(#wrapR)"><g transform="translate({TRIM_W},0)">{body_a}
  </g></g>{guides_svg(WRAP_TRIM_W, (seam,)) if guides else ""}
</svg>"""


def html_doc(figures):
    return f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<title>Push Pop Manga Sticker</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  @font-face {{ font-family: "Dela Gothic One"; src: url("../fonts/DelaGothicOne-Regular.ttf"); }}
  :root {{ --bg: #1b1916; --fg: #f3ece3; }}
  @media (prefers-color-scheme: light) {{ :root:not([data-theme="dark"]) {{ --bg: #e9e4dc; --fg: #1b1916; }} }}
  html, body {{ margin: 0; background: var(--bg); color: var(--fg); font-family: system-ui, sans-serif; }}
  .wrap {{ display: flex; flex-wrap: wrap; gap: 24px; justify-content: center; padding: 24px 16px; }}
  figure {{ margin: 0; text-align: center; }}
  figcaption {{ font-size: 13px; opacity: .75; margin-top: 8px; }}
  svg.side {{ max-width: 100%; height: auto; display: block; direction: ltr; unicode-bidi: isolate; }}
  .sfx {{ font-family: "Dela Gothic One"; fill: {INK}; stroke: {PAPER}; stroke-width: 0.55;
          paint-order: stroke fill; stroke-linejoin: round; }}
  .num {{ font-family: "Dela Gothic One"; fill: {PAPER}; }}
  body.print .wrap {{ padding: 0; gap: 0; }}
  body.print svg.side {{ max-width: none; }}
  body.print figcaption {{ display: none; }}
</style></head>
<body>
<div class="wrap">{figures}
</div>
</body></html>
"""


def write(name, html):
    os.makedirs(os.path.join(ROOT, "layout"), exist_ok=True)
    out = os.path.join(ROOT, "layout", name)
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out)


def build(guides):
    suffix = "_guides" if guides else ""
    body_a, body_b = side_bodies()
    write(f"sticker{suffix}.html", html_doc(
        f"""
<figure>{page("A", body_a, guides)}<figcaption>צד א׳: הסיפור (8 פאנלים, נקרא מימין לשמאל) · 50×100 מ״מ + בליד 2 מ״מ</figcaption></figure>
<figure>{page("B", body_b, guides)}<figcaption>צד ב׳: הוראות שימוש + לוגו · 50×100 מ״מ + בליד 2 מ״מ</figcaption></figure>"""))
    write(f"wrap{suffix}.html", html_doc(
        f"""
<figure>{wrap_page(body_a, body_b, guides)}<figcaption>עטיפה אחת: צד ב׳ משמאל, צד א׳ מימין · 100×100 מ״מ + בליד 2 מ״מ</figcaption></figure>"""))


# ---------------------------------------------------------------- placeholders
def placeholders(ids, size=1024):
    """1024x1024 washi placeholders with the panel id, beat and the central-70% action box."""
    import math, random
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    beats = {p.id: p.beat for p in side_a()}
    font = os.path.join(ROOT, "fonts", "DelaGothicOne-Regular.ttf")
    big, small = ImageFont.truetype(font, 230), ImageFont.truetype(font, 40)
    for pid in ids:
        rnd = random.Random(pid)
        im = Image.new("RGB", (size, size), (241, 233, 218))
        d = ImageDraw.Draw(im)
        for _ in range(900):                                   # washi fibres
            x, y = rnd.uniform(0, size), rnd.uniform(0, size)
            a, ln = rnd.uniform(0, 6.283), rnd.uniform(8, 40)
            c = rnd.randint(200, 228)
            d.line([(x, y), (x + ln * math.cos(a), y + ln * math.sin(a))], fill=(c, c - 6, c - 18), width=1)
        im = im.filter(ImageFilter.GaussianBlur(0.6))
        d = ImageDraw.Draw(im)
        m = 0.15 * size
        for i in range(0, int(size - 2 * m), 24):              # dashed central-70% box
            for (x1, y1, x2, y2) in [(m + i, m, m + i + 12, m), (m + i, size - m, m + i + 12, size - m),
                                     (m, m + i, m, m + i + 12), (size - m, m + i, size - m, m + i + 12)]:
                d.line([(x1, y1), (x2, y2)], fill=(150, 140, 125), width=3)
        d.line([(size / 2 - 30, size / 2), (size / 2 + 30, size / 2)], fill=(180, 40, 30), width=3)
        d.line([(size / 2, size / 2 - 30), (size / 2, size / 2 + 30)], fill=(180, 40, 30), width=3)
        d.text((size / 2, size / 2 - 60), pid, font=big, fill=(20, 17, 15), anchor="mm")
        d.text((size / 2, size / 2 + 120), "PLACEHOLDER", font=small, fill=(180, 40, 30), anchor="mm")
        d.text((size / 2, size / 2 + 180), beats.get(pid, "").split(" (")[0].split(",")[0][:30], font=small, fill=(60, 55, 50), anchor="mm")
        d.text((m + 10, m + 10), "action: central 70%", font=ImageFont.truetype(font, 26), fill=(150, 140, 125))
        out = os.path.join(PANEL_DIR, f"{pid}.png")
        im.save(out)
        print("placeholder", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--guides", action="store_true")
    ap.add_argument("--placeholders", nargs="+", metavar="ID",
                    help="write 1024x1024 placeholder PNGs for these panel ids (overwrites assets/panels/<ID>.png)")
    a = ap.parse_args()
    if a.placeholders:
        placeholders(a.placeholders)
    else:
        build(a.guides)
