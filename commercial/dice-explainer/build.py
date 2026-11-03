#!/usr/bin/env python3
"""Builds the Hebrew dice-game explainer: compositions/*.html and index.html.

Every card is a finished Noir & Or poster from its first frame; only the action moves.
Edit the cards and the shared CSS here, then run `python3 build.py`. Don't hand-edit the
generated HTML, because the next build overwrites it.
"""
from pathlib import Path

ROOT = Path(__file__).parent
GOLD, GOLD_HI, IVORY, INK, RED = "#c9a36b", "#e2c590", "#f4ecdf", "#0b0907", "#b8322a"
SKIN, SKIN_SH, SKIN_LN, SLEEVE = "#d9a77c", "#b9845c", "#8d5f3e", "#17120f"

FONTS = """
@font-face { font-family: "Frank Ruhl"; font-weight: 300 900; font-display: block; src: url('assets/fonts/frankruhl-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Frank Ruhl"; font-weight: 300 900; font-display: block; src: url('assets/fonts/frankruhl-normal-hebrew.woff2') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F; }
@font-face { font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-hebrew.woff2') format('woff2'); unicode-range: U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F; }
@font-face { font-family: "Cormorant"; font-weight: 500 700; font-display: block; src: url('assets/fonts/cormorant-upright-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Shippori"; font-weight: 800; font-display: block; src: url('assets/fonts/shippori-jp-subset.woff2') format('woff2'); }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: hidden; direction: rtl; font-variant-numeric: lining-nums;
  background: radial-gradient(ellipse 85% 55% at 50% 52%, #24160e 0%, {INK} 72%); }}
.h {{ position: absolute; left: 96px; right: 96px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 800; color: {IVORY}; line-height: 1.04; }}
.sub {{ position: absolute; left: 96px; right: 96px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 500; color: {GOLD_HI}; line-height: 1.28; }}
.kick {{ position: absolute; left: 96px; right: 96px; text-align: center; font-family: "Heebo", sans-serif; font-weight: 500; letter-spacing: .12em; color: {GOLD}; }}
.big {{ position: absolute; left: 60px; right: 60px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 700; line-height: .9; }}
.num {{ position: absolute; left: 500px; width: 80px; height: 80px; border-radius: 50%; border: 2px solid {GOLD}; display: grid; place-items: center;
  font-family: "Frank Ruhl", serif; font-weight: 700; font-size: 50px; color: {GOLD}; line-height: 1; }}
.die {{ position: absolute; }}
.art {{ position: absolute; overflow: visible; }}
.ltr {{ direction: ltr; unicode-bidi: isolate; display: inline-block; }}
"""


# ---------- shared drawings ----------

def logo_svg(id_, x, y, w, stroke=GOLD, extra=""):
    h = w * 1.3
    return f"""<svg id="{id_}" class="art" style="left:{x}px;top:{y}px;width:{w}px;height:{h:.0f}px" viewBox="0 0 200 260" data-layout-ignore {extra}>
  <g fill="none" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="M50 127 V68 A50 50 0 0 1 150 68 V127 M50 168 V192 A50 50 0 0 0 150 192 V168"/>
    <path d="M54 50 Q74 60 92 70 M146 50 Q126 60 108 70"/>
    <g>{''.join(f'<circle cx="{cx+dx:.1f}" cy="{cy+dy:.1f}" r="3.1"/>' for cx, cy in [(64,56),(80,66),(74,42),(136,56),(120,66),(126,42)] for dx, dy in [(0,-4.6),(4.4,-1.4),(2.7,3.7),(-2.7,3.7),(-4.4,-1.4)])}</g>
    <polyline points="62,124 86,90 99,106 113,80 138,124"/>
    <polyline points="80,99 84,103 88,98 92,102"/><polyline points="105,92 109,97 113,92 117,97 120,94"/>
    <path d="M78 182 L122 182 Q120 204 100 204 Q80 204 78 182 Z M99 181 L110 169 M105 182 L117 171"/>
    <path d="M70 230 Q100 208 130 230 M78 236 Q100 220 122 236 M86 240 Q100 230 114 240"/>
  </g>
  <text x="100" y="151" text-anchor="middle" direction="ltr" fill="{stroke}" font-family="Cormorant, serif" font-weight="600" font-size="29" letter-spacing="2.6">YOKO ONO</text>
  <text x="100" y="163" text-anchor="middle" direction="ltr" fill="{stroke}" font-family="Cormorant, serif" font-weight="700" font-size="8.6" letter-spacing="1.9">ASIAN KITCHEN</text>
</svg>"""


