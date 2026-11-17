"""Director's finishing pass: 16:9 AI sushi ad -> 9:16 cinematic social cut.

Usage: python3 finish_v2.py <source_16x9.mp4> <out_9x16.mp4>
Needs ffmpeg, numpy, Pillow. Techniques that break the "AI look":
  virtual camera (push-ins, slide, handheld weave + roll), speed ramps with frame blending,
  beat-locked cuts (96 BPM, 15 frames/beat), cut-around of AI morphs, light leak + flash cut,
  halation, film grade, grain, CA, vignette, synthesized foley + taiko score.
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
FPS, OW, OH, SW, SH, SR = 24, 1080, 1920, 1920, 1080, 48000
GOLD = (214, 178, 110)

# (out_frames, src_start_s, speed_start, speed_end, cx, cy, crop_w_start, crop_w_end, pan_px, title)
# Source map: hands 0-2.4s | flash 2.5 | torch 2.75-4.9 | AI morph 5.0-5.4 (avoided) | chopsticks 5.5-7.9
#             | sauce 8.5-11.1 | logo 11.5-14.
SHOTS = [
    (30, 3.55, .5, 1., 915, 575, 380, 330, 0, "FIRE"),     # hook: flame macro, speed ramp into real time
    (15, 2.85, 1., 1., 930, 540, 590, 560, 0, "FIRE"),     # torch medium, flash cut in
    (45, 0.05, .8, .8, 995, 540, 590, 530, 0, "CRAFT"),    # hands spread tuna, slow push
    (15, 1.72, 1., 1., 995, 497, 430, 400, 0, "CRAFT"),    # texture detail
    (45, 5.55, .6, .6, 990, 540, 590, 520, 0, None),       # chopsticks, 60% slow-mo
    (15, 6.80, 1., 1., 1004, 525, 440, 410, 0, None),      # crumbs macro
    (45, 8.55, .76, .76, 1000, 420, 470, 455, 90, None),   # sauce, lateral slider move
    (45, 10.05, .5, .5, 1003, 560, 470, 400, 0, None),     # hero dolly-in + tilt down, dip to black
]
LOGO_N, LOGO_T = 60, 11.40
CUTS = np.cumsum([0] + [s[0] for s in SHOTS])  # shot start frames; logo starts at CUTS[-1]
TOTAL = int(CUTS[-1]) + LOGO_N
YBOT = {6: 848, 7: 848}  # keep the source's burned-in "RED DRAGON TATAKI" super (rows 850-920) out of frame
LOGO_BOX = (394, 222, 1526, 859)  # logo bbox 698-1222 x 241-838, padded to 16:9


def decode(t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-i", SRC, "-t", f"{dur}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)


def font(size):
    try:
        path = subprocess.run(["fc-match", "-f", "%{file}", "Montserrat:light"], capture_output=True, text=True).stdout
        if "ontserrat" in path:
            return ImageFont.truetype(path, size)
    except OSError:
        pass
    import glob
    found = sorted(glob.glob("/usr/**/*ontserrat*.[ot]tf", recursive=True) + glob.glob("/home/**/*ontserrat*.[ot]tf", recursive=True),
                   key=lambda p: "Light" not in p)
    return ImageFont.truetype(found[0], size) if found else ImageFont.truetype("DejaVuSans.ttf", size)


def text_layer(txt, size, track):
    f = font(size)
    widths = [f.getlength(c) for c in txt]
    x = (OW - sum(widths) - track * size * (len(txt) - 1)) / 2
    im = Image.new("RGBA", (OW, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for c, w in zip(txt, widths):
        d.text((x, size * 0.4), c, font=f, fill=GOLD + (255,))
        x += w + track * size
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .7)))
    return im, shadow


def put(img, layer, y, alpha):
    if alpha <= 0:
        return
    for L in layer[::-1]:  # shadow first, then text
        L = L.copy()
        L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
        img.paste(L, (0, y), L)


def fade(k, a, b, n=5):
    return float(np.clip(min((k - a) / n, (b - k) / n), 0, 1))


TITLES = {"FIRE": text_layer("FIRE", 72, .45), "CRAFT": text_layer("CRAFT", 72, .45),
          "DISH": text_layer("RED DRAGON TATAKI", 52, .3)}
TSPAN = {"FIRE": (4, int(CUTS[2]) - 1), "CRAFT": (int(CUTS[2]) + 4, int(CUTS[4]) - 1),
         "DISH": (int(CUTS[6]) + 6, int(CUTS[8]) - 5)}


def leak(u):
    """Warm light leak drifting across the frame (screen-blended)."""
    yy, xx = np.mgrid[0:192, 0:108] / np.array([192, 108])[:, None, None]
    cx, cy = .95 - .7 * u, .12 + .25 * u
    v = np.exp(-((xx - cx) ** 2 + ((yy - cy) * .6) ** 2) / .09)
    rgb = (v[..., None] * np.array([1., .45, .12]) * .32 * np.sin(np.pi * u) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(rgb).resize((OW, OH), Image.BILINEAR), np.float32) / 255


def render_video(enc):
    g = 0
    for si, (n, t0, v0, v1, cx, cy, w0, w1, pan, title) in enumerate(SHOTS):
        fr = decode(t0, n / FPS * (v0 + v1) / 2 + .2)
        ph = np.random.default_rng(si).uniform(0, 2 * np.pi, 5)
        for k in range(n):
            u = k / max(n - 1, 1)
            st = n * (v0 * u + (v1 - v0) * u * u / 2)          # source frame (speed ramp integral)
            i0 = min(int(st), len(fr) - 1); i1 = min(i0 + 1, len(fr) - 1); a = st - int(st)
            src = fr[i0] if (min(v0, v1) >= 1 or a < .02) else (fr[i0] * (1 - a) + fr[i1] * a).astype(np.uint8)
            e = u * u * (3 - 2 * u)                               # ease in-out camera move
            w = w0 + (w1 - w0) * e; h = w * 16 / 9; s = w / OW; t = g / FPS
            dx = 2.6 * (.6 * np.sin(2 * np.pi * .55 * t + ph[0]) + .3 * np.sin(2 * np.pi * 1.3 * t + ph[1])
                        + .1 * np.sin(2 * np.pi * 3.1 * t + ph[2]))
            dy = 2.0 * (.6 * np.sin(2 * np.pi * .47 * t + ph[3]) + .4 * np.sin(2 * np.pi * 1.1 * t + ph[4]))
            roll = np.deg2rad(.12 * np.sin(2 * np.pi * .35 * t + ph[0]))
            ccx = float(np.clip(cx - pan / 2 + pan * e + dx, w / 2 + 3, SW - w / 2 - 3))
            ccy = float(np.clip(cy + dy, h / 2 + 3, YBOT.get(si, SH) - h / 2 - 3))
            A, B, D, E = s * np.cos(roll), -s * np.sin(roll), s * np.sin(roll), s * np.cos(roll)
            img = Image.fromarray(src).transform(
                (OW, OH), Image.AFFINE, (A, B, ccx - (A * OW / 2 + B * OH / 2), D, E, ccy - (D * OW / 2 + E * OH / 2)),
                resample=Image.BICUBIC)
            fx = None
            if g < CUTS[2]:                                       # light leak over the fire section
                fx = np.asarray(img, np.float32) / 255
                fx = 1 - (1 - fx) * (1 - leak(g / (CUTS[2] - 1)))
            if g in (CUTS[1], CUTS[1] + 1):                       # 2-frame exposure flash cut
                fx = (np.asarray(img, np.float32) / 255) if fx is None else fx
                fx = np.clip(fx * (2.0 if g == CUTS[1] else 1.35) + (.08 if g == CUTS[1] else .02), 0, 1)
            if si == len(SHOTS) - 1 and k >= n - 4:               # dip to black into the end card
                fx = (np.asarray(img, np.float32) / 255 if fx is None else fx) * ((n - 1 - k) / 4)
            if fx is not None:
                img = Image.fromarray((fx * 255).astype(np.uint8))
            for name, (a_, b_) in TSPAN.items():
                put(img, TITLES[name], 1380, fade(g, a_, b_))
            enc.stdin.write(img.tobytes())
            g += 1
        del fr
    fr = decode(LOGO_T, LOGO_N / FPS + .2)
    cta = text_layer("ORDER NOW", 60, .42)
    for k in range(LOGO_N):
        u = k / (LOGO_N - 1)
        wv = int(OW * (1 + .05 * u)); hv = int(wv * (LOGO_BOX[3] - LOGO_BOX[1]) / (LOGO_BOX[2] - LOGO_BOX[0]))
        lg = Image.fromarray(fr[min(k, len(fr) - 1)]).crop(LOGO_BOX).resize((wv, hv), Image.BICUBIC)
        if k < 12:                                                # focus-pull reveal
            lg = lg.filter(ImageFilter.GaussianBlur(14 * (1 - k / 12) ** 2))
        img = Image.new("RGB", (OW, OH))
        img.paste(lg, ((OW - wv) // 2, (OH - hv) // 2 - 60))
        al = float(np.clip((k - 16) / 10, 0, 1))
        put(img, cta, 1290, al)
        if al > 0:
            ImageDraw.Draw(img).rectangle([OW / 2 - 70, 1268, OW / 2 + 70, 1269], fill=tuple(int(c * al) for c in GOLD))
        enc.stdin.write(img.tobytes())


def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-3
    return np.fft.irfft(X / (1 + (lo / f) ** 4) / (1 + (f / hi) ** 4), len(x))


def render_audio(path):
    T = TOTAL / FPS; N = int(T * SR); out = np.zeros(N); rng = np.random.default_rng(7)
    ft = lambda fr: fr / FPS

    def add(sig, t0, gain):
        i = int(t0 * SR); j = min(N, i + len(sig))
        if i < N:
            out[i:j] += sig[:j - i] * gain

    def env(n, a, r):
        t = np.arange(n) / SR
        return np.minimum(t / a, 1) * np.exp(-t / r)

    def taiko(big=False):
        n = int((1.8 if big else .7) * SR); t = np.arange(n) / SR
        body = np.sin(2 * np.pi * np.cumsum(52 + 85 * np.exp(-t / .045)) / SR) * np.exp(-t / (.6 if big else .28))
        s = body + .5 * band(rng.standard_normal(n), 60, 1800) * np.exp(-t / .018)
        if big:
            s = s + sum(np.concatenate([np.zeros(int(d * SR)), s[:n - int(d * SR)]]) * gg
                        for d, gg in [(.031, .35), (.047, .3), (.071, .25), (.113, .2), (.167, .15), (.26, .1)])
        return s / np.abs(s).max()

    def ka():
        n = int(.12 * SR); t = np.arange(n) / SR
        s = (np.sin(2 * np.pi * 1850 * t) + .6 * np.sin(2 * np.pi * 3100 * t)) * np.exp(-t / .02)
        return s + .3 * band(rng.standard_normal(n), 2000, 9000) * np.exp(-t / .006)

    def clicks(t0, dur, rate, lo, hi, gain):
        for tt in np.sort(rng.uniform(t0, t0 + dur, int(rate * dur))):
            n = int(.004 * SR)
            add(band(rng.standard_normal(n * 4), lo, hi)[:n] * np.exp(-np.arange(n) / (SR * .001)), tt, gain * rng.uniform(.3, 1))

    # score: taiko "don" on long shots, rim "ka" on the 1-beat shots, big hit on the logo
    for i, c in enumerate(CUTS[:-1]):
        add(ka() if SHOTS[i][0] == 15 else taiko(), ft(c), .35 if SHOTS[i][0] == 15 else (.8 if i == 0 else .55))
    add(taiko(True), ft(CUTS[-1]), 1.0)
    for fr in np.arange(CUTS[2], CUTS[-1], 7.5):  # shaker 8ths
        n = int(.08 * SR)
        add(band(rng.standard_normal(n), 5000, 14000) * env(n, .004, .03), ft(fr), .12 if fr % 15 == 0 else .07)
    t = np.arange(N) / SR
    drone = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(73.42, 1), (110, .5), (146.84, .3)])
    add(drone * (.5 + .5 * np.sin(2 * np.pi * .2 * t)) * np.clip(t / 2, 0, 1)
        * np.where(t < ft(CUTS[-1]), .05 + .05 * t / ft(CUTS[-1]), .06 * np.exp(-(t - ft(CUTS[-1])) / 1.2)), 0, 1)
    # foley
    n = int(ft(CUTS[2]) * SR); tt = np.arange(n) / SR
    add(band(rng.standard_normal(n), 1200, 9000) * (.7 + .3 * np.sin(2 * np.pi * 14 * tt))
        * np.clip(tt / .05, 0, 1) * np.clip((tt[-1] - tt) / .1, 0, 1), 0, .16)          # torch hiss
    clicks(0, ft(CUTS[2]) + .1, 70, 2000, 8000, .5)                                     # sear crackle
    n = int(ft(CUTS[4] - CUTS[2]) * SR); tt = np.arange(n) / SR
    add(band(rng.standard_normal(n), 600, 3500) * (.5 + .5 * np.sin(2 * np.pi * .9 * tt)) ** 2, ft(CUTS[2]), .05)  # spreading
    add(ka(), ft(CUTS[4]) + .9, .22); add(ka(), ft(CUTS[4]) + 1.05, .12)               # chopstick clicks
    clicks(ft(CUTS[5]), ft(15), 50, 3000, 12000, .25)                                  # crumb patter
    n = int(ft(45) * SR)
    add(band(rng.standard_normal(n), 150, 700) * np.sin(np.pi * np.arange(n) / n), ft(CUTS[6]), .08)  # sauce pour
    n = int(.45 * SR)
    add(band(rng.standard_normal(n), 400, 6000) * (np.arange(n) / n) ** 2, ft(CUTS[-1]) - .45, .3)   # whoosh
    add(band(np.cumsum(rng.standard_normal(N)), 30, 2500) / 400, 0, .015)             # room tone
    out /= np.abs(out).max() * 1.12
    pcm = (np.repeat(out[:, None], 2, 1) * 32767).astype("<i2")
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


GRADE = (
    "[0:v]format=gbrp,split[b][h];"
    "[h]format=yuv444p,lutyuv=y='clip((val-185)*3.5,0,255)':u=128:v=128,format=gbrp,gblur=sigma=30,"
    "colorchannelmixer=rr=1:gg=0.36:bb=0.1[hl];"                                   # halation key
    "[b][hl]blend=all_mode=screen:all_opacity=0.30,"
    "curves=master='0/0.035 0.3/0.27 0.6/0.63 1/0.965',"                           # filmic S, lifted blacks
    "colorbalance=bs=0.035:rm=0.035:gm=0.006:bm=-0.03:rh=0.02:bh=-0.025,"          # cool shadows, warm mids
    "vibrance=intensity=0.16,rgbashift=rh=-2:bh=2,format=yuv444p,vignette=angle=PI/5,"
    "unsharp=5:5:0.4,noise=c0s=10:c0f=t:c1s=4:c1f=t:c2s=4:c2f=t,format=yuv420p[v];"  # grain
    "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]"
)

if __name__ == "__main__":
    render_audio("audio.wav")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                            "-r", str(FPS), "-i", "-", "-i", "audio.wav", "-filter_complex", GRADE, "-map", "[v]",
                            "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-tune", "grain", "-maxrate", "30M", "-bufsize", "60M", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT],
                           stdin=subprocess.PIPE)
    render_video(enc)
    enc.stdin.close()
    sys.exit(enc.wait())
