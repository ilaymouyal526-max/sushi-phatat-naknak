#!/usr/bin/env python3
"""Builds the Hebrew dice-game explainer (v6): compositions/*.html and index.html.

Rules that shape this file (see SPEC.md and HANDOFF.md):
  - Every card is a finished Noir & Or poster from its first frame; only the action moves.
  - All times are in beats (96 BPM, 1 beat = 15 frames = 0.625 s). Every cut is hard and on a beat.
  - Throws are simulated here (a tiny physics sim, baked frame by frame), and the same events place the sound
    effects, so picture and sound cannot drift apart.

Edit here, then run `python3 build.py`. Don't hand-edit the generated HTML: the next build overwrites it.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent
FPS, BEAT = 24, 0.625
GOLD, GOLD_HI, IVORY, INK, RED = "#c9a36b", "#e2c590", "#f4ecdf", "#0b0907", "#b8322a"

FONTS = """
@font-face { font-family: "Frank Ruhl"; font-weight: 300 900; font-display: block; src: url('assets/fonts/frankruhl-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Frank Ruhl"; font-weight: 300 900; font-display: block; src: url('assets/fonts/frankruhl-normal-hebrew.woff2') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F; }
@font-face { font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-hebrew.woff2') format('woff2'); unicode-range: U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F; }
@font-face { font-family: "Cormorant"; font-weight: 500 700; font-display: block; src: url('assets/fonts/cormorant-upright-normal-latin.woff2') format('woff2'); }
@font-face { font-family: "Shippori"; font-weight: 800; font-display: block; src: url('assets/fonts/shippori-jp-subset.woff2') format('woff2'); }
"""

# The design system. One type scale, one header pattern, one way to ground an object (a shadow under it).
BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: hidden; direction: rtl; font-variant-numeric: lining-nums;
  background: radial-gradient(ellipse 92% 44% at 50% var(--glow, 54%), rgba(84,50,22,.66) 0%, rgba(84,50,22,0) 72%), url('assets/img/tex-noir.jpg') center / cover no-repeat, {INK}; }}
.h {{ position: absolute; left: 80px; right: 80px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 800; color: {IVORY}; line-height: 1.04;
  text-shadow: 0 3px 0 rgba(0,0,0,.6), 0 16px 34px rgba(0,0,0,.6); }}
.sub {{ position: absolute; left: 90px; right: 90px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 500; color: {GOLD_HI}; line-height: 1.28;
  text-shadow: 0 2px 0 rgba(0,0,0,.55); }}
.kick {{ position: absolute; left: 90px; right: 90px; text-align: center; font-family: "Heebo", sans-serif; font-weight: 500; letter-spacing: .14em; color: {GOLD}; }}
.big {{ position: absolute; left: 40px; right: 40px; text-align: center; font-family: "Frank Ruhl", serif; font-weight: 700; line-height: .9; }}
.foil {{ background: linear-gradient(100deg, #a8814a 0%, #e9c98a 30%, #c9a36b 42%, #fff1c9 50%, #c9a36b 58%, #e9c98a 70%, #a8814a 100%);
  background-size: 300% 100%; background-position: 100% 0; -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: none;
  filter: drop-shadow(0 3px 0 #3a280f) drop-shadow(0 14px 24px rgba(0,0,0,.6)); }}
.ltr {{ direction: ltr; unicode-bidi: isolate; display: inline-block; }}
.rule {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 24px; direction: ltr; }}
.rule b {{ width: 86px; height: 86px; border-radius: 50%; border: 2px solid {GOLD}; display: grid; place-items: center; line-height: 1;
  font-family: "Frank Ruhl", serif; font-weight: 700; font-size: 52px; color: {GOLD_HI};
  background: radial-gradient(circle at 35% 28%, #3a2716 0%, #120c08 70%); box-shadow: inset 0 0 0 5px {INK}, inset 0 0 0 6px rgba(201,163,107,.6), 0 10px 24px rgba(0,0,0,.6); }}
.rule i {{ width: 200px; height: 2px; background: linear-gradient(90deg, rgba(201,163,107,0), {GOLD}); }}
.rule i + b + i {{ background: linear-gradient(90deg, {GOLD}, rgba(201,163,107,0)); }}
.die {{ position: absolute; }}
.shd {{ position: absolute; border-radius: 50%; background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,.72) 0%, rgba(70,4,12,.34) 46%, rgba(0,0,0,0) 70%); }}
.art {{ position: absolute; overflow: visible; }}
.hand {{ position: absolute; transform-origin: 56.6% 43.6%; }}
.hand img {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
"""


# ---------- timing ----------

def fr(t):
    """Snap a time to the film's frame grid."""
    return round(t * FPS) / FPS


def beat(n):
    return n * BEAT


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


def rule(n, top=168):
    """The header of a rule card: the rule's number in a gold medallion between two hairlines."""
    return f'<div class="rule" style="top:{top}px" data-layout-ignore><i></i><b>{n}</b><i></i></div>'


def die(id_, faces, x, y, size, v="a", rot=0):
    """A die centred on (x, y); `size` is the cube's visible width. `faces`: every face it shows, the first one first."""
    faces = faces if isinstance(faces, (list, tuple)) else [faces]
    return (f'<div id="{id_}" class="die" data-faces="{",".join(map(str, faces))}" data-v="{v}" '
            f'style="left:{x - size / 2:.0f}px;top:{y - size / 2:.0f}px;width:{size}px;height:{size}px;rotate:{rot}deg"></div>')


def shadow(id_, x, y, w, opacity=1.0):
    """The soft shadow a die leaves on the surface under it, centred on (x, y)."""
    return f'<div id="{id_}" class="shd" style="left:{x - w / 2:.0f}px;top:{y - w * 0.21:.0f}px;width:{w}px;height:{w * 0.42:.0f}px;opacity:{opacity}" data-layout-ignore></div>'


HAND_POSES = ("open", "release", "fist", "flat")


def hand(id_, x, y, w, pose="open", rot=0):
    """The thrower's right hand (tools/hand.html): all four poses stacked, DiceKit.pose() switches them.
    (x, y) is where the middle of the palm sits; the hand turns about that point."""
    imgs = "".join(f'<img data-pose="{n}" src="assets/img/hand-{n}.png" alt="" style="opacity:{1 if n == pose else 0}">' for n in HAND_POSES)
    return (f'<div id="{id_}" class="hand" style="left:{x - 0.566 * w:.0f}px;top:{y - 0.96 * w:.0f}px;width:{w}px;height:{w * 2.2:.0f}px;rotate:{rot}deg" data-layout-ignore>{imgs}</div>')


def stamp(id_, text, x, y, color, rot, size=68):
    return (f'<div id="{id_}" style="position:absolute;left:0;right:0;top:{y}px;text-align:center" data-layout-ignore>'
            f'<span style="display:inline-block;translate:{x - 540}px 0;padding:12px 44px 14px;border:6px solid {color};border-radius:16px;color:{color};'
            f'font-family:Heebo,sans-serif;font-weight:800;font-size:{size}px;line-height:1.1;background:rgba(11,9,7,.82);rotate:{rot}deg;'
            f'box-shadow:0 14px 30px rgba(0,0,0,.5)">{text}</span></div>')


# ---------- baked motion ----------

def J(x):
    return json.dumps(x, separators=(",", ":"))


def js_bake(sel, t0, keys, rows):
    return f'DiceKit.bake(tl,"{sel}",{t0:.4f},{J(keys)},{J(rows)});\n'


def js_spin(sel, t0, face, ks):
    return f'DiceKit.spin(tl,"{sel}",{t0:.4f},{face},{J(ks)});\n'


def spin_keys(n):
    """Which of the 24 strip frames to show on each of n film frames of a tumble that ends at rest.
    A long tumble loops the fast, blurred first 10 strip frames, then plays the last 14 once: a new image on every
    film frame, and a continuous slow-down into the rest pose."""
    if n <= 1:
        return [23] * n
    if n <= 24:
        return [round(i * 23 / (n - 1)) for i in range(n)]
    return [i % 10 for i in range(n - 14)] + list(range(10, 24))


def r1(v):
    return round(v, 1)


SFX = []  # (card id, time inside the card, file, volume): placed by the same code that moves the picture


def sfx(card_id, t, name, vol):
    SFX.append((card_id, round(t, 3), name, vol))


# ---------- the dice table (cards 6a, 6b) ----------

class Table:
    """The restaurant's dice table (reference/dice_table.jpg): green felt in a walnut tray, the logo on the felt.
    The plane is real CSS 3D (walls standing on the felt). The dice are screen-space sprites; proj() is the same
    camera, so the baked throws land exactly on the drawn felt."""
    PW, PL, LEFT, TOP = 1000, 2600, 40, -530   # the plane, in px, before perspective
    TH, D = math.radians(30), 2500              # tilt and perspective distance
    IN, RIM, WH, C = 88, 44, 120, 172           # felt inset, rim width, wall height, die size on the felt

    @classmethod
    def proj(cls, x, y, z=0.0):
        """Plane point (x, y, height z) -> (screen x, screen y, scale)."""
        X, Y = x - cls.PW / 2, y - cls.PL
        yy = Y * math.cos(cls.TH) - z * math.sin(cls.TH)
        zz = Y * math.sin(cls.TH) + z * math.cos(cls.TH)
        k = cls.D / (cls.D - zz)
        return cls.LEFT + cls.PW / 2 + X * k, cls.TOP + cls.PL + yy * k, k

    CSS = f"""
.tbl {{ position: absolute; left: 40px; top: -530px; width: 1000px; height: 2600px; transform-origin: 50% 100%;
  transform: perspective(2500px) rotateX(30deg); transform-style: preserve-3d; }}
.tbl > div {{ position: absolute; }}
.tbl .felt {{ left: 88px; top: 88px; right: 88px; bottom: 0;
  background: radial-gradient(ellipse 62% 22% at 50% 25%, rgba(255,255,205,.20) 0%, rgba(255,255,205,0) 100%),
    linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 9%, rgba(0,0,0,0) 55%, rgba(0,0,0,.5) 100%),
    linear-gradient(90deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 9%, rgba(0,0,0,0) 91%, rgba(0,0,0,.45) 100%),
    url('assets/img/tex-felt.jpg') 0 0 / 520px 520px; }}
.tbl .wall-far {{ left: 88px; top: -32px; width: 824px; height: 120px; transform-origin: 50% 100%; transform: rotateX(-90deg);
  background: linear-gradient(180deg, rgba(255,255,220,.10) 0%, rgba(0,0,0,.30) 100%), url('assets/img/tex-felt.jpg') 0 0 / 520px 520px; }}
.tbl .wall-l {{ left: -32px; top: 88px; width: 120px; bottom: 0; transform-origin: 100% 50%; transform: rotateY(90deg);
  background: linear-gradient(90deg, rgba(0,0,0,.28) 0%, rgba(0,0,0,.52) 100%), url('assets/img/tex-felt.jpg') 0 0 / 520px 520px; }}
.tbl .wall-r {{ left: 912px; top: 88px; width: 120px; bottom: 0; transform-origin: 0 50%; transform: rotateY(-90deg);
  background: linear-gradient(90deg, rgba(0,0,0,.52) 0%, rgba(0,0,0,.28) 100%), url('assets/img/tex-felt.jpg') 0 0 / 520px 520px; }}
.tbl .rim {{ transform: translateZ(120px); background: url('assets/img/tex-walnut.jpg') 0 0 / 700px 180px; box-shadow: inset 0 0 0 1px rgba(40,20,8,.6); }}
.tbl .rim-far {{ left: 44px; top: 44px; width: 912px; height: 44px; }}
.tbl .rim-l {{ left: 44px; top: 44px; width: 44px; bottom: 0; background: url('assets/img/tex-walnutv.jpg') 0 0 / 180px 700px; }}
.tbl .rim-r {{ left: 912px; top: 44px; width: 44px; bottom: 0; background: url('assets/img/tex-walnutv.jpg') -90px 0 / 180px 700px; }}
.spark {{ position: absolute; width: 150px; height: 150px; margin: -75px 0 0 -75px; border-radius: 50%; opacity: 0;
  background: radial-gradient(circle, rgba(255,246,214,.95) 0%, rgba(233,201,138,.55) 28%, rgba(233,201,138,0) 66%); }}
"""

    @classmethod
    def html(cls, prefix):
        return f"""<div class="tbl" data-layout-allow-overflow data-layout-ignore>
  <div class="felt"></div>
  {logo_svg(prefix + "-felt-logo", 320, 430, 360, stroke="#dcb873", extra='opacity=".92"')}
  <div class="wall-l"></div><div class="wall-r"></div><div class="wall-far"></div>
  <div class="rim rim-l"></div><div class="rim rim-r"></div><div class="rim rim-far"></div>
</div>"""


def throw_sim(start, aim, speed, vz0=850.0):
    """A die thrown down the table: gravity, bounces on the felt, a rebound off the walls, then it rolls to a stop.
    Returns one (x, y, z) per film frame, and the events [(time, kind, strength)]: "floor" and "wall" hits."""
    x, y, z = start
    dx, dy = aim[0] - x, aim[1] - y
    L = math.hypot(dx, dy)
    vx, vy, vz = speed * dx / L, speed * dy / L, vz0
    G, E, MU, ROLL, DT = 5200.0, 0.42, 0.74, 2300.0, 1 / 240
    ymin = Table.IN + Table.C / 2
    xmin, xmax = Table.IN + Table.C / 2, Table.PW - Table.IN - Table.C / 2
    out, ev, t, i = [], [], 0.0, 0
    while t < 5:
        if i % 10 == 0:
            out.append((x, y, z))
        vz -= G * DT
        x, y, z = x + vx * DT, y + vy * DT, z + vz * DT
        if z <= 0:
            z = 0.0
            if vz < -300:
                ev.append((t, "floor", min(1.0, -vz / 1500)))
                vz, vx, vy = -E * vz, vx * MU, vy * MU
            else:
                vz = 0.0
        if z == 0 and vz == 0:
            sp = math.hypot(vx, vy)
            if sp < 12:
                break
            f = max(0.0, sp - ROLL * DT) / sp
            vx, vy = vx * f, vy * f
        if y < ymin and vy < 0:
            y, vy, vx = ymin, -0.5 * vy, vx * 0.8
            ev.append((t, "wall", 1.0))
        if x < xmin and vx < 0:
            x, vx = xmin, -0.5 * vx
        if x > xmax and vx > 0:
            x, vx = xmax, -0.5 * vx
        t += DT
        i += 1
    out.append((x, y, z))
    return out, ev


def tune_throw(start, aim, rest_y, hits_wall):
    """Find the throw speed that leaves the die at rest_y, with or without touching the far wall."""
    best = None
    for speed in range(700, 5200, 15):
        out, ev = throw_sim(start, aim, speed)
        if any(k == "wall" for _, k, _ in ev) != hits_wall:
            continue
        err = abs(out[-1][1] - rest_y)
        if best is None or err < best[0]:
            best = (err, out, ev)
    assert best, "no throw fits"
    return best[1], best[2]


def table_throw(card_id, die_id, face, start, aim, rest_y, hits_wall, wall_at=None, launch=None, vol=1.0):
    """Bake one die's throw on the table. `wall_at`: the time (in the card) its wall hit must land on.
    Returns the JS, the rest point on screen, the wall-hit point on screen, and the time it comes to rest."""
    out, ev = tune_throw(start, aim, rest_y, hits_wall)
    wall = next((t for t, k, _ in ev if k == "wall"), None)
    t0 = fr(wall_at - wall) if wall_at is not None and wall is not None else fr(launch)
    n = len(out)
    rows, srows = [], []
    for x, y, z in out:
        sx, sy, k = Table.proj(x, y, z + Table.C / 2)
        gx, gy, gk = Table.proj(x, y, 0)
        rows.append([r1(sx), r1(sy), round(k, 3), 1])
        srows.append([r1(gx + 10 * gk), r1(gy + 26 * gk), round(gk * (1 + z / 500), 3), round(0.95 / (1 + z / 140), 2)])
    js = js_bake(f"#{die_id}", 0, ["opacity"], [[0]]) + js_bake(f"#{die_id}", t0, ["x", "y", "scale", "opacity"], rows)
    js += js_bake(f"#{die_id}-sh", 0, ["opacity"], [[0]]) + js_bake(f"#{die_id}-sh", t0, ["x", "y", "scale", "opacity"], srows)
    js += js_spin(f"#{die_id}", t0, face, spin_keys(n - 1) + [-1])
    for t, kind, s in ev:
        if kind == "wall":
            sfx(card_id, t0 + t, "click", vol)
        elif s > 0.35:
            sfx(card_id, t0 + t, "click-soft", round(vol * 0.5 * s + 0.2, 2))
    wall_xy = None
    if wall is not None:
        i = min(n - 1, round(wall * FPS))
        wall_xy = Table.proj(out[i][0], Table.IN, Table.C / 2)[:2]
    path = [Table.proj(x, y, 0)[:2] for x, y, _ in out]
    return dict(js=js, t0=t0, rest=tuple(rows[-1][:3]), wall=wall_xy, wall_t=None if wall is None else t0 + wall, rest_t=t0 + (n - 1) / FPS, path=path)


def table_die(die_id, face, v):
    """A die and its shadow for the table cards: both sit at the screen origin and are moved by the baked throw."""
    c = Table.C
    return (f'<div id="{die_id}-sh" class="shd" style="left:{-c * 0.62:.0f}px;top:{-c * 0.26:.0f}px;width:{c * 1.24:.0f}px;height:{c * 0.52:.0f}px" data-layout-ignore></div>',
            f'<div id="{die_id}" class="die" data-faces="{face}" data-v="{v}" style="left:{-c / 2:.0f}px;top:{-c / 2:.0f}px;width:{c}px;height:{c}px" data-layout-allow-overflow></div>')


# ---------- the cards ----------
# Each card: id, length in beats, body HTML, extra CSS, timeline JS.

CARDS = []


def card(id_, beats, body, css="", js=""):
    CARDS.append(dict(id=id_, beats=beats, dur=beat(beats), body=body, css=css, js=js))


# ===== The opening: three Higgsfield clips (mounted in index()), with transparent overlays on top =====

def bubble(id_, text, top, size, tail_x, tail_up=False):
    tail = f"left:{tail_x}px;{'top:-22px' if tail_up else 'bottom:-22px'}"
    return (f'<div id="{id_}" style="position:absolute;left:96px;right:96px;top:{top}px;text-align:center">'
            f'<div style="position:relative;display:inline-block;padding:26px 46px 30px;background:{IVORY};border:4px solid {GOLD};border-radius:44px;'
            f'box-shadow:0 18px 40px rgba(0,0,0,.45), inset 0 0 0 3px {IVORY}, inset 0 0 0 4px rgba(201,163,107,.55);font-family:Heebo,sans-serif;font-weight:800;font-size:{size}px;line-height:1.2;color:#14110e">{text}'
            f'<span style="position:absolute;{tail};width:40px;height:40px;background:{IVORY};border-right:4px solid {GOLD};border-bottom:4px solid {GOLD};rotate:{225 if tail_up else 45}deg"></span></div></div>')


OVERLAY_CSS = "#root { background: transparent; }"

# P1: the couple asks for the bill
card("p1", 5, f"""
{bubble("p1-say", "אפשר חשבון?", 1150, 74, 90, tail_up=True)}
""", css=OVERLAY_CSS, js="""
tl.fromTo("#p1-say", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.8)" }, 0.625 - 0.08);
""")
sfx("p1", 0.6, "pop", .7)

# P2: the chef: first you roll the dice
card("p2", 6, f"""
{bubble("p2-say", "לא, לא, לא…<br>קודם מטילים את הקוביות!", 700, 64, 560, tail_up=True)}
""", css=OVERLAY_CSS, js="""
tl.fromTo("#p2-say", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.8)" }, 0.625 - 0.08);
""")
sfx("p2", 0.08, "click-soft", .8)
sfx("p2", 0.6, "pop", .8)

# P3: the couple is surprised (2 beats of clip), then the felt close-up: the hand scoops the dice (2 beats)
P3_CUT = beat(2)
P3_CSS = OVERLAY_CSS + """
#p3-b { position: absolute; inset: 0; opacity: 0;
  background: radial-gradient(ellipse 80% 46% at 50% 42%, rgba(255,255,205,.20) 0%, rgba(255,255,205,0) 100%),
    radial-gradient(ellipse 130% 95% at 50% 46%, rgba(0,0,0,0) 38%, rgba(0,0,0,.66) 100%), url('assets/img/tex-felt.jpg') 0 0 / 620px 620px; }
"""
card("p3", 4, f"""
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <text id="p3-q1" x="60" y="290" font-family="Frank Ruhl, serif" font-weight="900" font-size="130" fill="#fff4dc" stroke="#c9a36b" stroke-width="4" direction="ltr">?!</text>
  <text id="p3-q2" x="900" y="300" font-family="Frank Ruhl, serif" font-weight="900" font-size="120" fill="#fff4dc" stroke="#c9a36b" stroke-width="4" direction="ltr">?</text>
</svg>
<div id="p3-b">
  {logo_svg("p3-felt-logo", 330, 250, 420, stroke="#dcb873")}
  {shadow("p3-shA", 440, 1105, 300)}{shadow("p3-shB", 668, 1135, 300)}
  {die("p3-dA", 6, 430, 1010, 220, "a", -10)}{die("p3-dB", 4, 655, 1040, 220, "b", 14)}
  {hand("p3-hand", 560, 1100, 740, "open")}
</div>
""", css=P3_CSS, js=f"""
tl.fromTo(["#p3-q1", "#p3-q2"], {{ opacity: 0, scale: 0.4, transformOrigin: "50% 100%" }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)", stagger: 0.08 }}, 0.3);
tl.set("#p3-b", {{ opacity: 1 }}, {P3_CUT});
DiceKit.pose(tl, "#p3-hand", "open", 0);
tl.fromTo("#p3-hand", {{ y: 1250, rotation: 6 }}, {{ y: 0, rotation: -3, duration: 0.42, ease: "power3.out" }}, {P3_CUT});
DiceKit.pose(tl, "#p3-hand", "release", {P3_CUT + 0.42:.3f}); DiceKit.pose(tl, "#p3-hand", "fist", {P3_CUT + 0.5:.3f});
tl.set(["#p3-dA", "#p3-dB", "#p3-shA", "#p3-shB"], {{ opacity: 0 }}, {P3_CUT + 0.46:.3f});
tl.to("#p3-hand", {{ scale: 0.94, duration: 0.12, ease: "power2.out" }}, {P3_CUT + 0.42:.3f});
tl.to("#p3-hand", {{ y: 1350, rotation: 4, scale: 1, duration: 0.62, ease: "power2.in" }}, {P3_CUT + 0.6:.3f});
""")
sfx("p3", 0.3, "pop", .6)
sfx("p3", P3_CUT, "whoosh-short", .6)
sfx("p3", P3_CUT + 0.46, "click", .8)


# ===== 1. The hook: one throw, and the bill could disappear =====

def hook_flight(dx0, dy0, out, n=60, launch=7):
    """Card 1: the die leaves the fist, hangs in front of the lens (still turning), then rushes past the camera."""
    rows, hang = [], (n - launch) / FPS - 1.0
    for i in range(n):
        if i < launch:
            rows.append([dx0, dy0, 0.3, 0])
            continue
        t = (i - launch) / FPS
        u = min(1.0, t / 1.0)
        e = 1 - (1 - u) ** 3
        w = max(0.0, (t - 1.0) / hang)
        rows.append([r1(dx0 * (1 - e) + out[0] * (0.2 * w + 0.8 * w ** 4)), r1(dy0 * (1 - e) - 70 * math.sin(math.pi * u) * (1 - u) + out[1] * (0.2 * w + 0.8 * w ** 4)),
                     round(0.3 + 0.7 * e + 0.06 * w + 0.5 * w ** 4, 3), 1])
    ks = [0] * launch + [round(i * 17 / 23) for i in range(24)] + [17 + round(i * 6 / (n - launch - 25)) for i in range(n - launch - 24)]
    return rows, ks


_ra, _ka = hook_flight(215, 620, (-150, -70))
_rb, _kb = hook_flight(-200, 480, (150, 50))
card("s1", 4, f"""
<div class="h" style="top:236px;font-size:156px">הטלה אחת…</div>
<div class="sub" style="top:440px;font-size:64px">…והחשבון יכול להיעלם</div>
{die("s1-dA", 6, 330, 820, 290, "a", -16)}{die("s1-dB", 5, 748, 965, 290, "b", 20)}
{hand("s1-hand", 545, 1560, 470, "fist")}
""", css="#root { --glow: 46%; }", js=f"""
DiceKit.pose(tl, "#s1-hand", "fist", 0); DiceKit.pose(tl, "#s1-hand", "release", {7 / FPS:.4f}); DiceKit.pose(tl, "#s1-hand", "open", {10 / FPS:.4f});
tl.fromTo("#s1-hand", {{ y: 260, rotation: 4 }}, {{ y: -40, rotation: -8, duration: {7 / FPS:.4f}, ease: "power3.out" }}, 0);
tl.to("#s1-hand", {{ y: 30, rotation: -12, duration: 0.7, ease: "power1.out" }}, {7 / FPS:.4f});
tl.to("#s1-hand", {{ y: 700, rotation: -20, duration: 1.3, ease: "power2.in" }}, {7 / FPS + 0.7:.4f});
""" + js_bake("#s1-dA", 0, ["x", "y", "scale", "opacity"], _ra) + js_spin("#s1-dA", 0, 6, _ka)
    + js_bake("#s1-dB", 0, ["x", "y", "scale", "opacity"], _rb) + js_spin("#s1-dB", 0, 5, _kb))
sfx("s1", 7 / FPS, "whoosh", .8)
sfx("s1", 1.7, "whoosh-cinematic", .7)


# ===== 2. The brand and the name =====

def drop_rows(first_hit, n, delay=0, G=7000.0, E=0.36):
    """A die dropped from above the frame: it lands at `first_hit` seconds and bounces to rest. Returns y per frame
    (0 = at rest, negative = above), the tumble length in frames, and the bounce times."""
    y, v, dt, t, rows, ev = -0.5 * G * first_hit ** 2, 0.0, 1 / 240, 0.0, [], []
    for i in range((n - delay) * 10):
        if i % 10 == 0:
            rows.append(r1(y))
        v += G * dt
        y += v * dt
        if y >= 0:
            y = 0.0
            if v > 350:
                ev.append((delay / FPS + t, min(1.0, v / 2500)))
                v = -E * v
            else:
                v = 0.0
        t += dt
    rest = next(i for i in range(len(rows)) if all(abs(r) < 0.5 for r in rows[i:]))
    return [rows[0]] * delay + rows, delay + rest, ev


_ya, _na, _eva = drop_rows(beat(1), 90)
_yb, _nb, _evb = drop_rows(beat(1), 90, delay=2)
for _t, _s in _eva[:3] + _evb[:3]:
    sfx("s2", _t, "click" if _s > 0.9 else "click-soft", round(0.4 + 0.5 * _s, 2))
card("s2", 6, f"""
{logo_svg("s2-logo", 315, 150, 450)}
<div id="s2-jp" style="position:absolute;right:92px;top:226px;font-family:Shippori,serif;font-weight:800;font-size:56px;letter-spacing:.16em;color:{GOLD};writing-mode:vertical-rl" data-layout-ignore>運試し</div>
<div id="s2-badge" style="position:absolute;left:78px;top:520px;width:184px;height:184px;rotate:-12deg" data-layout-ignore>
  <svg viewBox="0 0 184 184" style="position:absolute;inset:0;width:100%;height:100%"><path d="{' '.join(('M' if k == 0 else 'L') + f'{92 + (90 if k % 2 == 0 else 80) * math.cos(k * math.pi / 16):.1f} {92 + (90 if k % 2 == 0 else 80) * math.sin(k * math.pi / 16):.1f}' for k in range(32))} Z" fill="{RED}" stroke="{GOLD_HI}" stroke-width="2"/>
  <circle cx="92" cy="92" r="66" fill="none" stroke="rgba(244,236,223,.55)" stroke-width="1.5"/></svg>
  <div style="position:absolute;inset:0;display:grid;place-items:center;font-family:'Frank Ruhl',serif;font-weight:800;font-size:60px;color:{IVORY};text-shadow:0 2px 0 rgba(0,0,0,.35)">חדש</div>
</div>
<div class="kick" style="top:772px;font-size:46px">המשחק הגדול</div>
<div class="h foil" id="s2-title" style="top:836px;font-size:110px">הטילו את הקוביות</div>
{shadow("s2-shA", 462, 1190, 210)}{shadow("s2-shB", 632, 1198, 210)}
{die("s2-dA", 6, 456, 1118, 150, "a", -12)}{die("s2-dB", 6, 628, 1126, 150, "b", 9)}
<div id="s2-seal" style="position:absolute;left:500px;top:1268px;width:80px;height:80px;border-radius:5px;background:{RED};color:{IVORY};display:grid;place-items:center;font-family:Shippori,serif;font-weight:800;font-size:50px;box-shadow:inset 0 0 0 3px rgba(244,236,223,.35), 0 8px 18px rgba(0,0,0,.5);rotate:-3deg" data-layout-ignore>運</div>
""", css="#root { --glow: 30%; }", js=
    js_bake("#s2-dA", 0, ["y"], [[v] for v in _ya]) + js_spin("#s2-dA", 0, 6, spin_keys(_na) + [-1])
    + js_bake("#s2-dB", 0, ["y"], [[v] for v in _yb]) + js_spin("#s2-dB", 0, 6, [0, 0] + spin_keys(_nb - 2) + [-1])
    + js_bake("#s2-shA", 0, ["opacity", "scale"], [[round(1 / (1 + -v / 90), 2), round(1 + -v / 900, 3)] for v in _ya])
    + js_bake("#s2-shB", 0, ["opacity", "scale"], [[round(1 / (1 + -v / 90), 2), round(1 + -v / 900, 3)] for v in _yb])
    + """
tl.fromTo("#s2-title", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.5, ease: "power2.inOut" }, 1.25);
tl.fromTo("#s2-badge", { scale: 1 }, { scale: 1.08, duration: 0.3125, ease: "power2.out", yoyo: true, repeat: 1 }, 2.5);
""")
sfx("s2", 2.5, "sparkle", .4)


# ===== 3a. When: happy hour, 16:00-18:00 =====
# A gold dress-watch dial: the hour hand sweeps 4 -> 6 o'clock across the lit happy-hour sector while, in the aperture
# above the pivot, the red sun sets behind ink mountains.
CX, CY = 540, 1000


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
card("s3a", 6, f"""
<div class="h foil" id="s3a-title" style="top:200px;font-size:132px">האפי האוור</div>
<div class="big" style="top:356px;font-size:128px;color:{IVORY};text-shadow:0 3px 0 rgba(0,0,0,.6), 0 16px 34px rgba(0,0,0,.6)"><span class="ltr">16:00–18:00</span></div>
<div class="sub" style="top:504px;font-size:56px">בואו בין ארבע לשש</div>
<svg id="s3a-watch" class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  <defs>
    <linearGradient id="s3a-bezel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e2a8"/><stop offset=".35" stop-color="#c9a36b"/><stop offset=".55" stop-color="#8a6534"/><stop offset=".8" stop-color="#e7c98a"/><stop offset="1" stop-color="#a8814a"/></linearGradient>
    <radialGradient id="s3a-face" cx=".5" cy=".42" r=".7"><stop offset="0" stop-color="#2a1d12"/><stop offset=".7" stop-color="#140f0b"/><stop offset="1" stop-color="#0b0907"/></radialGradient>
    <linearGradient id="s3a-sky" x1="0" y1="0" x2="0" y2="1"><stop id="s3a-skytop" offset="0" stop-color="#f3c66f"/><stop id="s3a-skybot" offset="1" stop-color="#e98b3a"/></linearGradient>
    <clipPath id="s3a-ap"><circle cx="{CX}" cy="{CY - 150}" r="104"/></clipPath>
    <linearGradient id="s3a-hand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f6e2a8"/><stop offset=".5" stop-color="#c9a36b"/><stop offset="1" stop-color="#8a6534"/></linearGradient>
    <radialGradient id="s3a-glass" cx=".32" cy=".22" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <linearGradient id="s3a-strapT" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#2b1b10"/><stop offset=".7" stop-color="#1c120b" stop-opacity=".85"/><stop offset="1" stop-color="#1c120b" stop-opacity="0"/></linearGradient>
    <linearGradient id="s3a-strapB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b1b10"/><stop offset=".55" stop-color="#1c120b" stop-opacity=".8"/><stop offset="1" stop-color="#1c120b" stop-opacity="0"/></linearGradient>
    <linearGradient id="s3a-stitch" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{CY + 320}" y2="{CY + 560}"><stop offset="0" stop-color="{GOLD}" stop-opacity=".5"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
    <filter id="s3a-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
  </defs>
  <ellipse cx="{CX}" cy="{CY + 40}" rx="352" ry="352" fill="#000" opacity=".7" filter="url(#s3a-soft)"/>
  <!-- the crown and the lugs make it a watch, not a wall clock -->
  <rect x="{CX + 346}" y="{CY - 26}" width="34" height="52" rx="8" fill="url(#s3a-bezel)"/>
  <path d="M{CX - 150} {CY - 300} L{CX - 132} {CY - 420} L{CX + 132} {CY - 420} L{CX + 150} {CY - 300} Z" fill="url(#s3a-strapT)"/>
  <path d="M{CX - 150} {CY + 300} L{CX - 120} {CY + 600} L{CX + 120} {CY + 600} L{CX + 150} {CY + 300} Z" fill="url(#s3a-strapB)"/>
  <g fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="9 8">
    <path d="M{CX - 116} {CY - 420} L{CX - 130} {CY - 320} M{CX + 116} {CY - 420} L{CX + 130} {CY - 320}" opacity=".45"/>
    <path d="M{CX - 130} {CY + 320} L{CX - 106} {CY + 560} M{CX + 130} {CY + 320} L{CX + 106} {CY + 560}" stroke="url(#s3a-stitch)"/></g>
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
  <circle cx="{CX}" cy="{CY}" r="320" fill="url(#s3a-glass)"/>
  <path id="s3a-glint" d="M{CX - 300} {CY - 160} A350 350 0 0 1 {CX - 120} {CY - 330}" fill="none" stroke="#fff6dc" stroke-width="6" stroke-linecap="round" opacity=".55"/>
</svg>
""", css="#root { --glow: 52%; }", js=f"""
tl.fromTo("#s3a-hr", {{ rotation: 120, svgOrigin: "{CX} {CY}" }}, {{ rotation: 180, svgOrigin: "{CX} {CY}", duration: 3.75, ease: "power1.inOut" }}, 0);
tl.fromTo("#s3a-min", {{ rotation: 0, svgOrigin: "{CX} {CY}" }}, {{ rotation: 720, svgOrigin: "{CX} {CY}", duration: 3.75, ease: "power1.inOut" }}, 0);
tl.fromTo("#s3a-sun", {{ attr: {{ cy: {CY - 170} }} }}, {{ attr: {{ cy: {CY - 90} }}, duration: 3.75, ease: "power1.in" }}, 0);
tl.fromTo("#s3a-skytop", {{ attr: {{ "stop-color": "#f3c66f" }} }}, {{ attr: {{ "stop-color": "#c0492f" }}, duration: 3.75, ease: "none" }}, 0);
tl.fromTo("#s3a-skybot", {{ attr: {{ "stop-color": "#e98b3a" }} }}, {{ attr: {{ "stop-color": "#4a1a1a" }}, duration: 3.75, ease: "none" }}, 0);
tl.fromTo("#s3a-glint", {{ rotation: 0, svgOrigin: "{CX} {CY}", opacity: 0 }}, {{ rotation: 300, svgOrigin: "{CX} {CY}", opacity: .55, duration: 1.6, ease: "power2.inOut" }}, 0.4);
tl.to("#s3a-glint", {{ opacity: 0, duration: 0.3, ease: "power1.in" }}, 2.0);
tl.fromTo("#s3a-title", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }}, 0.2);
""")
sfx("s3a", 0.5, "sparkle", .5)


# ===== 3b. Rule 1: the moment of truth (the bill arrives, with the dice on it) =====

def slide_rows(dx0, n, hops=2, hop=34):
    """A die rolling in along a surface from dx0 px away: it slows to a stop with a few small hops."""
    rows = []
    for i in range(n + 1):
        u = i / n
        rows.append([r1(dx0 * (1 - u) ** 3), r1(-hop * abs(math.sin(math.pi * hops * u)) * (1 - u) ** 1.5)])
    return rows


TABLE_CSS = """
.dtable { position: absolute; left: 70px; top: 668px; width: 940px; height: 680px; border-radius: 52px;
  background: linear-gradient(180deg, rgba(255,220,170,.10) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,.34) 100%), url('assets/img/tex-walnut.jpg') center / 1400px 100%;
  box-shadow: inset 0 0 0 3px rgba(201,163,107,.6), inset 0 0 0 14px rgba(0,0,0,.14), inset 0 0 120px rgba(0,0,0,.55), 0 40px 70px rgba(0,0,0,.7); }
.plate { position: absolute; width: 250px; height: 250px; margin: -125px 0 0 -125px; background: url('assets/img/plate.png') center / contain no-repeat; }
.cup { position: absolute; width: 62px; height: 62px; margin: -31px 0 0 -31px; border-radius: 50%;
  background: radial-gradient(circle at 42% 38%, #d8c28e 0%, #b08c4c 34%, #1d1612 38%, #0e0a08 62%, #c9a36b 66%, #7a5a2a 70%, rgba(0,0,0,0) 72%); box-shadow: 0 10px 14px rgba(0,0,0,.5); }
"""
card("s3b", 6, f"""
{rule(1)}
<div class="h" style="top:284px;font-size:132px">רגע האמת</div>
<div class="sub" style="top:440px;font-size:54px">משחקים רק בסוף הארוחה,<br>כשמגיע החשבון</div>
<div class="dtable" data-layout-ignore>
  <div class="plate" style="left:470px;top:108px;rotate:8deg"></div><div class="plate" style="left:812px;top:344px;rotate:96deg"></div>
  <div class="plate" style="left:470px;top:572px;rotate:188deg"></div><div class="plate" style="left:128px;top:344px;rotate:-82deg"></div>
  <div class="cup" style="left:650px;top:120px"></div><div class="cup" style="left:296px;top:560px"></div><div class="cup" style="left:150px;top:150px"></div><div class="cup" style="left:800px;top:560px"></div>
</div>
<div id="s3b-grp" style="position:absolute;inset:0">
  <img id="s3b-folder" class="art" src="assets/img/folder.png" alt="" style="left:182px;top:744px;width:716px;height:528px;rotate:-4deg">
  {shadow("s3b-shA", 498, 1050, 150)}{shadow("s3b-shB", 606, 1062, 150)}
  {die("s3b-dA", 3, 492, 1000, 104, "a", -10)}{die("s3b-dB", 5, 600, 1012, 104, "b", 14)}
</div>
{hand("s3b-hand", 905, 1030, 400, "flat", -92)}
""", css=TABLE_CSS + "#root { --glow: 52%; }", js="""
DiceKit.pose(tl, "#s3b-hand", "flat", 0);
tl.fromTo(["#s3b-grp", "#s3b-hand"], { x: 900 }, { x: 0, duration: 0.95, ease: "power3.out" }, 0);
tl.to("#s3b-hand", { x: 700, duration: 0.8, ease: "power2.in" }, 1.25);
tl.fromTo("#s3b-folder", { rotation: 4 }, { rotation: 0, duration: 0.95, ease: "power3.out" }, 0);
for (const [d, r] of [["#s3b-dA", -3], ["#s3b-dB", 3]]) { tl.fromTo(d, { y: 0 }, { y: -16, duration: 0.11, ease: "power2.out", yoyo: true, repeat: 1 }, 0.9); }
""")
sfx("s3b", 0.04, "whoosh-short", .7)
sfx("s3b", 0.92, "click-soft", .7)


# ===== 4. Rule 2: one chance =====
_s4 = slide_rows(760, 26)
card("s4", 6, f"""
{rule(2)}
<div class="h" style="top:284px;font-size:124px">הזדמנות אחת</div>
<div class="big foil" id="s4-x1" style="top:452px;font-size:430px"><span class="ltr">×1</span></div>
<div class="sub" style="top:912px;font-size:56px">ניסיון אחד ויחיד לכל השולחן</div>
<div style="position:absolute;left:140px;top:1150px;width:800px;height:260px;border-radius:50%;background:radial-gradient(ellipse at 50% 50%, rgba(226,197,144,.20) 0%, rgba(226,197,144,0) 68%)" data-layout-ignore></div>
{shadow("s4-shA", 432, 1272, 300)}{shadow("s4-shB", 672, 1284, 300)}
{die("s4-dA", 4, 424, 1170, 212, "a", -12)}{die("s4-dB", 2, 664, 1182, 212, "b", 10)}
""", css="#root { --glow: 60%; }", js=
    js_bake("#s4-dA", 0, ["x", "y"], _s4) + js_bake("#s4-shA", 0, ["x"], [[r[0]] for r in _s4]) + js_spin("#s4-dA", 0, 4, spin_keys(26) + [-1])
    + js_bake("#s4-dB", 2 / FPS, ["x", "y"], _s4) + js_bake("#s4-shB", 2 / FPS, ["x"], [[r[0]] for r in _s4]) + js_spin("#s4-dB", 2 / FPS, 2, spin_keys(26) + [-1])
    + f"""
tl.set(["#s4-dB", "#s4-shB"], {{ x: {_s4[0][0]} }}, 0);
tl.fromTo("#s4-x1", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.6, ease: "power2.inOut" }}, 1.25);
tl.fromTo("#s4-x1", {{ scale: 1 }}, {{ scale: 1.045, duration: 0.3125, ease: "power2.out", yoyo: true, repeat: 1 }}, 3.125);
""")
sfx("s4", 0.04, "whoosh-short", .6)
sfx("s4", 26 / FPS * 0.55, "click-soft", .6)
sfx("s4", 3.125, "pop", .5)


# ===== 5. Rule 3: one player. A Higgsfield still (assets/hf/S5.png): the friends point at the man with the dice =====
card("s5", 6, f"""
{rule(3)}
<div class="h" style="top:284px;font-size:132px">שחקן אחד</div>
<div class="sub" style="top:444px;font-size:56px">רק אחד מטיל, בשביל כולם</div>
<div style="position:absolute;left:84px;top:560px;width:912px;height:1090px;border-radius:30px;background:linear-gradient(135deg,#f6e2a8 0%,#c9a36b 30%,#8a6534 52%,#e7c98a 78%,#a8814a 100%);box-shadow:0 30px 60px rgba(0,0,0,.65)" data-layout-ignore></div>
<div style="position:absolute;left:92px;top:568px;width:896px;height:1074px;border-radius:24px;background:{INK}" data-layout-ignore></div>
<div style="position:absolute;left:104px;top:580px;width:872px;height:1050px;border-radius:16px;overflow:hidden" data-layout-allow-overflow>
  <img id="s5-img" src="assets/hf/S5.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%">
  <div style="position:absolute;inset:0;border-radius:16px;box-shadow:inset 0 0 0 2px rgba(226,197,144,.7), inset 0 0 90px rgba(0,0,0,.45)"></div>
  <div id="s5-spot" style="position:absolute;inset:0;background:radial-gradient(ellipse 46% 40% at 47% 34%, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 62%, rgba(0,0,0,.55) 100%);opacity:0"></div>
</div>
""", css="#root { --glow: 30%; }", js="""
tl.fromTo("#s5-img", { scale: 1, transformOrigin: "47% 30%" }, { scale: 1.14, transformOrigin: "47% 30%", duration: 3.75, ease: "power1.inOut" }, 0);
tl.fromTo("#s5-spot", { opacity: 0 }, { opacity: 1, duration: 2.5, ease: "power1.inOut" }, 0.625);
""")
sfx("s5", 0.02, "whoosh-short", .5)
sfx("s5", 1.25, "pop", .5)


# ===== 6a. Rule 4: the throw that doesn't count (only one die reaches the far wall) =====

def trail(points, color, cls):
    """The dotted line a die travelled along the felt."""
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in points[::2] + [points[-1]])
    return f'<polyline class="{cls}" points="{pts}" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 20" opacity="0"/>'


def table_hand_js(hid, t0):
    """The thrower's fist comes up, opens on the release, and drops out of frame."""
    return f"""
DiceKit.pose(tl, "#{hid}", "fist", 0); DiceKit.pose(tl, "#{hid}", "release", {t0:.4f}); DiceKit.pose(tl, "#{hid}", "open", {t0 + 3 / FPS:.4f});
tl.fromTo("#{hid}", {{ y: 190, rotation: 3 }}, {{ y: -60, rotation: -4, duration: {t0:.4f}, ease: "power3.out" }}, 0);
tl.to("#{hid}", {{ y: -30, duration: 0.3, ease: "power1.out" }}, {t0:.4f});
tl.to("#{hid}", {{ y: 640, rotation: 6, duration: 0.8, ease: "power2.in" }}, {t0 + 0.3:.4f});
"""


WALL_Y = Table.proj(500, Table.IN, Table.WH)[1]   # where the top of the far wall is on screen
TABLE_BG = f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse 90% 26% at 50% 14%, rgba(84,50,22,.6) 0%, rgba(84,50,22,0) 100%)" data-layout-ignore></div>'

_a = table_throw("s6a", "s6a-dA", 4, (430, 2250, 140), (395, 163), 520, True, wall_at=beat(2))
_b = table_throw("s6a", "s6a-dB", 2, (590, 2250, 140), (578, 700), 840, False, launch=_a["t0"], vol=.8)
_shA, _dA = table_die("s6a-dA", 4, "a")
_shB, _dB = table_die("s6a-dB", 2, "b")
card("s6a", 6, f"""
{TABLE_BG}
{Table.html("s6a")}
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  {trail(_a["path"], IVORY, "s6a-miss")}{trail(_b["path"], IVORY, "s6a-miss")}
  <circle id="s6a-ring" cx="{_b["rest"][0]:.0f}" cy="{_b["rest"][1]:.0f}" r="{Table.C * _b["rest"][2] * 0.86:.0f}" fill="none" stroke="#e0574b" stroke-width="9" opacity="0"/>
</svg>
{_shA}{_shB}{_dA}{_dB}
<div id="s6a-spark" class="spark" style="left:{_a["wall"][0]:.0f}px;top:{_a["wall"][1]:.0f}px" data-layout-ignore></div>
{rule(4, 160)}
<div class="h" style="top:270px;font-size:112px">ההטלה המושלמת</div>
<div class="kick" style="top:414px;font-size:46px;letter-spacing:.04em;font-weight:700">הקיר שממול ⌄</div>
{stamp("s6a-x", "✕&nbsp; לא נחשב", 540, 1052, "#e0574b", -5)}
<div class="h" id="s6a-again" style="top:1212px;font-size:84px;color:{GOLD_HI}">מטילים שוב!</div>
{hand("s6a-hand", 545, 1740, 400, "fist")}
""", css=Table.CSS, js=table_hand_js("s6a-hand", _a["t0"]) + _a["js"] + _b["js"] + f"""
tl.fromTo("#s6a-spark", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.06, ease: "none" }}, {_a["wall_t"]:.4f});
tl.to("#s6a-spark", {{ opacity: 0, scale: 1.5, duration: 0.3, ease: "power2.out" }}, {_a["wall_t"] + 0.06:.4f});
tl.fromTo(".s6a-miss", {{ opacity: 0 }}, {{ opacity: 0.6, duration: 0.2, ease: "power1.out" }}, {beat(3) - 0.2:.4f});
tl.fromTo("#s6a-ring", {{ opacity: 0, scale: 1.6, svgOrigin: "{_b["rest"][0]:.0f} {_b["rest"][1]:.0f}" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }}, {beat(3) - 0.2:.4f});
tl.fromTo("#s6a-x", {{ opacity: 0, scale: 1.7 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }}, {beat(4) - 0.2:.4f});
tl.fromTo("#s6a-again", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }}, {beat(5) - 0.2:.4f});
tl.to("#s6a-again", {{ scale: 1.05, duration: 0.3125, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {beat(5):.4f});
""")
sfx("s6a", _a["t0"], "whoosh", .8)
sfx("s6a", beat(3), "pop", .6)
sfx("s6a", beat(4), "impact-bass-2", .8)
sfx("s6a", beat(5), "pop", .8)


# ===== 6b. Rule 4: the perfect throw (both dice come back off the far wall) =====
_a2 = table_throw("s6b", "s6b-dA", 3, (430, 2250, 140), (372, 163), 690, True, wall_at=beat(2))
_b2 = table_throw("s6b", "s6b-dB", 5, (590, 2250, 140), (628, 163), 830, True, launch=_a2["t0"])
_shA2, _dA2 = table_die("s6b-dA", 3, "a")
_shB2, _dB2 = table_die("s6b-dB", 5, "b")
_okx, _oky = 540, 1196
card("s6b", 10, f"""
{TABLE_BG}
{Table.html("s6b")}
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  {trail(_a2["path"], GOLD_HI, "s6b-trail")}{trail(_b2["path"], GOLD_HI, "s6b-trail")}
</svg>
<div id="s6b-glow" style="position:absolute;left:{_okx - 260}px;top:{_oky - 190}px;width:520px;height:380px;border-radius:50%;background:radial-gradient(ellipse at 50% 50%, rgba(226,197,144,.5) 0%, rgba(226,197,144,0) 70%);opacity:0" data-layout-ignore></div>
{_shA2}{_shB2}{_dA2}{_dB2}
<div id="s6b-sparkA" class="spark" style="left:{_a2["wall"][0]:.0f}px;top:{_a2["wall"][1]:.0f}px" data-layout-ignore></div>
<div id="s6b-sparkB" class="spark" style="left:{_b2["wall"][0]:.0f}px;top:{_b2["wall"][1]:.0f}px" data-layout-ignore></div>
{rule(4, 160)}
<div class="h foil" id="s6b-title" style="top:270px;font-size:112px">ההטלה המושלמת</div>
<div class="sub" style="top:410px;font-size:50px">שתי הקוביות חייבות לפגוע בקיר</div>
<svg id="s6b-ok" class="art" style="left:{_okx - 85}px;top:{_oky - 85}px;width:170px;height:170px;opacity:0" viewBox="0 0 140 140" data-layout-ignore>
  <circle cx="70" cy="70" r="64" fill="{INK}" stroke="{GOLD}" stroke-width="5"/><circle cx="70" cy="70" r="54" fill="none" stroke="rgba(201,163,107,.5)" stroke-width="1.5"/>
  <path d="M40 72 L62 94 L102 50" fill="none" stroke="{GOLD_HI}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>
{hand("s6b-hand", 545, 1740, 400, "fist")}
""", css=Table.CSS, js=table_hand_js("s6b-hand", _a2["t0"]) + _a2["js"] + _b2["js"] + "".join(f"""
tl.fromTo("#{sid}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.06, ease: "none" }}, {th["wall_t"]:.4f});
tl.to("#{sid}", {{ opacity: 0, scale: 1.5, duration: 0.3, ease: "power2.out" }}, {th["wall_t"] + 0.06:.4f});
tl.fromTo("#{sid}", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 0.9, scale: 1.1, duration: 0.25, ease: "power2.out", immediateRender: false }}, {beat(6) + k * 0.3125:.4f});
tl.to("#{sid}", {{ opacity: 0, scale: 1.7, duration: 0.5, ease: "power2.out" }}, {beat(6) + k * 0.3125 + 0.25:.4f});
""" for k, (sid, th) in enumerate([("s6b-sparkA", _a2), ("s6b-sparkB", _b2)])) + f"""
tl.fromTo(".s6b-trail", {{ opacity: 0 }}, {{ opacity: 0.7, duration: 0.25, ease: "power1.out" }}, {beat(4) - 0.25:.4f});
tl.fromTo("#s6b-ok", {{ opacity: 0, scale: 1.7 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.in" }}, {beat(4) - 0.2:.4f});
tl.fromTo("#s6b-glow", {{ opacity: 0 }}, {{ opacity: 0.7, duration: 0.3, ease: "power2.out" }}, {beat(4):.4f});
tl.to("#s6b-glow", {{ opacity: 0.25, duration: 0.9, ease: "power2.inOut" }}, {beat(4) + 0.3:.4f});
tl.fromTo("#s6b-title", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.8, ease: "power2.inOut" }}, {beat(5):.4f});
tl.to("#s6b-glow", {{ opacity: 0.75, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {beat(8):.4f});
tl.to("#s6b-ok", {{ scale: 1.08, duration: 0.3125, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {beat(8):.4f});
""")
sfx("s6b", _a2["t0"], "whoosh", .8)
sfx("s6b", beat(4), "impact-bass-1", .8)
sfx("s6b", beat(6), "sparkle", .5)


# ===== 7. Prize: double 1, 2 or 3 = 50% off =====

def flip_js(sel, face, t_land, n=8, lift=54):
    """A die hops and turns over onto `face`, landing exactly at t_land (the last n frames of that face's tumble)."""
    t0 = t_land - n / FPS
    return js_spin(sel, t0, face, list(range(24 - n, 24)) + [-1]) + (
        f'tl.to("{sel}", {{ y: -{lift}, duration: {n / FPS / 2:.4f}, ease: "power2.out", yoyo: true, repeat: 1 }}, {t0:.4f});\n')


def doubles_js(card_id, faces):
    """Both dice turn over to the next double on each beat."""
    js = ""
    for i, f in enumerate(faces[1:], start=1):
        js += flip_js(f"#{card_id}-dA", f, beat(i)) + flip_js(f"#{card_id}-dB", f, beat(i) + 1 / FPS)
        sfx(card_id, beat(i), "click-soft", .8)
    return js


card("s7", 8, f"""
<div class="h" style="top:196px;font-size:112px">דאבל 1 · 2 · 3</div>
{shadow("s7-shA", 474, 452, 170, .8)}{shadow("s7-shB", 612, 452, 170, .8)}
{die("s7-dA", [1, 2, 3], 470, 400, 122, "a", -8)}{die("s7-dB", [1, 2, 3], 610, 400, 122, "b", 7)}
<div class="big foil" id="s7-pct" style="top:512px;font-size:300px"><span class="ltr">−50%*</span></div>
<div class="sub" style="top:826px;font-size:58px">על כל החשבון של השולחן</div>
<img id="s7-rc" class="art" src="assets/img/receipt.png" alt="" style="left:245px;top:900px;width:590px;height:852px;rotate:-4deg" data-layout-ignore>
<div id="s7-stamp" style="position:absolute;left:372px;top:1318px;width:340px;height:150px;rotate:-13deg;border:8px solid #b3261e;border-radius:18px;display:grid;place-items:center;
  font-family:'Frank Ruhl',serif;font-weight:900;font-size:108px;line-height:1;color:#b3261e;mix-blend-mode:multiply;opacity:0" data-layout-ignore><span class="ltr">−50%</span></div>
""", css="#root { --glow: 68%; }", js=doubles_js("s7", [1, 2, 3]) + f"""
tl.fromTo("#s7-stamp", {{ opacity: 0, scale: 1.9 }}, {{ opacity: 0.86, scale: 1, duration: 0.2, ease: "power3.in" }}, {beat(4) - 0.2:.4f});
tl.fromTo("#s7-rc", {{ y: 0 }}, {{ y: 10, duration: 0.07, ease: "power1.out", yoyo: true, repeat: 1 }}, {beat(4):.4f});
tl.fromTo("#s7-pct", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }}, {beat(5):.4f});
tl.fromTo("#s7-pct", {{ scale: 1 }}, {{ scale: 1.04, duration: 0.3125, ease: "power2.out", yoyo: true, repeat: 1 }}, {beat(4):.4f});
""")
sfx("s7", beat(4), "impact-bass-2", .8)
sfx("s7", beat(5) + 0.4, "sparkle", .4)


# ===== 8. Prize: double 4, 5 or 6 = the meal is on the house =====
_seed = [7]


def rnd():
    _seed[0] = (_seed[0] * 16807) % 2147483647
    return _seed[0] / 2147483647


PETAL = "M0 -18 C10 -18 14 -6 6 2 L0 8 L-6 2 C-14 -6 -10 -18 0 -18 Z"
PETALS = "".join(
    f'<g class="s8-fall" data-vy="{300 + rnd() * 260:.0f}" data-vr="{(rnd() - .5) * 240:.0f}" data-sway="{20 + rnd() * 50:.0f}"><g transform="translate({60 + rnd() * 960:.0f} {-260 + rnd() * 1900:.0f}) rotate({rnd() * 360:.0f}) scale({1.0 + rnd() * 0.9:.2f})">'
    + (f'<path d="{PETAL}" fill="{["#f7d6d9", IVORY, "#f3c1c6"][k % 3]}"/>' if k % 2 else f'<rect x="-13" y="-9" width="26" height="18" rx="2" fill="{["#fff3cf", "#f6e2a8", "#b98c42"][k % 3]}"/>')
    + '</g></g>' for k in range(26))
# the bill, torn into 8 pieces: 2 columns x 4 rows of the receipt, each with ragged inner edges
RW, RH = 330, 477
PIECES = ""
for _r in range(4):
    for _c in range(2):
        x0, x1, y0, y1 = _c * 50, (_c + 1) * 50, _r * 25, (_r + 1) * 25
        j = lambda: (rnd() - .5) * 5
        poly = f"{x0}% {y0}%, {(x0 + x1) / 2 + j():.1f}% {y0 + j() * (_r > 0):.1f}%, {x1}% {y0}%, {x1 + j() * (_c == 0):.1f}% {(y0 + y1) / 2:.1f}%, {x1}% {y1}%, {(x0 + x1) / 2 + j():.1f}% {y1 + j() * (_r < 3):.1f}%, {x0}% {y1}%"
        PIECES += (f'<div class="s8-piece" data-dx="{(-1 if _c == 0 else 1) * (150 + rnd() * 260):.0f}" data-dy="{(_r - 1.5) * 110 + 40 + rnd() * 150:.0f}" data-r="{(rnd() - .5) * 300:.0f}" '
                   f'style="position:absolute;left:0;top:0;width:{RW}px;height:{RH}px;background:url(\'assets/img/receipt.png\') center / 100% 100%;clip-path:polygon({poly});transform-origin:{(x0 + x1) / 2}% {(y0 + y1) / 2}%"></div>')
card("s8", 8, f"""
<div style="position:absolute;inset:0;background:url('assets/img/tex-gold.jpg') center / cover" data-layout-ignore></div>
<div id="s8-rays" style="position:absolute;left:-460px;top:-160px;width:2000px;height:2000px;border-radius:50%;
  background:repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,246,214,.20) 0deg 6deg, rgba(255,246,214,0) 6deg 15deg);
  -webkit-mask-image:radial-gradient(circle, rgba(0,0,0,0) 14%, #000 34%, rgba(0,0,0,0) 70%);mask-image:radial-gradient(circle, rgba(0,0,0,0) 14%, #000 34%, rgba(0,0,0,0) 70%)" data-layout-ignore></div>
<svg id="s8-burst" class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>{PETALS}</svg>
<div id="s8-ribbon" style="position:absolute;left:230px;top:186px;width:620px;height:126px;background:linear-gradient(180deg,#c93a30 0%,{RED} 55%,#8f241d 100%);clip-path:polygon(0 0, 100% 0, 94% 50%, 100% 100%, 0 100%, 6% 50%);display:grid;place-items:center;
  font-family:'Frank Ruhl',serif;font-weight:900;font-size:82px;color:{IVORY};line-height:1;text-shadow:0 3px 0 rgba(0,0,0,.3)">ג'קפוט!</div>
<div class="h" style="top:344px;font-size:100px;color:#14110e;text-shadow:0 2px 0 rgba(255,244,205,.55)">דאבל 4 · 5 · 6</div>
<div class="big" id="s8-pct" style="top:470px;font-size:330px;color:#14110e;text-shadow:0 3px 0 rgba(255,244,205,.6)"><span class="ltr">100%*</span></div>
<div class="h" id="s8-title" style="top:806px;font-size:88px;color:#14110e;text-shadow:none;background:linear-gradient(100deg,#14110e 0%,#14110e 42%,#8a2a1f 50%,#14110e 58%,#14110e 100%);background-size:300% 100%;background-position:100% 0;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">כל הארוחה עלינו</div>
{shadow("s8-shA", 430, 1198, 290, .8)}{shadow("s8-shB", 664, 1210, 290, .8)}
{die("s8-dA", [4, 5, 6], 424, 1098, 204, "a", -10)}{die("s8-dB", [4, 5, 6], 658, 1110, 204, "b", 8)}
<div id="s8-rc" style="position:absolute;left:{540 - RW // 2}px;top:1262px;width:{RW}px;height:{RH}px;rotate:3deg" data-layout-ignore>{PIECES}</div>
""", js=doubles_js("s8", [4, 5, 6]) + f"""
// the bill bursts on the jackpot beat; petals and gold leaf fall for the whole card
document.querySelectorAll(".s8-piece").forEach((p) => {{
  tl.fromTo(p, {{ x: 0, y: 0, rotation: 0 }}, {{ x: +p.dataset.dx, y: +p.dataset.dy, rotation: +p.dataset.r, duration: 2.2, ease: "expo.out" }}, {beat(2):.4f});
  tl.fromTo(p, {{ opacity: 1 }}, {{ opacity: 0, duration: 1.2, ease: "power1.in", immediateRender: false }}, {beat(2) + 0.9:.4f});
}});
document.querySelectorAll(".s8-fall").forEach((g) => {{
  tl.fromTo(g, {{ y: -200, x: 0, rotation: 0, transformOrigin: "50% 50%" }}, {{ y: -200 + +g.dataset.vy * 5 / 2.6, x: +g.dataset.sway, rotation: +g.dataset.vr, duration: 5, ease: "none" }}, 0);
}});
tl.fromTo("#s8-rays", {{ rotation: 0 }}, {{ rotation: 24, duration: 5, ease: "none" }}, 0);
tl.fromTo("#s8-pct", {{ scale: 1 }}, {{ scale: 1.07, duration: 0.2, ease: "power2.out" }}, {beat(2):.4f});
tl.to("#s8-pct", {{ scale: 1, duration: 0.5, ease: "power2.inOut" }}, {beat(2) + 0.2:.4f});
tl.fromTo("#s8-ribbon", {{ scale: 1 }}, {{ scale: 1.1, duration: 0.2, ease: "power2.out", yoyo: true, repeat: 1 }}, {beat(2):.4f});
tl.fromTo("#s8-title", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.4, ease: "power2.inOut" }}, {beat(4):.4f});
tl.to("#s8-pct", {{ scale: 1.035, duration: 0.3125, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {beat(6):.4f});
""")
SFX.append(("s7", beat(7), "riser", .6))  # the riser starts under the last beat of card 7 and lands on the jackpot
sfx("s8", beat(2), "impact-bass-1", 1.0)
sfx("s8", beat(2) + 0.05, "sparkle", .6)


# ===== 9. No double =====
_s9a, _s9b = slide_rows(-640, 24, hops=2, hop=44), slide_rows(640, 26, hops=2, hop=44)
card("s9", 4, f"""
<div class="h" style="top:232px;font-size:128px">לא יצא דאבל?</div>
<div class="sub" style="top:408px;font-size:60px">נשארתם עם ארוחה מעולה</div>
{shadow("s9-shA", 370, 905, 350)}{shadow("s9-shB", 728, 945, 350)}
{die("s9-dA", 3, 360, 790, 248, "a", -12)}{die("s9-dB", 5, 720, 830, 248, "b", 11)}
<svg class="art" style="left:340px;top:1060px;width:400px;height:400px" viewBox="0 0 300 300" data-layout-ignore>
  <defs><linearGradient id="s9-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e2a8"/><stop offset=".5" stop-color="#c9a36b"/><stop offset="1" stop-color="#e7c98a"/></linearGradient></defs>
  <g fill="none" stroke="url(#s9-g)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M52 150 L248 150 Q244 246 150 250 Q56 246 52 150 Z"/><path d="M96 268 L204 268"/><path d="M70 176 Q150 196 230 176" opacity=".55"/>
    <path d="M176 148 L236 84 M196 150 L252 96"/>
    <path class="s9-steam" d="M112 118 Q96 94 112 72 Q128 50 114 28"/><path class="s9-steam" d="M150 118 Q134 94 150 72 Q166 50 152 28"/></g></svg>
""", css="#root { --glow: 46%; }", js=
    js_bake("#s9-dA", 0, ["x", "y"], _s9a) + js_bake("#s9-shA", 0, ["x"], [[r[0]] for r in _s9a]) + js_spin("#s9-dA", 0, 3, spin_keys(24) + [-1])
    + js_bake("#s9-dB", 0, ["x", "y"], _s9b) + js_bake("#s9-shB", 0, ["x"], [[r[0]] for r in _s9b]) + js_spin("#s9-dB", 0, 5, spin_keys(26) + [-1])
    + """
tl.fromTo(".s9-steam", { y: 14, opacity: 0.25 }, { y: -18, opacity: 1, duration: 1.25, ease: "sine.inOut", stagger: 0.3, yoyo: true, repeat: 1 }, 0);
""")
sfx("s9", 0.04, "whoosh-short", .7)
sfx("s9", 0.62, "click-soft", .9)


# ===== 10. The service: the tip isn't included =====
COINS = "".join(f'<img class="s10-set" src="assets/img/coin-settle-{k}.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;opacity:{1 if k == 0 else 0}">' for k in range(12))
card("s10", 6, f"""
<div class="h foil" id="s10-title" style="top:232px;font-size:138px">השירות</div>
<div class="sub" style="top:416px;font-size:62px">הטיפ לא כלול בהטבה</div>
<div style="position:absolute;left:90px;top:1000px;width:900px;height:380px;border-radius:50%;background:radial-gradient(ellipse at 50% 50%, rgba(0,0,0,.8) 0%, rgba(0,0,0,0) 68%)" data-layout-ignore></div>
<img class="art" src="assets/img/tray.png" alt="" style="left:20px;top:716px;width:1040px;height:601px" data-layout-ignore>
<div class="art" style="left:{462 - 180}px;top:{1066 - 159}px;width:360px;height:270px;background:url('assets/img/coin.png') center / contain no-repeat" data-layout-ignore></div>
<div class="art" style="left:{628 - 180}px;top:{1086 - 159}px;width:360px;height:270px;background:url('assets/img/coin.png') center / contain no-repeat;rotate:8deg" data-layout-ignore></div>
<div id="s10-drop" class="art" style="left:{546 - 180}px;top:{1034 - 159}px;width:360px;height:270px" data-layout-ignore>{COINS}</div>
<svg class="art" style="left:0;top:0;width:1080px;height:1920px" viewBox="0 0 1080 1920" data-layout-ignore>
  {"".join(f'<path class="s10-tw" d="M{x} {y - r} Q{x} {y} {x + r} {y} Q{x} {y} {x} {y + r} Q{x} {y} {x - r} {y} Q{x} {y} {x} {y - r} Z" fill="#fff6dc" opacity="0"/>' for x, y, r in [(486, 1000, 44), (640, 1052, 30), (566, 1094, 22)])}</svg>
""", css="#root { --glow: 56%; }", js=f"""
tl.fromTo("#s10-drop", {{ y: -1150 }}, {{ y: 0, duration: {beat(1):.4f}, ease: "power2.in" }}, 0);
tl.to("#s10-drop", {{ y: -34, duration: 0.11, ease: "power2.out", yoyo: true, repeat: 1 }}, {beat(1):.4f});
const coins = document.querySelectorAll(".s10-set");
for (let k = 1; k < 12; k++) tl.set(coins, {{ opacity: (i) => (i === k ? 1 : 0) }}, {beat(1):.4f} + (k - 1) / 24 - 1e-4);
tl.fromTo(".s10-tw", {{ opacity: 0, scale: 0.2, rotation: 0, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, rotation: 45, duration: 0.3, ease: "power2.out", stagger: 0.3125 }}, {beat(2):.4f});
tl.to(".s10-tw", {{ opacity: 0, scale: 0.3, rotation: 90, duration: 0.35, ease: "power2.in", stagger: 0.3125 }}, {beat(2) + 0.3:.4f});
tl.fromTo("#s10-title", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.5, ease: "power2.inOut" }}, {beat(3):.4f});
""")
sfx("s10", beat(1), "click", .9)
sfx("s10", beat(2), "sparkle", .5)


# ===== 11. Smile, you're on camera. The winners (assets/hf/S11.png) on a phone that is recording =====
card("s11", 8, f"""
<div class="h" style="top:192px;font-size:112px">חייכו,<br>אתם מצולמים!</div>
<div class="sub" style="top:444px;font-size:52px">רגעי הזכייה עולים לרשתות שלנו</div>
<div style="position:absolute;left:216px;top:548px;width:648px;height:1122px;border-radius:88px;background:linear-gradient(135deg,#f6e2a8 0%,#c9a36b 22%,#6d5026 48%,#e7c98a 74%,#a8814a 100%);box-shadow:0 36px 70px rgba(0,0,0,.7)" data-layout-ignore></div>
<div style="position:absolute;left:224px;top:556px;width:632px;height:1106px;border-radius:80px;background:#070605" data-layout-ignore></div>
<div style="position:absolute;left:240px;top:572px;width:600px;height:1074px;border-radius:66px;overflow:hidden;background:#1c120c" data-layout-allow-overflow>
  <img id="s11-img" src="assets/hf/S11.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">
  <div style="position:absolute;inset:0;background:linear-gradient(180deg, rgba(0,0,0,.5) 0%, rgba(0,0,0,0) 16%, rgba(0,0,0,0) 78%, rgba(0,0,0,.55) 100%)"></div>
  <svg style="position:absolute;inset:0;width:100%;height:100%" viewBox="0 0 600 1074"><g fill="none" stroke="rgba(255,255,255,.85)" stroke-width="4" stroke-linecap="round">
    <path d="M70 250 V200 H120 M480 200 H530 V250 M530 800 V850 H480 M120 850 H70 V800"/></g>
    <circle cx="300" cy="975" r="46" fill="none" stroke="#fff" stroke-width="5"/><rect id="s11-rec" x="279" y="954" width="42" height="42" rx="9" fill="#e23b2e"/></svg>
  <div style="position:absolute;left:50%;top:22px;width:170px;height:44px;margin-left:-85px;border-radius:22px;background:#000"></div>
  <div style="position:absolute;top:88px;left:0;right:0;text-align:center;direction:ltr"><span style="display:inline-block;padding:4px 20px 5px;border-radius:12px;background:#e23b2e;font-family:Heebo,sans-serif;font-weight:600;font-size:34px;color:#fff;line-height:1.2">
    <span id="s11-dot" style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#fff;margin-right:12px;vertical-align:3px"></span>00:0<span id="s11-sec" style="display:inline-block;width:.62em;text-align:left">3</span></span></div>
  <div id="s11-flash" style="position:absolute;inset:0;background:#fff8e8;opacity:0"></div>
</div>
""", css="#root { --glow: 40%; }", js=f"""
for (let k = 0; k < 8; k++) tl.set("#s11-sec", {{ textContent: String(3 + k) }}, k * {BEAT} - 1e-4 < 0 ? 0 : k * {BEAT});
for (let k = 0; k < 16; k++) tl.set("#s11-dot", {{ opacity: k % 2 ? 0.2 : 1 }}, k * {BEAT / 2});
for (const [t, s0, s1] of [[{beat(1)}, 1.0, 1.08], [{beat(5)}, 1.03, 1.12]]) {{
  tl.fromTo("#s11-flash", {{ opacity: 0 }}, {{ opacity: 0.92, duration: 0.042, ease: "none", immediateRender: false }}, t);
  tl.to("#s11-flash", {{ opacity: 0, duration: 0.42, ease: "power2.out" }}, t + 0.042);
  tl.fromTo("#s11-img", {{ scale: s0 }}, {{ scale: s1, duration: 0.3, ease: "power2.out", immediateRender: false }}, t);
  tl.to("#s11-img", {{ scale: s1 - 0.05, duration: 2.0, ease: "power1.inOut" }}, t + 0.3);
}}
""")
sfx("s11", beat(1), "click", .9)
sfx("s11", beat(5), "click", .9)


# ===== 12. The end card =====

def arc_rows(dx0, dy0, n, lift=150, s0=0.55):
    """A die tossed from the hand in an arc: it lands at its rest spot and takes two small bounces."""
    rows = []
    for i in range(n + 1):
        u = i / n
        e = 1 - (1 - u) ** 2.2
        b = 26 * abs(math.sin(math.pi * 2 * (u - 0.72) / 0.28)) * (1 - u) / 0.28 if u > 0.72 else 0
        rows.append([r1(dx0 * (1 - e)), r1(dy0 * (1 - e) - lift * math.sin(math.pi * min(1, u / 0.72)) * (1 - e * 0.5) - b), round(s0 + (1 - s0) * e, 3), 1])
    return rows


_ea, _eb = arc_rows(330, 860, 26), arc_rows(190, 850, 28)
_t12 = 7 / FPS
card("s12", 10, f"""
<svg class="art" style="left:0;top:0;width:1080px;height:1920px;opacity:.13" viewBox="0 0 1080 1920" data-layout-ignore>
  <path d="M0 1010 L180 730 L300 870 L470 590 L640 850 L760 710 L1080 1010 L1080 1920 L0 1920 Z" fill="{GOLD}"/></svg>
{logo_svg("s12-logo", 325, 146, 430)}
{shadow("s12-shA", 482, 826, 160)}{shadow("s12-shB", 608, 832, 160)}
{die("s12-dA", 6, 478, 772, 112, "a", -10)}{die("s12-dB", 6, 604, 778, 112, "b", 8)}
<div class="h foil" id="s12-title" style="top:862px;font-size:100px">הטילו את הקוביות</div>
<div class="sub" style="top:984px;font-size:54px">האפי האוור · <span class="ltr">16:00–18:00</span></div>
<div style="position:absolute;left:0;right:0;top:1072px;text-align:center"><span id="s12-cta" style="display:inline-block;padding:10px 58px 12px;border:3px solid {GOLD};border-radius:999px;font-family:Heebo,sans-serif;font-weight:700;font-size:48px;color:{IVORY};background:rgba(11,9,7,.5);box-shadow:inset 0 0 0 5px rgba(11,9,7,.6), inset 0 0 0 6px rgba(201,163,107,.45)">הזמינו שולחן</span></div>
<div style="position:absolute;left:96px;right:96px;top:1172px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:40px;color:#ddd2c0">אחוזה 124, רעננה · <span class="ltr">@[instagram]</span></div>
<div style="position:absolute;left:80px;right:80px;top:1246px;text-align:center;font-family:Heebo,sans-serif;font-weight:400;font-size:34px;line-height:1.3;color:{GOLD}">בכפוף לתקנון. את התקנון המלא אפשר לבקש מהמלצר.</div>
{hand("s12-hand", 800, 1660, 400, "fist")}
""", css="#root { --glow: 24%; }", js=f"""
DiceKit.pose(tl, "#s12-hand", "fist", 0); DiceKit.pose(tl, "#s12-hand", "release", {_t12:.4f}); DiceKit.pose(tl, "#s12-hand", "open", {_t12 + 3 / FPS:.4f});
tl.fromTo("#s12-hand", {{ y: 240, rotation: 10 }}, {{ y: -40, rotation: -8, duration: {_t12:.4f}, ease: "power3.out" }}, 0);
tl.to("#s12-hand", {{ y: 0, duration: 0.35, ease: "power1.out" }}, {_t12:.4f});
tl.to("#s12-hand", {{ y: 720, rotation: 4, duration: 0.8, ease: "power2.in" }}, {_t12 + 0.35:.4f});
tl.set(["#s12-dA", "#s12-dB", "#s12-shA", "#s12-shB"], {{ opacity: 0 }}, 0);
tl.set(["#s12-dA", "#s12-dB"], {{ opacity: 1 }}, {_t12:.4f} - 1e-4);
tl.fromTo(["#s12-shA", "#s12-shB"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.in" }}, {_t12 + 0.75:.4f});
""" + js_bake("#s12-dA", _t12, ["x", "y", "scale", "opacity"], _ea) + js_spin("#s12-dA", _t12, 6, spin_keys(26) + [-1])
    + js_bake("#s12-dB", _t12, ["x", "y", "scale", "opacity"], _eb) + js_spin("#s12-dB", _t12, 6, spin_keys(28) + [-1])
    + f"""
tl.fromTo("#s12-title", {{ backgroundPosition: "100% 0" }}, {{ backgroundPosition: "0% 0", duration: 1.6, ease: "power2.inOut" }}, {beat(3):.4f});
tl.fromTo("#s12-cta", {{ scale: 1 }}, {{ scale: 1.07, duration: 0.3125, ease: "power2.out", yoyo: true, repeat: 1 }}, {beat(6):.4f});
tl.fromTo("#s12-logo", {{ scale: 1, transformOrigin: "50% 50%" }}, {{ scale: 1.03, duration: {beat(4):.4f}, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {beat(2):.4f});
tl.to("#s12-cta", {{ scale: 1.07, duration: 0.3125, ease: "power2.out", yoyo: true, repeat: 1 }}, {beat(8):.4f});
""")
sfx("s12", _t12, "whoosh", .8)
sfx("s12", _t12 + 26 / FPS * 0.72, "click-soft", .9)
sfx("s12", beat(3), "impact-bass-1", .7)
sfx("s12", beat(3), "sparkle", .5)


# ---------- assembly ----------
INTRO_IDS = ("p1", "p2", "p3")
_t = 0.0
for c in CARDS:
    c["start"] = round(_t, 4)
    _t += c["dur"]
TOTAL = round(_t, 4)
INTRO = round(sum(c["dur"] for c in CARDS if c["id"] in INTRO_IDS), 4)
START = {c["id"]: c["start"] for c in CARDS}
# (start, duration, file) of the three opening clips, already fitted to 1080x1920 at 24 fps.
CLIPS = [(START["p1"], beat(5), "P1-fit.mp4"), (START["p2"], beat(6), "P2-fit.mp4"), (START["p3"], P3_CUT, "P3-fit.mp4")]
SFX_LEN = {k: v["duration"] for k, v in json.load(open(ROOT / "assets/sfx/manifest.json")).items()}


def composition(c):
    ids = ["#" + chunk.split('"', 1)[0] for chunk in c["body"].split('<div id="')[1:] if chunk.split('"', 1)[1].startswith(' class="die"')]
    mount = f"DiceKit.mount({J(ids)});" if ids else ""
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
    # two dice can land on the same frame: one cue is enough (the louder one)
    merged = {}
    for cid, t, f, v in SFX:
        key = (round(fr(START[cid] + t), 3), f)
        merged[key] = max(v, merged.get(key, 0))
    cues = sorted((t, f, v) for (t, f), v in merged.items())
    audio = "\n".join(
        f'      <audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}.mp3" data-start="{t}" data-duration="{SFX_LEN[f]}" data-track-index="{40 + i}" data-volume="{v}"></audio>'
        for i, (t, f, v) in enumerate(cues))
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
    <!-- Generated by build.py (v6): the opening clips, 14 Noir & Or cards, Hebrew only. Edit build.py, not this file. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="24">
{clips}
{hosts}
{audio}
      <div id="frame" style="z-index:50" data-composition-id="frame" data-composition-src="compositions/frame.html" data-start="{INTRO}" data-duration="{round(TOTAL - INTRO, 4)}" data-track-index="20" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


CORNER = "M0 46 V0 H46 M0 18 H18 V0"
FRAME = f"""<template>
  <style>
    @font-face {{ font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-latin.woff2') format('woff2'); }}
    @font-face {{ font-family: "Heebo"; font-weight: 100 900; font-display: block; src: url('assets/fonts/heebo-normal-hebrew.woff2') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+FB1D-FB4F; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #frame-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    #frame-legal {{ position: absolute; left: 0; right: 0; top: 1812px; text-align: center; direction: rtl; }}
    #frame-legal span {{ display: inline-block; padding: 4px 24px 5px; border-radius: 999px; background: rgba(11,9,7,.74); box-shadow: inset 0 0 0 1px rgba(201,163,107,.35);
      font-family: "Heebo", sans-serif; font-weight: 500; font-size: 28px; color: {GOLD_HI}; }}
  </style>
  <div id="root" data-composition-id="frame" data-width="1080" data-height="1920">
    <!-- The posters' double gold rule with stepped corners, and the house-rules note, on every card from the first frame -->
    <svg id="frame-svg" viewBox="0 0 1080 1920" data-layout-ignore>
      <rect x="24" y="24" width="1032" height="1872" fill="none" stroke="{GOLD}" stroke-width="2"/>
      <rect x="33" y="33" width="1014" height="1854" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-width="1"/>
      <g fill="none" stroke="{GOLD_HI}" stroke-width="2">
        <path d="{CORNER}" transform="translate(44 44)"/><path d="{CORNER}" transform="translate(1036 44) scale(-1 1)"/>
        <path d="{CORNER}" transform="translate(44 1876) scale(1 -1)"/><path d="{CORNER}" transform="translate(1036 1876) scale(-1 -1)"/></g>
    </svg>
    <svg id="frame-grain" viewBox="0 0 540 960" preserveAspectRatio="none" data-layout-ignore style="position:absolute;inset:0;width:100%;height:100%;opacity:.11;mix-blend-mode:overlay">
      <filter id="frame-noise"><feTurbulence id="frame-turb" type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="1"/><feColorMatrix type="saturate" values="0"/></filter>
      <rect width="540" height="960" filter="url(#frame-noise)"/>
    </svg>
    <div id="frame-legal" data-layout-allow-caption-zone><span>*בכפוף לתקנון</span></div>
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const turb = document.getElementById("frame-turb");
      for (let k = 0; k < {int((TOTAL - INTRO) * 12)}; k++) tl.set(turb, {{ attr: {{ seed: (k * 7) % 97 + 1 }} }}, k / 12);
      window.__timelines["frame"] = tl;
    }})();
  </script>
</template>
"""

if __name__ == "__main__":
    # every cut on a beat, every cue inside its card
    for c in CARDS:
        assert abs(c["start"] / BEAT - round(c["start"] / BEAT)) < 1e-6, f'{c["id"]} does not start on a beat'
    for cid, t, f, v in SFX:
        assert f in SFX_LEN, f"unknown effect {f}"
        assert -1e-6 <= t, f"{cid}: cue before the card"
    for c in CARDS:
        (ROOT / "compositions" / f'{c["id"]}.html').write_text(composition(c))
    (ROOT / "compositions" / "frame.html").write_text(FRAME)
    (ROOT / "index.html").write_text(index())
    print(f"built {len(CARDS)} cards, {TOTAL}s ({TOTAL / BEAT:.0f} beats), {len(SFX)} sound cues")