def hand_svg(id_, x, y, w, pose="open"):
    """A right hand seen from the back, fingers up, black sleeve with a gold cuff. Poses: open, release, fist."""
    fingers = {
        "open":    [((150, 300), (126, 106), 46), ((196, 292), (192, 66), 48), ((240, 294), (254, 88), 46), ((280, 306), (308, 158), 40)],
        "release": [((150, 300), (140, 168), 46), ((196, 292), (196, 150), 48), ((240, 294), (246, 160), 46), ((280, 306), (290, 200), 40)],
        "fist":    [((150, 300), (150, 250), 50), ((196, 292), (196, 240), 52), ((240, 294), (240, 246), 50), ((280, 306), (278, 266), 44)],
    }[pose]
    thumb = {"open": ((132, 420), (54, 300)), "release": ((132, 420), (74, 318)), "fist": ((132, 420), (170, 330))}[pose]

    def stroke(a, b, wd, color):
        return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{color}" stroke-width="{wd}" stroke-linecap="round"/>'

    parts = [stroke(*thumb, 58, SKIN_LN), stroke(*thumb, 52, SKIN)]
    parts += [stroke(a, b, wd + 6, SKIN_LN) for a, b, wd in fingers]
    parts += [stroke(a, b, wd, SKIN) for a, b, wd in fingers]
    parts += [f'<path d="M118 500 C104 430 102 360 120 300 Q200 268 290 300 C306 360 302 430 290 500 Z" fill="{SKIN}" stroke="{SKIN_LN}" stroke-width="3"/>',
              f'<path d="M140 330 Q200 312 270 330" fill="none" stroke="{SKIN_SH}" stroke-width="6" stroke-linecap="round"/>',
              f'<path d="M150 420 Q170 455 150 495" fill="none" stroke="{SKIN_SH}" stroke-width="5" stroke-linecap="round"/>',
              f'<rect x="92" y="500" width="224" height="150" rx="18" fill="{SLEEVE}"/>',
              f'<rect x="92" y="494" width="224" height="24" rx="6" fill="{GOLD}"/>']
    return (f'<svg id="{id_}" class="art" style="left:{x}px;top:{y}px;width:{w}px;height:{w*1.6:.0f}px" viewBox="0 0 400 640" data-layout-ignore>'
            + "".join(parts) + "</svg>")


def die(id_, face, x, y, size):
    return f'<div id="{id_}" class="die" data-face="{face}" style="left:{x}px;top:{y}px;width:{size}px;height:{size*1.0735:.0f}px"></div>'


def stamp(id_, text, top, color, rot):
    return (f'<div id="{id_}" style="position:absolute;left:0;right:0;top:{top}px;text-align:center">'
            f'<span style="display:inline-block;padding:14px 46px;border:6px solid {color};border-radius:16px;color:{color};'
            f'font-family:Heebo,sans-serif;font-weight:800;font-size:68px;line-height:1.1;background:rgba(11,9,7,.78);rotate:{rot}deg">{text}</span></div>')


# ---------- the cards ----------
# Each card: id, start, duration, extra CSS, body HTML, timeline JS (sets only for the stills stage).

FELT_PLANE = f"""
<div class="plane" data-layout-allow-overflow>
  <div class="wallband"></div><div class="felt"></div><div class="wallhi"></div>
  {logo_svg("@@-felt-logo", 320, 430, 360, stroke="#d6b26e")}
  @@PATHS@@
  <div id="@@-shA" class="sh"></div><div id="@@-shB" class="sh"></div>
  <div id="@@-dA" class="pdie" data-face="@@FA@@"></div><div id="@@-dB" class="pdie" data-face="@@FB@@"></div>
</div>"""

FELT_CSS = f"""
.plane {{ position: absolute; left: 40px; top: -530px; width: 1000px; height: 2600px; transform-origin: 50% 100%; transform: perspective(2500px) rotateX(30deg); transform-style: preserve-3d;
  background: linear-gradient(90deg, #6f4426 0%, #9a6539 18%, #7f4f2c 50%, #9a6539 82%, #6f4426 100%); border-radius: 26px; }}
.wallband {{ position: absolute; inset: 44px; border-radius: 10px; background: #11512d; box-shadow: inset 0 0 40px rgba(0,0,0,.6); }}
.felt {{ position: absolute; inset: 88px; border-radius: 6px; background: radial-gradient(ellipse 75% 45% at 50% 38%, #217d47 0%, #1a6b3c 45%, #0f4526 100%); }}
.wallhi {{ position: absolute; left: 44px; right: 44px; top: 44px; height: 46px; background: {GOLD}; opacity: .35; }}
.pdie {{ position: absolute; left: -75px; top: -81px; width: 150px; height: 162px; }}
.sh {{ position: absolute; left: -70px; top: -30px; width: 170px; height: 120px; border-radius: 50%;
  background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,.55) 0%, rgba(120,8,22,.35) 42%, rgba(0,0,0,0) 70%); }}
"""


