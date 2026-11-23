#!/usr/bin/env python3
"""Build layout/sticker.html: side A (5-panel manga story) and side B (4 how-to steps + logo).

Each side is an SVG in millimetres: 50x100 mm trim + 2 mm bleed = 54x104 mm page.
Panels read right to left. Sound effects (Dela Gothic One) and the real logo are added here,
never by the image model. Panel art comes from assets/panels/<ID>.png (placeholders until generated).

  python3 scripts/build_layout.py [--guides]     # --guides adds trim/safe/cut lines for review
"""
import argparse, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TRIM_W, TRIM_H, BLEED = 50.0, 100.0, 2.0
PAGE_W, PAGE_H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
PX_W, PX_H = 638, 1228            # 54 x 104 mm at 300 DPI (rounded to whole pixels)
MARGIN, GUTTER = 2.5, 1.6         # from trim edge; between panels
SAFE = 3.0                        # keep sounds, seals and logo this far inside the trim
CUT_RADIUS = 2.0

INK, PAPER, BG = "#14110f", "#f1e9da", "#0a0a0a"   # BG = design-system token bg

LOGO_W = 26.0                     # design system: min 25 mm in print
LOGO_AR = 660 / 694               # height / width of assets/yoko-ono-logo-gold.png
LOGO_CLEAR = 0.15 * LOGO_W        # design system: 15% of logo width on every side


def x0():
    return BLEED + MARGIN


def usable_w():
    return TRIM_W - 2 * MARGIN


def side_a():
    W, g = usable_w(), GUTTER
    half = (W - g) / 2
    h1 = W / (21 / 9)
    h3 = half / (4 / 5)
    top = BLEED + MARGIN
    bottom = BLEED + TRIM_H - MARGIN
    h4 = bottom - top - 2 * h1 - h3 - 3 * g
    y1, y2 = top, top + h1 + g
    y3 = y2 + h1 + g
    y4 = y3 + h3 + g
    X = x0()
    # (id, x, y, w, h, focal "x% y%")
    return [("A1", X, y1, W, h1, "50% 50%"),
            ("A2", X, y2, W, h1, "50% 55%"),
            ("A3", X + half + g, y3, half, h3, "50% 50%"),   # right: read first
            ("A4", X, y3, half, h3, "50% 50%"),
            ("A5", X, y4, W, h4, "50% 50%")]


def side_b():
    W, g = usable_w(), GUTTER
    half = (W - g) / 2
    logo_top = BLEED + SAFE + 1.4
    logo_h = LOGO_W * LOGO_AR
    top = logo_top + logo_h + LOGO_CLEAR
    bottom = BLEED + TRIM_H - MARGIN
    h = (bottom - top - g) / 2
    X = x0()
    panels = [("B1", X + half + g, top, half, h, "50% 45%"),
              ("B2", X, top, half, h, "50% 45%"),
              ("B3", X + half + g, top + h + g, half, h, "50% 45%"),
              ("B4", X, top + h + g, half, h, "50% 40%")]
    logo = ((PAGE_W - LOGO_W) / 2, logo_top, LOGO_W, logo_h)
    return panels, logo


# Sound effects: text, panel, anchor inside the panel (fractions), size mm, rotation, vertical?
SFX = [("ザッ", "A2", 0.21, 0.40, 6.2, -8, False),
       ("ドン!!", "A3", 0.40, 0.22, 6.0, -12, False),
       ("ズザッ", "A4", 0.42, 0.80, 5.4, 10, False),
       ("ゴゴゴ", "A5", 0.89, 0.52, 5.0, 0, True)]


def rect_d(x, y, w, h, r):
    return (f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} "
            f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} "
            f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z")


def panel_svg(pid, x, y, w, h, focal):
    href = f"../assets/panels/{pid}.png"
    fx, fy = (float(v.strip("%")) / 100 for v in focal.split())
    # emulate object-position with xMinYMin/xMidYMid/xMaxYMax slices
    ax = "xMin" if fx < 0.34 else ("xMax" if fx > 0.66 else "xMid")
    ay = "YMin" if fy < 0.34 else ("YMax" if fy > 0.66 else "YMid")
    return f"""
  <g class="panel" id="p{pid}">
    <clipPath id="c{pid}"><rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"/></clipPath>
    <rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{PAPER}"/>
    <image href="{href}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"
           preserveAspectRatio="{ax}{ay} slice" clip-path="url(#c{pid})"/>
    <rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="none"
          stroke="{INK}" stroke-width="0.75" filter="url(#rough)"/>
  </g>"""


def sfx_svg(text, box, fx, fy, size, rot, vertical):
    x, y, w, h = box
    cx, cy = x + fx * w, y + fy * h
    style = "writing-mode: vertical-rl; text-orientation: upright;" if vertical else ""
    return f"""
  <g transform="translate({cx:.3f},{cy:.3f}) rotate({rot})" filter="url(#roughText)">
    <text class="sfx" x="0" y="0" font-size="{size}" style="{style}"
          text-anchor="middle" dominant-baseline="central">{text}</text>
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


def guides_svg():
    b, t = BLEED, SAFE
    return f"""
  <g class="guides">
    <path d="{rect_d(b, b, TRIM_W, TRIM_H, CUT_RADIUS)}" fill="none" stroke="#ff00ff" stroke-width="0.2"/>
    <rect x="{b + t}" y="{b + t}" width="{TRIM_W - 2 * t}" height="{TRIM_H - 2 * t}" fill="none"
          stroke="#00b7ff" stroke-width="0.15" stroke-dasharray="0.8 0.6"/>
  </g>"""


def page(side, body, guides):
    return f"""<svg class="side" id="side{side}" xmlns="http://www.w3.org/2000/svg"
     width="{PX_W}" height="{PX_H}" viewBox="0 0 {PAGE_W} {PAGE_H}">{DEFS}
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="{BG}"/>{body}{guides_svg() if guides else ""}
</svg>"""


def build(guides):
    a_panels = side_a()
    body_a = "".join(panel_svg(*p) for p in a_panels)
    boxes = {p[0]: p[1:5] for p in a_panels}
    body_a += "".join(sfx_svg(t, boxes[pid], fx, fy, s, r, v) for t, pid, fx, fy, s, r, v in SFX)

    b_panels, (lx, ly, lw, lh) = side_b()
    body_b = "".join(panel_svg(*p) for p in b_panels)
    body_b += "".join(seal_svg(i + 1, p[1:5]) for i, p in enumerate(b_panels))
    body_b += f"""
  <image href="../assets/yoko-ono-logo-gold.png" x="{lx:.3f}" y="{ly:.3f}" width="{lw:.3f}" height="{lh:.3f}"/>"""

    html = f"""<!doctype html>
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
  body.print figcaption {{ display: none; }}
</style></head>
<body>
<div class="wrap">
<figure>{page("A", body_a, guides)}<figcaption>צד א׳: הסיפור (נקרא מימין לשמאל) · 50×100 מ״מ + בליד 2 מ״מ</figcaption></figure>
<figure>{page("B", body_b, guides)}<figcaption>צד ב׳: הוראות שימוש + לוגו · 50×100 מ״מ + בליד 2 מ״מ</figcaption></figure>
</div>
</body></html>
"""
    os.makedirs(os.path.join(ROOT, "layout"), exist_ok=True)
    out = os.path.join(ROOT, "layout", "sticker_guides.html" if guides else "sticker.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--guides", action="store_true")
    build(ap.parse_args().guides)
