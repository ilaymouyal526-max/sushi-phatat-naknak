# Build the photo texture set for the 3D trays: seamless colour tiles, cut-face decals,
# and per-texture normal + roughness maps made from the photo's brightness.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FILL = '../fill/'
OUT = '../trays/assets/'

def seamless(im, feather):
    a = np.asarray(im).astype(float); n = a.shape[0]
    sh = np.roll(np.roll(a, n//2, 0), n//2, 1)
    d = np.minimum(np.arange(n), np.arange(n)[::-1]); w1 = np.clip(d/feather, 0, 1)
    w = np.minimum.outer(w1, w1)[..., None]
    return Image.fromarray((a*w + sh*(1-w)).clip(0, 255).astype('uint8'))

def height(im, blur):
    g = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(blur))).astype(float)/255
    return g

def normal_map(im, size, strength, blur=1.2, wrap=True):
    h = height(im.resize((size, size), Image.LANCZOS), blur)
    if wrap:
        dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1))/2; dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0))/2
    else:
        dx = np.gradient(h, axis=1); dy = np.gradient(h, axis=0)
    k = strength*size/512
    nx, ny, nz = -dx*k, dy*k, np.ones_like(h)   # green up (three.js / OpenGL), image rows run down
    l = np.sqrt(nx*nx + ny*ny + nz*nz)
    rgb = np.stack([nx/l, ny/l, nz/l], -1)*0.5 + 0.5
    return Image.fromarray((rgb*255).clip(0, 255).astype('uint8'))

def rough_map(im, size, base, spread):
    a = np.asarray(im.resize((size, size), Image.LANCZOS).convert('RGB')).astype(float)/255
    lum = a.mean(-1); sat = a.max(-1) - a.min(-1)
    local = np.asarray(Image.fromarray((lum*255).astype('uint8')).filter(ImageFilter.GaussianBlur(6))).astype(float)/255
    detail = lum - local                                   # bright glints read glossy, crevices rough
    glint = np.clip((lum - 0.8)*4, 0, 1)*np.clip(1 - sat*3, 0, 1)
    r = np.clip(base - detail*spread*2 - glint*0.25, 0.05, 1)
    g = (r*255).astype('uint8'); z = np.zeros_like(g)
    return Image.fromarray(np.stack([z, g, z], -1))        # three.js reads roughness from G

def save(im, name, q=84):
    im.save(OUT + name, 'WEBP', quality=q, method=6)

# ---- surface tiles (1024, from the full-size originals) ----
TILES = {'rice': (3.0, .55), 'ses': (3.0, .55), 'pink': (4.0, .85), 'flake': (4.0, .85),
         'tempura': (4.0, .75), 'avo': (2.0, .35), 'nori': (3.0, .6)}
for k, (st, rb) in TILES.items():
    im = seamless(Image.open(FILL + f'orig/f_t_{k}.jpg').convert('RGB'), 160)
    save(im, f'tile-{k}.webp', 84)
    save(normal_map(im, 1024, st), f'tilen-{k}.webp', 80)
    save(rough_map(im, 512, rb, .6), f'tiler-{k}.webp', 80)

# ---- fillings (2048 colour from four quarters, 1024 normal, 512 roughness) ----
FILLS = {0: ('sear', 2.5, .45), 1: ('cooked', 3.0, .7), 2: ('spicy', 2.0, .4), 3: ('tunamayo', 2.5, .6),
         4: ('avo', 1.5, .35), 5: ('cuc', 1.5, .25), 6: ('carrot', 1.5, .4), 7: ('onion', 2.5, .4), 8: ('salmon', 1.5, .35)}
for i, (k, st, rb) in FILLS.items():
    big = Image.new('RGB', (2048, 2048))
    for q, (x, y) in enumerate([(0, 0), (1024, 0), (0, 1024), (1024, 1024)]):
        big.paste(Image.open(FILL + f'q/q{i}_{q}.jpg').convert('RGB'), (x, y))
    big = seamless(big, 320)
    save(big, f'fill-{k}.webp', 82)
    save(normal_map(big, 1024, st), f'filln-{k}.webp', 80)
    save(rough_map(big, 512, rb, .6), f'fillr-{k}.webp', 80)

# ---- cut faces (1024 RGBA decal on black, 512 normal) ----
FACES = ['pnk', 'ses', 'ins', 'drg', 'tmp', 'tmy', 'sap', 'sat', 'vgp', 'tmc']
for k in FACES:
    im = Image.open(FILL + f'orig/f_{k}.jpg').convert('RGB'); a = np.asarray(im).astype(int)
    mask = a.max(axis=2) > 45; ys, xs = np.where(mask)
    x0, x1 = np.percentile(xs, [0.3, 99.7]); y0, y1 = np.percentile(ys, [0.3, 99.7])
    cx, cy = (x0+x1)/2, (y0+y1)/2; r = max(x1-x0, y1-y0)/2*1.01
    c = im.crop((int(cx-r), int(cy-r), int(cx+r), int(cy+r))).resize((1024, 1024), Image.LANCZOS)
    m = Image.new('L', (4096, 4096), 0); ImageDraw.Draw(m).ellipse((8, 8, 4088, 4088), fill=255); m = m.resize((1024, 1024), Image.LANCZOS)
    fg = Image.fromarray(((np.asarray(c).max(axis=2) > 38)*255).astype('uint8')).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
    alpha = Image.fromarray(np.minimum(np.asarray(m), np.asarray(fg)).astype('uint8'))
    save(normal_map(c, 512, 3.0, 1.0, wrap=False), f'facen-{k}.webp', 80)
    c.putalpha(alpha); save(c, f'face-{k}.webp', 86)
# the two real-photo maki faces keep their decals; give them normals too
for k in ['mcc', 'nmk']:
    c = Image.open(OUT + f'face-{k}.webp').convert('RGB')
    save(normal_map(c, 512, 3.0, 1.0, wrap=False), f'facen-{k}.webp', 80)
print('done')