def felt(prefix, fa, fb, paths):
    return FELT_PLANE.replace("@@PATHS@@", paths).replace("@@FA@@", str(fa)).replace("@@FB@@", str(fb)).replace("@@", prefix)


def place(prefix, ax, ay, bx, by):
    return (f'tl.set(["#{prefix}-dA", "#{prefix}-shA"], {{ x: {ax}, y: {ay} }}, 0);\n'
            f'tl.set(["#{prefix}-dB", "#{prefix}-shB"], {{ x: {bx}, y: {by} }}, 0);')


CARDS = []


def card(id_, start, dur, body, css="", js=""):
    CARDS.append(dict(id=id_, start=start, dur=dur, body=body, css=css, js=js))


# 1. Hook: one throw, and the bill could disappear
card("s1", 0, 2.5, f"""
<div class="h" style="top:250px;font-size:150px">הטלה אחת…</div>
<div class="sub" style="top:440px;font-size:64px">…והחשבון יכול להיעלם</div>
{die("s1-dA", 6, 170, 650, 300)}{die("s1-dB", 5, 600, 760, 300)}
{hand_svg("s1-hand", 330, 1190, 420, "open")}
""", js="""tl.set("#s1-dA", { rotation: -18 }, 0); tl.set("#s1-dB", { rotation: 24 }, 0); tl.set("#s1-hand", { rotation: -10 }, 0);""")

# 2. The brand and the name
card("s2", 2.5, 3.75, f"""
{logo_svg("s2-logo", 300, 160, 480)}
<div id="s2-jp" style="position:absolute;right:86px;top:230px;font-family:Shippori,serif;font-weight:800;font-size:56px;letter-spacing:.16em;color:{GOLD};writing-mode:vertical-rl">運試し</div>
<div id="s2-badge" style="position:absolute;left:84px;top:600px;width:170px;height:170px;border-radius:50%;border:2px solid {GOLD};background:{INK};display:grid;place-items:center;font-family:'Frank Ruhl',serif;font-weight:800;font-size:58px;color:{GOLD_HI}">חדש</div>
<div class="kick" style="top:836px;font-size:46px">המשחק הגדול</div>
<div class="h" style="top:906px;font-size:104px">הטילו את הקוביות</div>
{die("s2-dA", 6, 378, 1080, 140)}{die("s2-dB", 6, 560, 1092, 140)}
<div id="s2-seal" style="position:absolute;left:502px;top:1262px;width:76px;height:76px;border-radius:4px;background:{RED};color:{IVORY};display:grid;place-items:center;font-family:Shippori,serif;font-weight:800;font-size:48px">運</div>
""", js="""tl.set("#s2-badge", { rotation: -12 }, 0); tl.set("#s2-dA", { rotation: -14 }, 0); tl.set("#s2-dB", { rotation: 9 }, 0);""")

# 3a. When: happy hour, 16:00-18:00
card("s3a", 6.25, 3.75, f"""
<div class="h" style="top:220px;font-size:132px">האפי האוור</div>
<div class="big" style="top:392px;font-size:140px;color:{IVORY}"><span class="ltr">16:00–18:00</span></div>
<div class="sub" style="top:560px;font-size:58px">בואו בין ארבע לשש</div>
<svg id="s3a-dial" class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <path d="M160 1250 A380 380 0 0 1 920 1250" fill="none" stroke="{GOLD}" stroke-width="3"/>
  <g stroke="{GOLD}" stroke-width="4" stroke-linecap="round"><line x1="196" y1="1048" x2="222" y2="1063"/><line x1="540" y1="856" x2="540" y2="886"/><line x1="904" y1="1080" x2="876" y2="1093"/></g>
  <g fill="{GOLD_HI}" font-family="Frank Ruhl, serif" font-weight="700" font-size="40" text-anchor="middle" direction="ltr">
    <text x="296" y="1110">16:00</text><text x="540" y="836">17:00</text><text x="786" y="1136">18:00</text></g>
  <g id="s3a-sunrig"><circle cx="160" cy="1250" r="56" fill="{RED}"/></g>
  <polyline points="160,1250 390,1090 480,1146 620,1050 870,1250 920,1250" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linejoin="round"/>
  <rect x="0" y="1253" width="1080" height="667" fill="{INK}"/>
  <line x1="120" y1="1251" x2="960" y2="1251" stroke="{GOLD}" stroke-width="3"/>
</svg>
""", js="""tl.set("#s3a-sunrig", { rotation: 150, svgOrigin: "540 1250" }, 0);""")

