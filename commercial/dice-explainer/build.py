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
.foil {{ background: linear-gradient(100deg, #a8814a 0%, #e9c98a 30%, #c9a36b 42%, #fff1c9 50%, #c9a36b 58%, #e9c98a 70%, #a8814a 100%);
  background-size: 300% 100%; background-position: 100% 0; -webkit-background-clip: text; background-clip: text; color: transparent; }}
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
    """The thrower's right hand: a real 3D render (tools/props.html) in three poses (fist, release, open), all stacked
    here; DiceKit.pose() switches between them on the timeline. Navy blazer sleeve, white cuff, like the man in img 1."""
    imgs = "".join(
        f'<img class="pose-{n}" src="assets/img/hand-{n}.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;opacity:{1 if n == pose else 0}">'
        for n in ("fist", "release", "open"))
    return f'<div id="{id_}" class="art" style="left:{x}px;top:{y}px;width:{w}px;height:{w*1.6:.0f}px" data-layout-ignore>{imgs}</div>'


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
{hand_svg("s1-hand", 330, 1190, 420, "fist")}
""", js="""tl.set("#s1-dA", { rotation: -18 }, 0); tl.set("#s1-dB", { rotation: 24 }, 0); tl.set("#s1-hand", { rotation: -10 }, 0);""")

# 2. The brand and the name
card("s2", 2.5, 3.75, f"""
{logo_svg("s2-logo", 300, 160, 480)}
<div id="s2-jp" style="position:absolute;right:86px;top:230px;font-family:Shippori,serif;font-weight:800;font-size:56px;letter-spacing:.16em;color:{GOLD};writing-mode:vertical-rl">運試し</div>
<div id="s2-badge" style="position:absolute;left:84px;top:600px;width:170px;height:170px;border-radius:50%;border:2px solid {GOLD};background:{INK};display:grid;place-items:center;font-family:'Frank Ruhl',serif;font-weight:800;font-size:58px;color:{GOLD_HI}">חדש</div>
<div class="kick" style="top:836px;font-size:46px">המשחק הגדול</div>
<div class="h foil" id="s2-title" style="top:906px;font-size:104px">הטילו את הקוביות</div>
{die("s2-dA", 6, 378, 1080, 140)}{die("s2-dB", 6, 560, 1092, 140)}
<div id="s2-seal" style="position:absolute;left:502px;top:1262px;width:76px;height:76px;border-radius:4px;background:{RED};color:{IVORY};display:grid;place-items:center;font-family:Shippori,serif;font-weight:800;font-size:48px">運</div>
""", js="""tl.set("#s2-badge", { rotation: -12 }, 0); tl.set("#s2-dA", { rotation: -14 }, 0); tl.set("#s2-dB", { rotation: 9 }, 0);""")

# 3a. When: happy hour, 16:00-18:00. A gold dress-watch dial: the hour hand sweeps 4 -> 6 o'clock across the lit
# happy-hour sector while, in the aperture above the pivot, the red sun sets behind ink mountains.
import math
CX, CY = 540, 990


def polar(r, deg):  # deg clockwise from 12 o'clock
    a = math.radians(deg - 90)
    return CX + r * math.cos(a), CY + r * math.sin(a)


GUILLOCHE = "".join(f'<line x1="{CX}" y1="{CY}" x2="{polar(318, d)[0]:.1f}" y2="{polar(318, d)[1]:.1f}"/>' for d in range(0, 360, 3))
INDICES = "".join(
    (f'<line x1="{polar(296, d)[0]:.1f}" y1="{polar(296, d)[1]:.1f}" x2="{polar(258 if d % 90 == 0 else 270, d)[0]:.1f}" y2="{polar(258 if d % 90 == 0 else 270, d)[1]:.1f}" '
     f'stroke-width="{9 if d % 90 == 0 else 5}"/>')
    for d in range(0, 360, 30))
MINUTES = "".join(f'<circle cx="{polar(306, d)[0]:.1f}" cy="{polar(306, d)[1]:.1f}" r="2.2"/>' for d in range(0, 360, 6) if d % 30)
SECTOR = (f'M{CX} {CY} L{polar(318, 120)[0]:.1f} {polar(318, 120)[1]:.1f} A318 318 0 0 1 {polar(318, 180)[0]:.1f} {polar(318, 180)[1]:.1f} Z')
L16, L18 = polar(232, 120), polar(232, 180)
card("s3a", 6.25, 3.75, f"""
<div class="h foil" id="s3a-title" style="top:206px;font-size:128px">האפי האוור</div>
<div class="big" style="top:356px;font-size:126px;color:{IVORY}"><span class="ltr">16:00–18:00</span></div>
<div class="sub" style="top:500px;font-size:56px">בואו בין ארבע לשש</div>
<svg id="s3a-watch" class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <defs>
    <linearGradient id="s3a-bezel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e2a8"/><stop offset=".35" stop-color="#c9a36b"/><stop offset=".55" stop-color="#8a6534"/><stop offset=".8" stop-color="#e7c98a"/><stop offset="1" stop-color="#a8814a"/></linearGradient>
    <radialGradient id="s3a-face" cx=".5" cy=".42" r=".7"><stop offset="0" stop-color="#2a1d12"/><stop offset=".7" stop-color="#140f0b"/><stop offset="1" stop-color="#0b0907"/></radialGradient>
    <linearGradient id="s3a-sky" x1="0" y1="0" x2="0" y2="1"><stop id="s3a-skytop" offset="0" stop-color="#f3c66f"/><stop id="s3a-skybot" offset="1" stop-color="#e98b3a"/></linearGradient>
    <clipPath id="s3a-ap"><circle cx="{CX}" cy="{CY - 150}" r="104"/></clipPath>
    <linearGradient id="s3a-hand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f6e2a8"/><stop offset=".5" stop-color="#c9a36b"/><stop offset="1" stop-color="#8a6534"/></linearGradient>
  </defs>
  <circle cx="{CX}" cy="{CY + 14}" r="352" fill="#000" opacity=".55"/>
  <circle cx="{CX}" cy="{CY}" r="350" fill="url(#s3a-bezel)"/>
  <circle cx="{CX}" cy="{CY}" r="330" fill="#1a130d"/>
  <circle cx="{CX}" cy="{CY}" r="320" fill="url(#s3a-face)"/>
  <g stroke="{GOLD}" stroke-opacity=".10" stroke-width="1.2">{GUILLOCHE}</g>
  <path d="{SECTOR}" fill="{GOLD}" opacity=".26"/>
  <path d="M{polar(312, 120)[0]:.1f} {polar(312, 120)[1]:.1f} A312 312 0 0 1 {polar(312, 180)[0]:.1f} {polar(312, 180)[1]:.1f}" fill="none" stroke="{GOLD_HI}" stroke-width="10" stroke-linecap="round"/>
  <g stroke="{GOLD_HI}" stroke-linecap="round">{INDICES}</g>
  <g fill="{GOLD}">{MINUTES}</g>
  <g fill="{GOLD_HI}" font-family="Frank Ruhl, serif" font-weight="800" font-size="44" text-anchor="middle" direction="ltr">
    <text x="{L16[0]:.0f}" y="{L16[1] + 15:.0f}">16</text><text x="{L18[0]:.0f}" y="{L18[1] + 15:.0f}">18</text></g>
  <g clip-path="url(#s3a-ap)">
    <rect x="{CX - 110}" y="{CY - 260}" width="220" height="220" fill="url(#s3a-sky)"/>
    <circle id="s3a-sun" cx="{CX}" cy="{CY - 170}" r="44" fill="{RED}"/>
    <path d="M{CX - 110} {CY - 104} L{CX - 60} {CY - 150} L{CX - 30} {CY - 126} L{CX + 14} {CY - 172} L{CX + 70} {CY - 118} L{CX + 110} {CY - 140} L{CX + 110} {CY - 40} L{CX - 110} {CY - 40} Z" fill="#120d0a"/>
    <path d="M{CX - 110} {CY - 84} L{CX - 40} {CY - 118} L{CX + 30} {CY - 96} L{CX + 110} {CY - 112} L{CX + 110} {CY - 40} L{CX - 110} {CY - 40} Z" fill="#070504"/>
  </g>
  <circle cx="{CX}" cy="{CY - 150}" r="104" fill="none" stroke="url(#s3a-bezel)" stroke-width="7"/>
  <g id="s3a-min"><path d="M{CX - 5} {CY + 34} L{CX} {CY - 296} L{CX + 5} {CY + 34} Z" fill="url(#s3a-hand)"/></g>
  <g id="s3a-hr"><path d="M{CX} {CY + 40} L{CX - 16} {CY - 40} L{CX} {CY - 206} L{CX + 16} {CY - 40} Z" fill="url(#s3a-hand)" stroke="#5a4020" stroke-width="2"/>
    <circle cx="{CX}" cy="{CY - 120}" r="9" fill="{INK}" stroke="{GOLD_HI}" stroke-width="3"/></g>
  <circle cx="{CX}" cy="{CY}" r="20" fill="url(#s3a-bezel)"/><circle cx="{CX}" cy="{CY}" r="7" fill="{INK}"/>
  <path id="s3a-glint" d="M{CX - 300} {CY - 160} A350 350 0 0 1 {CX - 120} {CY - 330}" fill="none" stroke="#fff6dc" stroke-width="6" stroke-linecap="round" opacity=".55"/>
</svg>
""", js="""
tl.fromTo("#s3a-hr", { rotation: 120, svgOrigin: "540 990" }, { rotation: 180, svgOrigin: "540 990", duration: 3.75, ease: "power1.inOut" }, 0);
tl.fromTo("#s3a-min", { rotation: 0, svgOrigin: "540 990" }, { rotation: 720, svgOrigin: "540 990", duration: 3.75, ease: "power1.inOut" }, 0);
tl.fromTo("#s3a-sun", { attr: { cy: 820 } }, { attr: { cy: 900 }, duration: 3.75, ease: "power1.in" }, 0);
tl.fromTo("#s3a-skytop", { attr: { "stop-color": "#f3c66f" } }, { attr: { "stop-color": "#c0492f" }, duration: 3.75, ease: "none" }, 0);
tl.fromTo("#s3a-skybot", { attr: { "stop-color": "#e98b3a" } }, { attr: { "stop-color": "#4a1a1a" }, duration: 3.75, ease: "none" }, 0);
tl.fromTo("#s3a-glint", { rotation: 0, svgOrigin: "540 990", opacity: 0 }, { rotation: 300, svgOrigin: "540 990", opacity: .55, duration: 1.6, ease: "power2.inOut" }, 0.4);
tl.to("#s3a-glint", { opacity: 0, duration: 0.3, ease: "power1.in" }, 2.0);
tl.fromTo("#s3a-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }, 0.2);
""")

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
<div class="big foil" id="s4-x1" style="top:470px;font-size:400px"><span class="ltr">×1</span></div>
<div class="sub" style="top:900px;font-size:56px">ניסיון אחד ויחיד לכל השולחן</div>
{die("s4-dA", 4, 300, 1030, 220)}{die("s4-dB", 2, 560, 1040, 220)}
""", js="""tl.set("#s4-dA", { rotation: -12 }, 0); tl.set("#s4-dB", { rotation: 10 }, 0);""")

# 5. Rule 3: one player. A Higgsfield still (assets/hf/S5.png): the friends point at the man holding the dice.
card("s5", 17.5, 3.75, f"""
<div class="num" style="top:196px">3</div>
<div class="h" style="top:300px;font-size:128px">שחקן אחד</div>
<div class="sub" style="top:452px;font-size:56px">רק אחד מטיל, בשביל כולם</div>
<div style="position:absolute;left:90px;top:560px;width:900px;height:1080px;border-radius:36px;overflow:hidden;box-shadow:inset 0 0 0 4px {GOLD}, 0 24px 50px rgba(0,0,0,.55)">
  <img id="s5-img" src="assets/hf/S5.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%">
  <div style="position:absolute;inset:0;border-radius:36px;box-shadow:inset 0 0 0 4px {GOLD}"></div>
</div>
""")

# 6a. Rule 4: the throw that doesn't count
MISS_PATHS = f"""<svg class="art" style="left:0;top:0;width:1000px;height:2600px" viewBox="0 0 1000 2600" data-layout-ignore>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <polyline class="s6a-miss" points="430,2350 400,128 362,520" stroke="{IVORY}" stroke-width="7" stroke-dasharray="2 22" opacity=".85"/>
    <polyline class="s6a-miss" points="590,2380 565,905 575,830" stroke="{IVORY}" stroke-width="7" stroke-dasharray="2 22" opacity=".85"/>
    <circle class="s6a-miss" cx="575" cy="830" r="118" stroke="{RED}" stroke-width="10"/></g></svg>"""
card("s6a", 21.25, 3.75, f"""
<div id="s6a-all" style="position:absolute;inset:0;background:radial-gradient(ellipse 90% 30% at 50% 18%, #22150d 0%, {INK} 75%)">
{felt("s6a", 4, 2, MISS_PATHS)}
</div>
<div class="num" style="top:176px">4</div>
<div class="h" style="top:276px;font-size:108px">ההטלה המושלמת</div>
<div class="kick" style="top:420px;font-size:46px;letter-spacing:.04em;font-weight:700">הקיר שממול ⌄</div>
{stamp("s6a-x", "✕&nbsp; לא נחשב", 1040, "#e0574b", -5)}
<div class="h" id="s6a-again" style="top:1190px;font-size:76px;color:{GOLD_HI}">מטילים שוב!</div>
{hand_svg("s6a-hand", 360, 1480, 360, "fist")}
""", css=FELT_CSS, js=place("s6a", 362, 520, 575, 830))

# 6b. Rule 4: the perfect throw
OK_PATHS = f"""<svg class="art" style="left:0;top:0;width:1000px;height:2600px" viewBox="0 0 1000 2600" data-layout-ignore>
  <g fill="none" stroke="{GOLD_HI}" stroke-opacity=".8" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    <path id="s6b-pa" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1.1" d="M430 2350 L380 128 L330 700"/><path id="s6b-pb" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1.1" d="M590 2380 L610 128 L680 820"/></g></svg>"""
card("s6b", 25.0, 6.25, f"""
<div id="s6b-all" style="position:absolute;inset:0;background:radial-gradient(ellipse 90% 30% at 50% 18%, #22150d 0%, {INK} 75%)">
{felt("s6b", 3, 5, OK_PATHS)}
</div>
<div class="num" style="top:176px">4</div>
<div class="h foil" id="s6b-title" style="top:276px;font-size:108px">ההטלה המושלמת</div>
<div class="sub" style="top:410px;font-size:50px">שתי הקוביות חייבות לפגוע בקיר</div>
<div id="s6b-glow" style="position:absolute;left:330px;top:1080px;width:420px;height:300px;border-radius:50%;background:radial-gradient(ellipse at 50% 50%, rgba(226,197,144,.45) 0%, rgba(226,197,144,0) 70%);opacity:0"></div>
<svg id="s6b-ok" class="art" style="left:465px;top:1150px;width:150px;height:150px" viewBox="0 0 140 140" data-layout-ignore>
  <circle cx="70" cy="70" r="62" fill="{INK}" stroke="{GOLD}" stroke-width="5"/>
  <path d="M40 72 L62 94 L102 50" fill="none" stroke="{GOLD_HI}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg>
{hand_svg("s6b-hand", 360, 1480, 360, "fist")}
""", css=FELT_CSS, js=place("s6b", 330, 700, 680, 820))

# 7. Prize: double 1-2-3, 50% off
card("s7", 31.25, 5.0, f"""
<div class="h" style="top:206px;font-size:110px">דאבל 1 · 2 · 3</div>
{die("s7-dA", 3, 392, 360, 130)}{die("s7-dB", 3, 558, 360, 130)}
<div class="big foil" id="s7-pct" style="top:540px;font-size:300px"><span class="ltr">−50%*</span></div>
<div class="sub" style="top:852px;font-size:58px">על כל החשבון של השולחן</div>
<img id="s7-rc" class="art" src="assets/img/receipt.png" alt="" style="left:325px;top:930px;width:430px;height:auto">
""", js="""tl.set("#s7-rc", { rotation: -3 }, 0); tl.set("#s7-dA", { rotation: -8 }, 0); tl.set("#s7-dB", { rotation: 7 }, 0);""")

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
<svg id="s8-burst" class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore><g id="s8-leaf">{LEAF}</g><g id="s8-petals">{PETALS}</g></svg>
<div id="s8-ribbon" style="position:absolute;left:250px;top:196px;width:580px;height:118px;background:{RED};clip-path:polygon(0 0, 100% 0, 94% 50%, 100% 100%, 0 100%, 6% 50%);display:grid;place-items:center;
  font-family:'Frank Ruhl',serif;font-weight:900;font-size:76px;color:{IVORY};line-height:1">ג'קפוט!</div>
<div class="h" style="top:348px;font-size:100px;color:#14110e">דאבל 4 · 5 · 6</div>
<div class="big" style="top:476px;font-size:320px;color:#14110e"><span class="ltr">100%*</span></div>
<div class="h" id="s8-title" style="top:808px;font-size:84px;color:#14110e;background:linear-gradient(100deg,#14110e 0%,#14110e 42%,#7a2a20 50%,#14110e 58%,#14110e 100%);background-size:300% 100%;background-position:100% 0;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">כל הארוחה עלינו</div>
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
<div class="h foil" id="s10-title" style="top:240px;font-size:132px">השירות</div>
<div class="sub" style="top:416px;font-size:62px">הטיפ לא כלול בהטבה</div>
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <ellipse cx="540" cy="1080" rx="300" ry="118" fill="#120e0b" stroke="{GOLD}" stroke-width="5"/>
  <ellipse cx="540" cy="1074" rx="250" ry="88" fill="#1d1612" stroke="rgba(201,163,107,.5)" stroke-width="2"/>
  {''.join(f'<image href="assets/img/coin.png" x="{x - 100}" y="{y - 80}" width="200" height="150"/>' for x, y in [(470, 1070), (600, 1084)])}
  <g id="s10-drop"><g id="s10-coin"><image href="assets/img/coin.png" x="440" y="966" width="200" height="150"/></g></g>
  <path id="s10-glint" d="M500 1036 L560 1036" stroke="#fff6dc" stroke-width="6" stroke-linecap="round" opacity="0"/>
</svg>
""")

# 11. Smile, you're on camera. The winners still (assets/hf/S11.png) inside the phone, a punch-in on each flash.
card("s11", 47.5, 5.0, f"""
<div class="h" style="top:200px;font-size:110px">חייכו,<br>אתם מצולמים!</div>
<div class="sub" style="top:446px;font-size:52px">רגעי הזכייה עולים לרשתות שלנו</div>
<div style="position:absolute;left:225px;top:556px;width:630px;height:1100px;border-radius:64px;background:#0f0d0c;box-shadow:inset 0 0 0 4px {GOLD}, 0 24px 50px rgba(0,0,0,.6)"></div>
<div style="position:absolute;left:247px;top:592px;width:586px;height:1028px;border-radius:44px;overflow:hidden;background:radial-gradient(ellipse 80% 60% at 50% 60%, #4a2c18 0%, #1c120c 80%)">
  <img id="s11-img" src="assets/hf/S11.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">
  <div id="s11-flash" style="position:absolute;inset:0;background:#fff8e8;opacity:0"></div>
  <div style="position:absolute;top:24px;left:26px;direction:ltr;font-family:Heebo,sans-serif;font-weight:700;font-size:30px;color:{IVORY}"><span id="s11-dot" style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#e23b2e;margin-right:10px;vertical-align:-1px"></span>REC</div>
</div>
""")

# 12. End card
card("s12", 52.5, 6.25, f"""
<svg class="art" style="left:0;top:0;width:1080px;height:1920px;opacity:.16" viewBox="0 0 1080 1920" data-layout-ignore>
  <path d="M0 980 L180 700 L300 840 L470 560 L640 820 L760 680 L1080 980 L1080 1920 L0 1920 Z" fill="{GOLD}"/></svg>
{logo_svg("s12-logo", 330, 150, 420)}
{die("s12-dA", 6, 418, 712, 110)}{die("s12-dB", 6, 552, 718, 110)}
<div class="h foil" id="s12-title" style="top:862px;font-size:96px">הטילו את הקוביות</div>
<div class="sub" style="top:978px;font-size:54px">האפי האוור · <span class="ltr">16:00–18:00</span></div>
<div style="position:absolute;left:0;right:0;top:1064px;text-align:center"><span style="display:inline-block;padding:10px 54px;border:3px solid {GOLD};border-radius:999px;font-family:Heebo,sans-serif;font-weight:700;font-size:48px;color:{IVORY}">הזמינו שולחן</span></div>
<div style="position:absolute;left:96px;right:96px;top:1160px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:40px;color:#ddd2c0">אחוזה 124, רעננה · <span class="ltr">@[instagram]</span></div>
<div style="position:absolute;left:80px;right:80px;top:1236px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:34px;line-height:1.3;color:{GOLD}">בכפוף לתקנון. את התקנון המלא אפשר לבקש מהמלצר.</div>
{hand_svg("s12-hand", 640, 1380, 340, "fist")}
""", js="""tl.set("#s12-dA", { rotation: -10 }, 0); tl.set("#s12-dB", { rotation: 8 }, 0);""")

# ---------- motion: only the action moves ----------
MOTION = {
"s1": """
DiceKit.pose(tl, "#s1-hand", "fist", 0); DiceKit.pose(tl, "#s1-hand", "release", 0.34); DiceKit.pose(tl, "#s1-hand", "open", 0.46);
tl.fromTo("#s1-hand", { y: 160, rotation: -4 }, { y: 0, rotation: -14, duration: 0.42, ease: "power3.out" }, 0);
tl.to("#s1-hand", { y: 520, rotation: -24, duration: 1.2, ease: "power2.in" }, 0.9);
tl.fromTo("#s1-dA", { x: 200, y: 430, scale: 0.28, rotation: -120 }, { x: 0, y: 0, scale: 1, rotation: -18, duration: 1.1, ease: "power3.out" }, 0.34);
tl.fromTo("#s1-dB", { x: -190, y: 330, scale: 0.28, rotation: 140 }, { x: 0, y: 0, scale: 1, rotation: 24, duration: 1.15, ease: "power3.out" }, 0.38);
tl.to("#s1-dA", { x: -120, y: -60, scale: 1.55, rotation: -40, duration: 1.06, ease: "power1.in" }, 1.44);
tl.to("#s1-dB", { x: 120, y: 40, scale: 1.55, rotation: 50, duration: 0.97, ease: "power1.in" }, 1.53);
DiceKit.tumble(tl, "#s1-dA", 0.34, 1.3, 6, 1 / 12, 0); DiceKit.tumble(tl, "#s1-dB", 0.38, 1.34, 5, 1 / 12, 3);
""",
"s2": """
tl.fromTo("#s2-dA", { y: -980, rotation: -260 }, { y: 0, rotation: -14, duration: 0.95, ease: "bounce.out" }, 0);
tl.fromTo("#s2-dB", { y: -1040, rotation: 300 }, { y: 0, rotation: 9, duration: 1.0, ease: "bounce.out" }, 0.06);
DiceKit.tumble(tl, "#s2-dA", 0, 0.6, 6, 1 / 12, 2); DiceKit.tumble(tl, "#s2-dB", 0.06, 0.66, 6, 1 / 12, 4);
tl.fromTo("#s2-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.5, ease: "power2.inOut" }, 1.1);
""",
"s3b": """
tl.fromTo(["#s3b-folder", "#s3b-hand"], { x: 760 }, { x: 0, duration: 1.0, ease: "power3.out" }, 0);
tl.to("#s3b-hand", { x: 760, duration: 0.7, ease: "power2.in" }, 1.55);
""",
"s4": """
tl.fromTo("#s4-dA", { rotation: -12 }, { rotation: 78, duration: 3.75, ease: "none" }, 0);
tl.fromTo("#s4-dB", { rotation: 10 }, { rotation: -80, duration: 3.75, ease: "none" }, 0);
tl.fromTo("#s4-x1", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.6, ease: "power2.inOut" }, 0.3);
""",
"s5": """
tl.fromTo("#s5-img", { scale: 1, transformOrigin: "47% 30%" }, { scale: 1.12, transformOrigin: "47% 30%", duration: 3.75, ease: "power1.inOut" }, 0);
""",
"s6a": """
DiceKit.pose(tl, "#s6a-hand", "fist", 0); DiceKit.pose(tl, "#s6a-hand", "release", 0.3); DiceKit.pose(tl, "#s6a-hand", "open", 0.4);
tl.fromTo("#s6a-hand", { y: 120 }, { y: -40, duration: 0.4, ease: "power3.out" }, 0);
tl.to("#s6a-hand", { y: 520, duration: 0.9, ease: "power2.in" }, 0.75);
tl.fromTo(["#s6a-dA", "#s6a-shA"], { x: 430, y: 2350 }, { x: 400, y: 128, duration: 0.9, ease: "power1.out" }, 0.3);
tl.to(["#s6a-dA", "#s6a-shA"], { x: 362, y: 520, duration: 0.6, ease: "expo.out" }, 1.2);
tl.fromTo("#s6a-dA", { z: 0 }, { z: 240, duration: 0.42, ease: "power2.out" }, 0.3); tl.to("#s6a-dA", { z: 0, duration: 0.48, ease: "power2.in" }, 0.72);
tl.fromTo(["#s6a-dB", "#s6a-shB"], { x: 590, y: 2380 }, { x: 565, y: 905, duration: 0.85, ease: "power2.out" }, 0.3);
tl.to(["#s6a-dB", "#s6a-shB"], { x: 575, y: 830, duration: 0.35, ease: "power2.out" }, 1.15);
tl.fromTo("#s6a-dB", { z: 0 }, { z: 190, duration: 0.36, ease: "power2.out" }, 0.3); tl.to("#s6a-dB", { z: 0, duration: 0.48, ease: "power2.in" }, 0.66);
tl.fromTo("#s6a-dA", { rotation: 0 }, { rotation: 600, duration: 1.5, ease: "power2.out" }, 0.3);
tl.fromTo("#s6a-dB", { rotation: 0 }, { rotation: -450, duration: 1.2, ease: "power2.out" }, 0.3);
DiceKit.tumble(tl, "#s6a-dA", 0.3, 1.6, 4, 1 / 12, 0); DiceKit.tumble(tl, "#s6a-dB", 0.3, 1.3, 2, 1 / 12, 2);
tl.fromTo(".s6a-miss", { opacity: 0 }, { opacity: 0.85, duration: 0.2, ease: "power1.out" }, 1.75);
tl.fromTo("#s6a-x", { opacity: 0, scale: 1.7 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }, 1.95);
tl.fromTo("#s6a-again", { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }, 2.6);
""",
"s6b": """
DiceKit.pose(tl, "#s6b-hand", "fist", 0); DiceKit.pose(tl, "#s6b-hand", "release", 0.3); DiceKit.pose(tl, "#s6b-hand", "open", 0.4);
tl.fromTo("#s6b-hand", { y: 120 }, { y: -40, duration: 0.4, ease: "power3.out" }, 0);
tl.to("#s6b-hand", { y: 520, duration: 0.9, ease: "power2.in" }, 0.8);
tl.fromTo(["#s6b-dA", "#s6b-shA"], { x: 430, y: 2350 }, { x: 380, y: 128, duration: 0.95, ease: "power1.out" }, 0.3);
tl.to(["#s6b-dA", "#s6b-shA"], { x: 330, y: 700, duration: 0.75, ease: "expo.out" }, 1.25);
tl.fromTo("#s6b-dA", { z: 0 }, { z: 250, duration: 0.45, ease: "power2.out" }, 0.3); tl.to("#s6b-dA", { z: 0, duration: 0.5, ease: "power2.in" }, 0.75);
tl.fromTo(["#s6b-dB", "#s6b-shB"], { x: 590, y: 2380 }, { x: 610, y: 128, duration: 1.575, ease: "power1.out" }, 0.3);
tl.to(["#s6b-dB", "#s6b-shB"], { x: 680, y: 820, duration: 0.8, ease: "expo.out" }, 1.875);
tl.fromTo("#s6b-dB", { z: 0 }, { z: 220, duration: 0.7, ease: "power2.out" }, 0.3); tl.to("#s6b-dB", { z: 0, duration: 0.875, ease: "power2.in" }, 1.0);
tl.fromTo("#s6b-dA", { rotation: 0 }, { rotation: 640, duration: 1.7, ease: "power2.out" }, 0.3);
tl.fromTo("#s6b-dB", { rotation: 0 }, { rotation: -700, duration: 2.3, ease: "power2.out" }, 0.3);
DiceKit.tumble(tl, "#s6b-dA", 0.3, 1.8, 3, 1 / 12, 1); DiceKit.tumble(tl, "#s6b-dB", 0.3, 2.4, 5, 1 / 12, 4);
tl.fromTo("#s6b-pa", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0.25, duration: 0.95, ease: "power1.out" }, 0.3);
tl.to("#s6b-pa", { strokeDashoffset: 0, duration: 0.75, ease: "expo.out" }, 1.25);
tl.fromTo("#s6b-pb", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0.25, duration: 1.575, ease: "power1.out" }, 0.3);
tl.to("#s6b-pb", { strokeDashoffset: 0, duration: 0.8, ease: "expo.out" }, 1.875);
tl.fromTo("#s6b-ok", { opacity: 0, scale: 1.7 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }, 3.0);
tl.fromTo("#s6b-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.8, ease: "power2.inOut" }, 3.4);
tl.fromTo("#s6b-glow", { opacity: 0 }, { opacity: 0.6, duration: 0.6, ease: "power2.out" }, 4.4);
tl.to("#s6b-glow", { opacity: 0.2, duration: 1.0, ease: "power2.inOut" }, 5.0);
""",
"s7": """
for (const [i, f] of [[0, 1], [1, 2], [2, 3]]) {
  DiceKit.setFace(tl, "#s7-dA", f, i * 0.625); DiceKit.setFace(tl, "#s7-dB", f, i * 0.625);
  tl.fromTo(["#s7-dA", "#s7-dB"], { scale: 1.25 }, { scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: i === 0 }, i * 0.625);
}
tl.fromTo("#s7-pct", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }, 2.3);
""",
"s8": """
for (const [i, f] of [[0, 4], [1, 5], [2, 6]]) {
  DiceKit.setFace(tl, "#s8-dA", f, i * 0.625); DiceKit.setFace(tl, "#s8-dB", f, i * 0.625);
  tl.fromTo(["#s8-dA", "#s8-dB"], { scale: 1.25 }, { scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: i === 0 }, i * 0.625);
}
tl.fromTo("#s8-leaf rect", { x: 0, y: 0, opacity: 0, rotation: 0 }, { x: (i) => [-260, 240, -330, 300, 60][i], y: (i) => [-220, -260, 180, 160, 260][i], rotation: (i) => [-60, 70, 90, -80, 40][i], opacity: 0.9, duration: 1.2, ease: "expo.out", svgOrigin: "540 1100" }, 1.3);
tl.fromTo("#s8-petals", { y: -160 }, { y: 260, duration: 5, ease: "none" }, 0);
tl.fromTo("#s8-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }, 2.6);
tl.fromTo("#s8-petals", { opacity: 0.0 }, { opacity: 1, duration: 0.2, ease: "power1.out" }, 1.3);
""",
"s9": """
tl.fromTo("#s9-dA", { x: -560, rotation: -560 }, { x: 0, rotation: -14, duration: 1.1, ease: "expo.out" }, 0);
tl.fromTo("#s9-dB", { x: 560, rotation: 520 }, { x: 0, rotation: 11, duration: 1.15, ease: "expo.out" }, 0.05);
DiceKit.tumble(tl, "#s9-dA", 0, 0.75, 3, 1 / 12, 0); DiceKit.tumble(tl, "#s9-dB", 0.05, 0.8, 5, 1 / 12, 2);
""",
"s10": """
tl.fromTo("#s10-drop", { y: -620 }, { y: 0, duration: 0.7, ease: "power2.in" }, 0.25);
tl.fromTo("#s10-coin", { scaleY: 1, transformOrigin: "50% 100%" }, { scaleY: 0.8, duration: 0.07, ease: "power1.out", yoyo: true, repeat: 1 }, 0.95);
tl.fromTo("#s10-glint", { opacity: 0, x: -60 }, { opacity: 0.9, x: 60, duration: 0.6, ease: "power2.inOut" }, 1.2);
tl.to("#s10-glint", { opacity: 0, duration: 0.25, ease: "power1.in" }, 1.8);
tl.fromTo("#s10-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.5, ease: "power2.inOut" }, 2.0);
""",
"s11": """
tl.fromTo("#s11-flash", { opacity: 0 }, { opacity: 0.9, duration: 0.05, ease: "none" }, 0.625);
tl.to("#s11-flash", { opacity: 0, duration: 0.4, ease: "power2.out" }, 0.68);
tl.fromTo("#s11-img", { scale: 1 }, { scale: 1.07, duration: 0.3, ease: "power2.out" }, 0.66);
tl.to("#s11-img", { scale: 1.02, duration: 2.1, ease: "power1.inOut" }, 0.96);
for (let k = 0; k < 10; k++) tl.set("#s11-dot", { opacity: k % 2 ? 0.15 : 1 }, k * 0.5);
tl.fromTo("#s11-flash", { opacity: 0 }, { opacity: 0.85, duration: 0.05, ease: "none", immediateRender: false }, 3.125);
tl.to("#s11-flash", { opacity: 0, duration: 0.4, ease: "power2.out" }, 3.18);
tl.to("#s11-img", { scale: 1.09, duration: 0.3, ease: "power2.out" }, 3.16);
tl.to("#s11-img", { scale: 1.04, duration: 1.5, ease: "power1.inOut" }, 3.46);
""",
"s12": """
DiceKit.pose(tl, "#s12-hand", "fist", 0); DiceKit.pose(tl, "#s12-hand", "release", 0.32); DiceKit.pose(tl, "#s12-hand", "open", 0.42);
tl.fromTo("#s12-hand", { y: 200, rotation: 8 }, { y: 0, rotation: -6, duration: 0.4, ease: "power3.out" }, 0);
tl.to("#s12-hand", { y: 640, duration: 0.8, ease: "power2.in" }, 0.85);
tl.fromTo("#s12-dA", { x: 300, y: 720, scale: 0.6, rotation: 300 }, { x: 0, y: 0, scale: 1, rotation: -10, duration: 1.0, ease: "power3.out" }, 0.32);
tl.fromTo("#s12-dB", { x: 180, y: 740, scale: 0.6, rotation: -320 }, { x: 0, y: 0, scale: 1, rotation: 8, duration: 1.05, ease: "power3.out" }, 0.36);
DiceKit.tumble(tl, "#s12-dA", 0.32, 1.1, 6, 1 / 12, 1); DiceKit.tumble(tl, "#s12-dB", 0.36, 1.15, 6, 1 / 12, 3);
tl.fromTo("#s12-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.6, ease: "power2.inOut" }, 1.4);
""",
}
for c in CARDS:
    c["js"] += MOTION.get(c["id"], "")

# ---------- sound: effects on the visible actions only (Pixabay, bundled with HyperFrames) ----------
SFX = [  # (file, time in s, volume)
    ("whoosh", 0.36, .8), ("whoosh-cinematic", 1.9, .7), ("click-soft", 3.05, .9), ("click", 3.12, .7),
    ("sparkle", 6.75, .5), ("whoosh-short", 10.05, .7), ("pop", 14.1, .5), ("whoosh-short", 17.65, .6), ("pop", 18.85, .6),
    ("whoosh", 21.55, .8), ("click-soft", 22.4, .9), ("click", 22.47, .9), ("impact-bass-2", 23.22, .8), ("pop", 23.88, .8),
    ("whoosh", 25.55, .8), ("click", 26.27, 1.0), ("click", 26.9, 1.0), ("impact-bass-1", 28.27, .8),
    ("pop", 31.3, .6), ("pop", 31.92, .6), ("pop", 32.55, .6), ("riser", 34.6, .6), ("pop", 36.3, .6), ("pop", 36.92, .6), ("impact-bass-1", 37.55, 1.0), ("sparkle", 37.6, .6),
    ("whoosh-short", 41.3, .7), ("click-soft", 42.1, .9), ("click", 44.72, .9), ("sparkle", 44.98, .5),
    ("click", 48.17, .9), ("click", 50.67, .9), ("whoosh", 52.86, .8), ("click-soft", 53.55, .9), ("impact-bass-1", 54.0, .7), ("sparkle", 54.0, .5),
]

# ---------- the opening: avatars ask for the bill, and the cashier sends them to the dice ----------
INTRO = 9.375  # 15 beats
for c in CARDS:
    c["start"] = round(c["start"] + INTRO, 4)
SFX = [(f, round(t + INTRO, 3), v) for f, t, v in SFX]

def bubble(id_, text, top, size, tail_x, tail_up=False):
    tail = f"left:{tail_x}px;{'top:-22px' if tail_up else 'bottom:-22px'}"
    return (f'<div id="{id_}" style="position:absolute;left:96px;right:96px;top:{top}px;text-align:center">'
            f'<div style="position:relative;display:inline-block;padding:26px 46px 30px;background:{IVORY};border:4px solid {GOLD};border-radius:44px;'
            f'box-shadow:0 18px 40px rgba(0,0,0,.45);font-family:Heebo,sans-serif;font-weight:800;font-size:{size}px;line-height:1.2;color:#14110e">{text}'
            f'<span style="position:absolute;{tail};width:40px;height:40px;background:{IVORY};border-right:4px solid {GOLD};border-bottom:4px solid {GOLD};rotate:{225 if tail_up else 45}deg"></span></div></div>')


# The opening actors are three Higgsfield clips (assets/hf/P1-3-fit.mp4, Kling from the F1-F3 stills) mounted in index();
# p1-p3 are transparent overlays on top (speech bubbles, the "?!", then the felt close-up in code).
OVERLAY_CSS = "#root { background: transparent; }"
INTRO_CARDS = []
INTRO_CARDS.append(dict(id="p1", start=0, dur=3.125, css=OVERLAY_CSS, body=f"""
{bubble("p1-say", "אפשר חשבון?", 1150, 74, 90, tail_up=True)}
""", js="""
tl.fromTo("#p1-say", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.8)" }, 0.55);
"""))
INTRO_CARDS.append(dict(id="p2", start=3.125, dur=3.75, css=OVERLAY_CSS, body=f"""
{bubble("p2-say", "לא, לא, לא…<br>קודם מטילים את הקוביות!", 700, 64, 560, tail_up=True)}
""", js="""
tl.fromTo("#p2-say", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.8)" }, 0.7);
"""))
INTRO_CARDS.append(dict(id="p3", start=6.875, dur=2.5, css=OVERLAY_CSS, body=f"""
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <text id="p3-q1" x="60" y="290" font-family="Frank Ruhl, serif" font-weight="900" font-size="130" fill="#fff4dc" stroke="#c9a36b" stroke-width="4" direction="ltr">?!</text>
  <text id="p3-q2" x="900" y="300" font-family="Frank Ruhl, serif" font-weight="900" font-size="120" fill="#fff4dc" stroke="#c9a36b" stroke-width="4" direction="ltr">?</text>
</svg>
<div id="p3-b" style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 55% at 50% 45%, #2a9a58 0%, #1a6b3c 45%, #0b3a20 100%)">
  {logo_svg("p3-felt-logo", 360, 300, 360, stroke="#d6b26e")}
  {die("p3-dA", 6, 330, 900, 220)}{die("p3-dB", 4, 560, 930, 220)}
  {hand_svg("p3-hand", 340, 1500, 440, "open")}
</div>
""", js="""
tl.fromTo(["#p3-q1", "#p3-q2"], { opacity: 0, scale: 0.4, transformOrigin: "50% 100%" }, { opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)", stagger: 0.08 }, 0.3);
tl.set("#p3-b", { opacity: 0 }, 0); tl.set("#p3-b", { opacity: 1 }, 1.25);
tl.fromTo("#p3-hand", { y: 420 }, { y: -560, duration: 0.42, ease: "power3.out" }, 1.25);
DiceKit.pose(tl, "#p3-hand", "open", 0); DiceKit.pose(tl, "#p3-hand", "release", 1.62); DiceKit.pose(tl, "#p3-hand", "fist", 1.7);
tl.to(["#p3-dA", "#p3-dB"], { scale: 0.3, opacity: 0, duration: 0.1, ease: "power2.in" }, 1.68);
tl.to("#p3-hand", { y: 300, duration: 0.7, ease: "power2.in" }, 1.8);
"""))

# (start, duration, file) of the three opening clips, already fitted to 1080x1920 at 24 fps.
CLIPS = [(0, 3.125, "P1-fit.mp4"), (3.125, 3.75, "P2-fit.mp4"), (6.875, 1.25, "P3-fit.mp4")]
CARDS[:0] = INTRO_CARDS
SFX = [("pop", 0.58, .7), ("click-soft", 3.2, .8), ("pop", 3.83, .8), ("pop", 7.18, .6), ("whoosh-short", 8.13, .6), ("click", 8.58, .8)] + SFX

SFX_LEN = {k: v['duration'] for k, v in __import__('json').load(open(ROOT / 'assets/sfx/manifest.json')).items()}
TOTAL = round(sum(c['dur'] for c in CARDS), 4)


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
    audio = "\n".join(
        f'      <audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}.mp3" data-start="{t}" data-duration="{SFX_LEN[f]}" data-track-index="{40 + i}" data-volume="{v}"></audio>'
        for i, (f, t, v) in enumerate(SFX))
    clips = "\n".join(
        f'      <video id="clip-{k + 1}" class="clip" src="assets/hf/{f}" muted playsinline data-start="{t}" data-duration="{d}" data-track-index="{30 + k}" '
        f'style="z-index:0;position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover"></video>'
        for k, (t, d, f) in enumerate(CLIPS))
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
{clips}
{hosts}
{audio}
      <div id="frame" style="z-index:50" data-composition-id="frame" data-composition-src="compositions/frame.html" data-start="{INTRO}" data-duration="{TOTAL - INTRO}" data-track-index="20" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
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
    <svg id="frame-grain" viewBox="0 0 540 960" preserveAspectRatio="none" data-layout-ignore style="position:absolute;inset:0;width:100%;height:100%;opacity:.13;mix-blend-mode:overlay">
      <filter id="frame-noise"><feTurbulence id="frame-turb" type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="1"/><feColorMatrix type="saturate" values="0"/></filter>
      <rect width="540" height="960" filter="url(#frame-noise)"/>
    </svg>
    <div id="frame-legal" data-layout-allow-caption-zone><span>*בכפוף לתקנון</span></div>
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const turb = document.getElementById("frame-turb");
      for (let k = 0; k < {int(TOTAL * 12)}; k++) tl.set(turb, {{ attr: {{ seed: (k * 7) % 97 + 1 }} }}, k / 12);
      window.__timelines["frame"] = tl;
    }})();
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
