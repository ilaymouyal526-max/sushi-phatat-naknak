"""Wrap the real Yoko Ono logo onto the blank round label of a Push Pop draft.
Local only, no credits. Cylindrical wrap + shading taken from the blank label itself."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter

src, logo_path, out, cfg = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
img = Image.open(src).convert('RGB')
A = np.asarray(img).astype(np.float32)
H, W = A.shape[:2]

tube_cx, R = cfg['tube_cx'], cfg['R']
lcx, lcy = cfg['lcx'], cfg['lcy']
fit_r = cfg['fit_r']                      # radius (px, unwrapped) the logo must fit in
theta0 = np.arcsin(np.clip((lcx - tube_cx) / R, -1, 1))

# ---- logo alpha, trimmed, measured
logo = Image.open(logo_path).getchannel('A')
bb = logo.getbbox(); logo = logo.crop(bb)
la = np.asarray(logo).astype(np.float32) / 255
ys, xs = np.nonzero(la > 0.5)
lc_x, lc_y = la.shape[1] / 2, la.shape[0] / 2
rmax = np.sqrt((xs - lc_x) ** 2 + (ys - lc_y) ** 2).max()
SS = 4                                     # supersampling per output px
scale = fit_r / rmax                       # output px per logo px
# resample logo so 1 output px == SS logo px
k = scale * SS
logo_s = logo.resize((max(1, round(logo.width * k)), max(1, round(logo.height * k))), Image.LANCZOS)
ls = np.asarray(logo_s).astype(np.float32) / 255
lcx_s, lcy_s = ls.shape[1] / 2, ls.shape[0] / 2

# ---- output region
x0, x1 = int(lcx - fit_r * 1.3), int(lcx + fit_r * 1.3)
y0, y1 = int(lcy - fit_r * 1.2), int(lcy + fit_r * 1.2)
sub = (np.arange(SS) + 0.5) / SS
gx = (np.arange(x0, x1)[:, None] + sub[None, :]).ravel()
gy = (np.arange(y0, y1)[:, None] + sub[None, :]).ravel()
X, Y = np.meshgrid(gx, gy)
inside_tube = np.abs(X - tube_cx) < R * 0.995
theta = np.arcsin(np.clip((X - tube_cx) / R, -1, 1))
u = R * (theta - theta0)                   # unwrapped horizontal distance from label centre
v = Y - lcy
sx = np.round(u * SS + lcx_s).astype(int); sy = np.round(v * SS + lcy_s).astype(int)
ok = inside_tube & (sx >= 0) & (sx < ls.shape[1]) & (sy >= 0) & (sy < ls.shape[0])
alpha_ss = np.zeros_like(X); alpha_ss[ok] = ls[sy[ok], sx[ok]]
# foreshortening: surfaces turning away get slightly dimmer edges, handled by shading below
alpha = alpha_ss.reshape(y1 - y0, SS, x1 - x0, SS).mean(axis=(1, 3))
vn = (v.reshape(y1 - y0, SS, x1 - x0, SS).mean(axis=(1, 3))) / fit_r     # -1 top .. 1 bottom

# ---- shading from the blank label
lum = A[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
L = Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8))
Lb = np.asarray(L.filter(ImageFilter.GaussianBlur(5))).astype(np.float32)
Lf = np.asarray(L.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)
reg = (slice(y0, y1), slice(x0, x1))
lab = alpha > 0.05
med = np.median(Lb[reg][lab]) if lab.any() else Lb[reg].mean()
shade = np.clip(Lb[reg] / med, 0.45, 1.7)
texture = (Lf[reg] - Lb[reg]) * 0.9        # paper grain shows through the foil

# ---- gold foil colour: warm gradient + sheen that follows the light
top = np.array([238, 208, 150], np.float32); mid = np.array([206, 166, 102], np.float32); bot = np.array([150, 112, 62], np.float32)
t = np.clip((vn + 1) / 2, 0, 1)[..., None]
gold = np.where(t < 0.5, top + (mid - top) * (t / 0.5), mid + (bot - mid) * ((t - 0.5) / 0.5))
col = gold * (shade[..., None] ** 0.85) * cfg.get('gain', 0.82) + np.clip(shade - 1, 0, None)[..., None] * 70 + texture[..., None]
col = np.clip(col, 0, 255)

a = (alpha * cfg.get('opacity', 0.96))[..., None]
A[reg] = A[reg] * (1 - a) + col * a
res = Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))
# match the photo's softness on the logo area only
soft = res.filter(ImageFilter.GaussianBlur(0.35))
m = Image.fromarray((np.pad(alpha, ((y0, H - y1), (x0, W - x1))) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
res.paste(soft, (0, 0), m)
res.save(out)
print('logo scale', round(scale, 4), 'theta0', round(float(theta0), 3), 'region', x0, y0, x1, y1)