# 3b. Rule 1: the moment of truth
TABLE_CSS = """
.table { position: absolute; left: 80px; top: 680px; width: 920px; height: 620px; border-radius: 44px;
  background: linear-gradient(97deg, #3b2414 0%, #4a2d19 28%, #3a2313 55%, #462a17 80%, #3b2414 100%);
  box-shadow: inset 0 0 0 3px rgba(201,163,107,.55), inset 0 0 90px rgba(0,0,0,.55); }
.folder { position: absolute; border-radius: 12px; background: linear-gradient(160deg, #1a1410 0%, #0d0a08 100%);
  box-shadow: 0 18px 40px rgba(0,0,0,.6), inset 0 0 0 2px #c9a36b, inset 0 0 0 10px #0d0a08, inset 0 0 0 11px rgba(201,163,107,.5); }
"""
PLATES = "".join(
    f'<g><circle cx="{cx}" cy="{cy}" r="80" fill="#1b130d" stroke="{GOLD}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="58" fill="none" stroke="rgba(201,163,107,.45)" stroke-width="1.5"/>'
    f'<circle cx="{cx-12}" cy="{cy-8}" r="5" fill="#e8dcc6"/><circle cx="{cx+14}" cy="{cy+10}" r="4" fill="#e8dcc6"/>'
    f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/></g>'
    for cx, cy, sx1, sy1, sx2, sy2 in [(460, 106, 560, 50, 574, 160), (790, 310, 730, 420, 846, 432), (460, 514, 340, 460, 354, 572), (130, 310, 74, 190, 186, 202)])
card("s3b", 10.0, 3.75, f"""
<div class="num" style="top:196px">1</div>
<div class="h" style="top:300px;font-size:128px">רגע האמת</div>
<div class="sub" style="top:448px;font-size:54px">משחקים רק בסוף הארוחה,<br>כשמגיע החשבון</div>
<div class="table"><svg class="art" style="left:0;top:0;width:920px;height:620px" viewBox="0 0 920 620" data-layout-ignore>{PLATES}</svg></div>
<div id="s3b-folder" class="folder" style="left:322px;top:850px;width:420px;height:290px">
  {die("s3b-dA", 3, 92, 80, 120)}{die("s3b-dB", 5, 222, 92, 120)}
</div>
{hand_svg("s3b-hand", 840, 760, 300, "open")}
""", css=TABLE_CSS, js="""tl.set("#s3b-hand", { rotation: -100, transformOrigin: "50% 50%" }, 0); tl.set("#s3b-folder", { rotation: -3 }, 0);""")

# 4. Rule 2: one chance
card("s4", 13.75, 3.75, f"""
<div class="num" style="top:196px">2</div>
<div class="h" style="top:300px;font-size:120px">הזדמנות אחת</div>
<div class="big" style="top:470px;font-size:400px;color:{GOLD}"><span class="ltr">×1</span></div>
<div class="sub" style="top:900px;font-size:56px">ניסיון אחד ויחיד לכל השולחן</div>
{die("s4-dA", 4, 300, 1030, 220)}{die("s4-dB", 2, 560, 1040, 220)}
""", js="""tl.set("#s4-dA", { rotation: -12 }, 0); tl.set("#s4-dB", { rotation: 10 }, 0);""")

# 5. Rule 3: one player
DINER = """<g transform="translate({x} {y}) rotate({r})"><ellipse cx="0" cy="34" rx="104" ry="58" fill="{c}"/><circle cx="0" cy="-6" r="46" fill="{hair}"/></g>"""
diners = "".join(DINER.format(x=x, y=y, r=r, c=c, hair=h) for x, y, r, c, h in [
    (540, 640, 180, "#3a3530", "#1d1916"), (232, 960, 90, "#4a3326", "#2a1d16"), (540, 1286, 0, "#2f3340", "#1a1712")])
card("s5", 17.5, 3.75, f"""
<div class="num" style="top:196px">3</div>
<div class="h" style="top:300px;font-size:128px">שחקן אחד</div>
<div class="sub" style="top:452px;font-size:56px">רק אחד מטיל, בשביל כולם</div>
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <circle cx="540" cy="960" r="276" fill="#3e2616" stroke="rgba(201,163,107,.6)" stroke-width="3"/>
  <circle cx="540" cy="960" r="250" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="30"/>
  {''.join(f'<circle cx="{x}" cy="{y}" r="54" fill="#1b130d" stroke="{GOLD}" stroke-width="2.5"/>' for x, y in [(540, 760), (340, 960), (540, 1160), (740, 960)])}
  {diners}
  <circle cx="848" cy="960" r="132" fill="rgba(201,163,107,.16)" stroke="{GOLD}" stroke-width="6"/>
  <g transform="translate(848 960) rotate(-90)"><ellipse cx="0" cy="34" rx="104" ry="58" fill="#5b4433"/><circle cx="0" cy="-6" r="46" fill="#2a1d16"/></g>
</svg>
{die("s5-dA", 1, 664, 880, 84)}{die("s5-dB", 6, 664, 980, 84)}
""", js="""tl.set("#s5-dA", { rotation: -8 }, 0); tl.set("#s5-dB", { rotation: 12 }, 0);""")

# 6a. Rule 4: the throw that doesn't count
MISS_PATHS = f"""<svg class="art" style="left:0;top:0;width:1000px;height:2600px" viewBox="0 0 1000 2600" data-layout-ignore>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="430,2350 400,128 362,520" stroke="{IVORY}" stroke-width="7" stroke-dasharray="2 22" opacity=".85"/>
    <polyline points="590,2380 565,905 575,830" stroke="{IVORY}" stroke-width="7" stroke-dasharray="2 22" opacity=".85"/>
    <circle cx="575" cy="830" r="118" stroke="{RED}" stroke-width="10"/></g></svg>"""
card("s6a", 21.25, 3.75, f"""
<div id="s6a-all" style="position:absolute;inset:0;background:radial-gradient(ellipse 90% 30% at 50% 18%, #22150d 0%, {INK} 75%)">
{felt("s6a", 4, 2, MISS_PATHS)}
</div>
<div class="num" style="top:176px">4</div>
<div class="h" style="top:276px;font-size:108px">ההטלה המושלמת</div>
<div class="kick" style="top:420px;font-size:46px;letter-spacing:.04em;font-weight:700">הקיר שממול ⌄</div>
{stamp("s6a-x", "✕&nbsp; לא נחשב", 1040, "#e0574b", -5)}
<div class="h" style="top:1190px;font-size:76px;color:{GOLD_HI}">מטילים שוב!</div>
{hand_svg("s6a-hand", 360, 1480, 360, "open")}
""", css=FELT_CSS, js=place("s6a", 362, 520, 575, 830))

# 6b. Rule 4: the perfect throw
OK_PATHS = f"""<svg class="art" style="left:0;top:0;width:1000px;height:2600px" viewBox="0 0 1000 2600" data-layout-ignore>
  <g fill="none" stroke="{GOLD_HI}" stroke-opacity=".8" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M430 2350 L380 128 L330 700"/><path d="M590 2380 L610 128 L680 820"/></g></svg>"""
card("s6b", 25.0, 6.25, f"""
<div id="s6b-all" style="position:absolute;inset:0;background:radial-gradient(ellipse 90% 30% at 50% 18%, #22150d 0%, {INK} 75%)">
{felt("s6b", 3, 5, OK_PATHS)}
</div>
<div class="num" style="top:176px">4</div>
<div class="h" style="top:276px;font-size:108px">ההטלה המושלמת</div>
<div class="sub" style="top:410px;font-size:50px">שתי הקוביות חייבות לפגוע בקיר</div>
<svg id="s6b-ok" class="art" style="left:465px;top:1150px;width:150px;height:150px" viewBox="0 0 140 140" data-layout-ignore>
  <circle cx="70" cy="70" r="62" fill="{INK}" stroke="{GOLD}" stroke-width="5"/>
  <path d="M40 72 L62 94 L102 50" fill="none" stroke="{GOLD_HI}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg>
{hand_svg("s6b-hand", 360, 1480, 360, "open")}
""", css=FELT_CSS, js=place("s6b", 330, 700, 680, 820))

# 7. Prize: double 1-2-3, 50% off
RECEIPT = f"""<div style="position:absolute;inset:0;background:#f3eadb;border-radius:6px;box-shadow:0 20px 40px rgba(0,0,0,.5)">
  <div style="position:absolute;top:26px;left:0;right:0;text-align:center;font-family:Cormorant,serif;font-weight:700;font-size:30px;letter-spacing:.2em;color:#3a2a1c;direction:ltr">YOKO ONO</div>
  <div style="position:absolute;top:70px;left:40px;right:40px;height:2px;background:#3a2a1c;opacity:.5"></div>
  {''.join(f'<div style="position:absolute;top:{100+i*40}px;left:40px;right:{90+(i*37)%80}px;height:10px;border-radius:5px;background:#3a2a1c;opacity:.22"></div>' for i in range(6))}
</div>"""
card("s7", 31.25, 5.0, f"""
<div class="h" style="top:206px;font-size:110px">דאבל 1 · 2 · 3</div>
{die("s7-dA", 3, 392, 360, 130)}{die("s7-dB", 3, 558, 360, 130)}
<div class="big" style="top:540px;font-size:300px;color:{GOLD_HI}"><span class="ltr">−50%*</span></div>
<div class="sub" style="top:852px;font-size:58px">על כל החשבון של השולחן</div>
<div id="s7-rcL" style="position:absolute;left:290px;top:960px;width:500px;height:360px;clip-path:polygon(0 0, 52% 0, 46% 100%, 0 100%)">{RECEIPT}</div>
<div id="s7-rcR" style="position:absolute;left:290px;top:960px;width:500px;height:360px;clip-path:polygon(52% 0, 100% 0, 100% 100%, 46% 100%)">{RECEIPT}</div>
<svg id="s7-knife" class="art" style="left:620px;top:900px;width:420px;height:120px" viewBox="0 0 420 120" data-layout-ignore>
  <path d="M10 70 L300 40 Q330 38 330 54 L330 70 Z" fill="#e8e2d6" stroke="{GOLD}" stroke-width="3"/>
  <rect x="330" y="46" width="84" height="26" rx="8" fill="#2a1d16" stroke="{GOLD}" stroke-width="3"/></svg>
""", js="""tl.set("#s7-rcL", { x: -34, y: 10, rotation: -5 }, 0); tl.set("#s7-rcR", { x: 34, y: -6, rotation: 4 }, 0); tl.set("#s7-knife", { rotation: -8 }, 0); tl.set("#s7-dA", { rotation: -8 }, 0); tl.set("#s7-dB", { rotation: 7 }, 0);""")

# 8. Prize: double 4-5-6, jackpot
PETALS = "".join(
    f'<g transform="translate({x} {y}) rotate({r}) scale({s})"><path d="M0 -18 C10 -18 14 -6 6 2 L0 8 L-6 2 C-14 -6 -10 -18 0 -18 Z" fill="{c}"/></g>'
    for x, y, r, s, c in [(140, 300, 20, 1.6, "#f7d6d9"), (930, 380, -30, 1.3, IVORY), (180, 980, 60, 1.4, "#f3c1c6"), (900, 1040, 10, 1.7, "#f7d6d9"),
                          (120, 1220, -40, 1.2, IVORY), (960, 1260, 35, 1.5, "#f3c1c6"), (300, 1330, 80, 1.1, "#f7d6d9"), (790, 1320, -15, 1.3, IVORY),
                          (980, 820, 50, 1.0, "#f3c1c6"), (90, 720, -20, 1.2, "#f7d6d9")])
LEAF = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#f3eadb" transform="rotate({r} {x} {y})" opacity=".9"/>'
               for x, y, w, h, r in [(220, 1140, 70, 46, -18), (760, 1150, 60, 40, 22), (180, 470, 50, 34, 30), (880, 560, 64, 42, -26), (640, 1300, 54, 36, 12)])
card("s8", 36.25, 5.0, f"""
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 45%, #ecd29a 0%, #d6b273 50%, #a8814a 100%)"></div>
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>{LEAF}{PETALS}</svg>
<div id="s8-ribbon" style="position:absolute;left:250px;top:196px;width:580px;height:118px;background:{RED};clip-path:polygon(0 0, 100% 0, 94% 50%, 100% 100%, 0 100%, 6% 50%);display:grid;place-items:center;
  font-family:'Frank Ruhl',serif;font-weight:900;font-size:76px;color:{IVORY};line-height:1">ג'קפוט!</div>
<div class="h" style="top:348px;font-size:100px;color:#14110e">דאבל 4 · 5 · 6</div>
<div class="big" style="top:476px;font-size:320px;color:#14110e"><span class="ltr">100%*</span></div>
<div class="h" style="top:808px;font-size:84px;color:#14110e">כל הארוחה עלינו</div>
{die("s8-dA", 6, 330, 990, 200)}{die("s8-dB", 6, 560, 1004, 200)}
""", js="""tl.set("#s8-dA", { rotation: -10 }, 0); tl.set("#s8-dB", { rotation: 8 }, 0);""")

# 9. No double
card("s9", 41.25, 2.5, f"""
<div class="h" style="top:240px;font-size:124px">לא יצא דאבל?</div>
<div class="sub" style="top:410px;font-size:60px">נשארתם עם ארוחה מעולה</div>
{die("s9-dA", 3, 250, 600, 260)}{die("s9-dB", 5, 580, 640, 260)}
<svg class="art" style="left:390px;top:1010px;width:300px;height:300px" viewBox="0 0 300 300" data-layout-ignore>
  <g fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 140 L240 140 Q236 250 150 254 Q64 250 60 140 Z"/><path d="M40 266 L260 266"/>
    <path d="M120 112 Q104 86 122 62 Q138 40 124 18"/><path d="M170 112 Q154 86 172 62 Q188 40 174 18"/></g></svg>
""", js="""tl.set("#s9-dA", { rotation: -14 }, 0); tl.set("#s9-dB", { rotation: 11 }, 0);""")

# 10. The service: the tip isn't included
card("s10", 43.75, 3.75, f"""
<div class="h" style="top:240px;font-size:132px">השירות</div>
<div class="sub" style="top:416px;font-size:62px">הטיפ לא כלול בהטבה</div>
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <ellipse cx="540" cy="1080" rx="300" ry="118" fill="#120e0b" stroke="{GOLD}" stroke-width="5"/>
  <ellipse cx="540" cy="1074" rx="250" ry="88" fill="#1d1612" stroke="rgba(201,163,107,.5)" stroke-width="2"/>
  {''.join(f'<g><ellipse cx="{x}" cy="{y+10}" rx="62" ry="24" fill="#8a6a35"/><ellipse cx="{x}" cy="{y}" rx="62" ry="24" fill="#e2c590" stroke="#a88545" stroke-width="3"/><ellipse cx="{x}" cy="{y}" rx="42" ry="15" fill="none" stroke="#a88545" stroke-width="2"/></g>' for x, y in [(470, 1070), (600, 1084), (540, 1046)])}
</svg>
""")

# 11. Smile, you're on camera
FIG = """<g transform="translate({x} {y})"><path d="M-70 120 Q-70 20 0 20 Q70 20 70 120 Z" fill="{c}"/>
<path d="M-50 40 L-96 -60" stroke="{c}" stroke-width="30" stroke-linecap="round"/><path d="M50 40 L96 -60" stroke="{c}" stroke-width="30" stroke-linecap="round"/>
<circle cx="-98" cy="-66" r="17" fill="{s}"/><circle cx="98" cy="-66" r="17" fill="{s}"/>
<circle cx="0" cy="-20" r="44" fill="{s}"/><path d="M-44 -26 Q-40 -72 0 -70 Q40 -72 44 -26 Q30 -50 0 -50 Q-30 -50 -44 -26 Z" fill="{h}"/>
<path d="M-16 -8 Q0 6 16 -8" fill="none" stroke="#5a3424" stroke-width="5" stroke-linecap="round"/></g>"""
figs = "".join(FIG.format(x=x, y=y, c=c, s=s, h=h) for x, y, c, s, h in [
    (390, 1040, "#7a2e2a", SKIN, "#2a1d16"), (540, 1000, "#2f3340", "#c38d63", "#1a1712"), (690, 1040, "#5b4433", "#e3b98f", "#4a3020")])
card("s11", 47.5, 5.0, f"""
<div class="h" style="top:200px;font-size:110px">חייכו,<br>אתם מצולמים!</div>
<div class="sub" style="top:446px;font-size:52px">רגעי הזכייה עולים לרשתות שלנו</div>
<div style="position:absolute;left:300px;top:556px;width:480px;height:770px;border-radius:56px;background:#0f0d0c;box-shadow:inset 0 0 0 4px {GOLD}, 0 24px 50px rgba(0,0,0,.6)"></div>
<div style="position:absolute;left:320px;top:590px;width:440px;height:700px;border-radius:38px;overflow:hidden;background:radial-gradient(ellipse 80% 60% at 50% 60%, #4a2c18 0%, #1c120c 80%)">
  <svg class="art" style="left:-300px;top:-590px;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
    <rect x="300" y="1150" width="480" height="200" fill="#1a6b3c"/>{figs}
    <rect x="300" y="1150" width="480" height="12" fill="#9a6539"/></svg>
  <div style="position:absolute;top:24px;left:26px;direction:ltr;font-family:Heebo,sans-serif;font-weight:700;font-size:30px;color:{IVORY}"><span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#e23b2e;margin-right:10px;vertical-align:-1px"></span>REC</div>
</div>
{die("s11-dA", 6, 452, 1176, 70)}{die("s11-dB", 6, 548, 1182, 70)}
""")

# 12. End card
card("s12", 52.5, 6.25, f"""
<svg class="art" style="left:0;top:0;width:1080px;height:1920px;opacity:.16" viewBox="0 0 1080 1920" data-layout-ignore>
  <path d="M0 980 L180 700 L300 840 L470 560 L640 820 L760 680 L1080 980 L1080 1920 L0 1920 Z" fill="{GOLD}"/></svg>
{logo_svg("s12-logo", 330, 150, 420)}
{die("s12-dA", 6, 418, 712, 110)}{die("s12-dB", 6, 552, 718, 110)}
<div class="h" style="top:862px;font-size:96px">הטילו את הקוביות</div>
<div class="sub" style="top:978px;font-size:54px">האפי האוור · <span class="ltr">16:00–18:00</span></div>
<div style="position:absolute;left:0;right:0;top:1064px;text-align:center"><span style="display:inline-block;padding:10px 54px;border:3px solid {GOLD};border-radius:999px;font-family:Heebo,sans-serif;font-weight:700;font-size:48px;color:{IVORY}">הזמינו שולחן</span></div>
<div style="position:absolute;left:96px;right:96px;top:1160px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:40px;color:#ddd2c0">אחוזה 124, רעננה · <span class="ltr">@[instagram]</span></div>
<div style="position:absolute;left:80px;right:80px;top:1236px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:34px;line-height:1.3;color:{GOLD}">בכפוף לתקנון. את התקנון המלא אפשר לבקש מהמלצר.</div>
""", js="""tl.set("#s12-dA", { rotation: -10 }, 0); tl.set("#s12-dB", { rotation: 8 }, 0);""")

TOTAL = 58.75


def composition(c):
    ids = []
    for chunk in c["body"].split('<div id="')[1:]:
        id_, rest = chunk.split('"', 1)
        if rest.startswith(' class="die"') or rest.startswith(' class="pdie"'):
            ids.append("#" + id_)
    mount = f"DiceKit.mount({ids!r});".replace("'", '"') if ids else ""
    return f"""<template>
  <style>{FONTS}{BASE_CSS}{c["css"]}</style>
  <div id="root" data-composition-id="{c["id"]}" data-width="1080" data-height="1920" dir="rtl" lang="he">
{c["body"]}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      {mount}
      {c["js"]}
      window.__timelines["{c["id"]}"] = tl;
    }})();
  </script>
</template>
"""


def index():
    hosts = "\n".join(
        f'      <div id="{c["id"]}" style="z-index:{i + 1}" data-composition-id="{c["id"]}" data-composition-src="compositions/{c["id"]}.html" '
        f'data-start="{c["start"]}" data-duration="{c["dur"]}" data-track-index="{i + 1}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
        for i, c in enumerate(CARDS))
    return f"""<!doctype html>
<html lang="he" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <script src="assets/dice-kit.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {INK}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <!-- Generated by build.py: 14 finished Noir & Or cards, Hebrew only. Edit build.py, not this file. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="24">
{hosts}
      <div id="frame" style="z-index:50" data-composition-id="frame" data-composition-src="compositions/frame.html" data-start="0" data-duration="{TOTAL}" data-track-index="20" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


FRAME = f"""<template>
  <style>
    @font-face {{ font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-latin.woff2') format('woff2'); }}
    @font-face {{ font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-hebrew.woff2') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+FB1D-FB4F; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #frame-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    #frame-legal {{ position: absolute; left: 0; right: 0; top: 1814px; text-align: center; direction: rtl; }}
    #frame-legal span {{ display: inline-block; padding: 4px 22px; border-radius: 999px; background: rgba(11,9,7,.72);
      font-family: "Heebo", sans-serif; font-weight: 500; font-size: 28px; color: {GOLD_HI}; }}
  </style>
  <div id="root" data-composition-id="frame" data-width="1080" data-height="1920">
    <!-- The posters' double gold rule and the house-rules note, on every card from the first frame -->
    <svg id="frame-svg" viewBox="0 0 1080 1920" data-layout-ignore>
      <rect x="24" y="24" width="1032" height="1872" fill="none" stroke="{GOLD}" stroke-width="2"/>
      <rect x="33" y="33" width="1014" height="1854" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-width="1"/>
    </svg>
    <div id="frame-legal" data-layout-allow-caption-zone><span>*בכפוף לתקנון</span></div>
  </div>
  <script>
    window.__timelines["frame"] = gsap.timeline({{ paused: true }});
  </script>
</template>
"""

if __name__ == "__main__":
    assert abs(sum(c["dur"] for c in CARDS) - TOTAL) < 1e-6, "cards must fill the film"
    for c in CARDS:
        (ROOT / "compositions" / f'{c["id"]}.html').write_text(composition(c))
    (ROOT / "compositions" / "frame.html").write_text(FRAME)
    (ROOT / "index.html").write_text(index())
    print(f"built {len(CARDS)} cards, {TOTAL}s")
