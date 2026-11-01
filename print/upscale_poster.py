#!/usr/bin/env python3
"""Upscale a single-image print PDF locally and rebuild its QR code as vectors.

Built for the YOKO ONO "Menu QR" poster (80 x 100 cm). The PDF holds one JPEG
that is only a soft 4x enlargement of a ~1232x1536 original, so it prints at
an effective ~39 ppi. This script:

  1. pulls the JPEG out of the PDF without re-encoding,
  2. shrinks it back to its real resolution and runs Real-ESRGAN (ncnn, CPU),
  3. resizes to the final print size (default ~313 ppi at 80 x 100 cm),
  4. decodes the QR code, regenerates it pixel-perfect (same link, same error
     correction, closest mask) and paints it into the raster AND as vectors
     on top of it in the PDF,
  5. writes a print PDF of the exact original page size plus a full-res JPEG.

Everything runs locally; no paid services.

Requirements (Python <= 3.12 because of realesrgan-ncnn-py wheels):
    pip install realesrgan-ncnn-py numpy Pillow zxing-cpp segno reportlab
    apt-get install libomp5          # runtime for realesrgan-ncnn-py

Usage:
    python upscale_poster.py INPUT.pdf OUTDIR [--model anime|x4plus|animevideo]
                             [--native-factor 4] [--final-scale 2] [--name NAME]
"""
from __future__ import annotations

import argparse
import base64
import io
import re
import time
from pathlib import Path

import numpy as np
import segno
import zxingcpp
from PIL import Image
from reportlab import rl_config
from reportlab.pdfgen import canvas

Image.MAX_IMAGE_PIXELS = None
MODELS = {"animevideo": 2, "anime": 3, "x4plus": 4}  # realesrgan-ncnn-py model ids (all x4)


# --------------------------------------------------------------------------- PDF in
def extract_pdf_image(pdf_path: Path) -> tuple[bytes, tuple[float, float]]:
    """Return the embedded JPEG bytes and the page size in points."""
    data = pdf_path.read_bytes()
    media = re.search(rb"/MediaBox\s*\[\s*([\d.\s-]+)\]", data)
    x0, y0, x1, y1 = (float(v) for v in media.group(1).split())
    page = (x1 - x0, y1 - y0)

    filt = re.search(rb"/Filter\s*(\[[^\]]*\]|/\w+)", data)
    filters = re.findall(rb"/(\w+)", filt.group(1))
    start = data.find(b"stream", filt.end()) + len(b"stream")
    while data[start:start + 1] in b"\r\n":
        start += 1
    end = data.find(b"endstream", start)
    raw = data[start:end].rstrip(b"\r\n")
    if b"ASCII85Decode" in filters:
        raw = base64.a85decode(b"<~" + raw[: raw.rfind(b"~>")] + b"~>", adobe=True)
    if b"DCTDecode" not in filters:
        raise SystemExit(f"unsupported image filters: {filters}")
    return raw, page


# --------------------------------------------------------------------------- QR
def find_qr(img: Image.Image) -> dict:
    """Decode the QR and measure its exact module box in image pixels."""
    hits = [r for r in zxingcpp.read_barcodes(img) if r.format == zxingcpp.BarcodeFormat.QRCode]
    if not hits:
        raise SystemExit("QR code could not be decoded - refusing to guess its content")
    hit = hits[0]
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    p = hit.position
    xs = [p.top_left.x, p.top_right.x, p.bottom_left.x, p.bottom_right.x]
    ys = [p.top_left.y, p.top_right.y, p.bottom_left.y, p.bottom_right.y]
    pad = 40
    sx0, sx1, sy0, sy1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    dy, dx = np.where(gray[sy0:sy1, sx0:sx1] < 128)
    box = (sx0 + dx.min(), sy0 + dy.min(), sx0 + dx.max() + 1, sy0 + dy.max() + 1)

    ec = {"L": "l", "M": "m", "Q": "q", "H": "h"}[str(hit.ec_level)]
    best = None
    for mask in range(8):
        q = segno.make(hit.text, error=ec, boost_error=False, micro=False, mask=mask)
        m = np.array([[bool(v) for v in row] for row in q.matrix])
        n = m.shape[0]
        mw, mh = (box[2] - box[0]) / n, (box[3] - box[1]) / n
        grid = np.zeros_like(m)
        for r in range(n):
            for c in range(n):
                yy, xx = int(box[1] + (r + 0.5) * mh), int(box[0] + (c + 0.5) * mw)
                grid[r, c] = gray[yy - 3:yy + 4, xx - 3:xx + 4].mean() < 128
        diff = int((grid != m).sum())
        if best is None or diff < best[0]:
            best = (diff, mask, m)
    diff, mask, matrix = best
    print(f"QR: {hit.text!r}  ec={hit.ec_level}  {matrix.shape[0]}x{matrix.shape[0]} modules  "
          f"mask={mask}  modules differing from a clean code: {diff}/{matrix.size}")
    return {"text": hit.text, "box": box, "matrix": matrix}


def paint_qr_raster(img: Image.Image, qr: dict, scale: float) -> None:
    """Paint a pixel-perfect QR (plus a white margin) into the upscaled raster."""
    m = qr["matrix"]
    n = m.shape[0]
    x0, y0, x1, y1 = (v * scale for v in qr["box"])
    mod = (x1 - x0) / n
    arr = np.asarray(img).copy()
    q = int(round(2 * mod))  # 2-module white margin, stays inside the white card
    arr[int(round(y0)) - q:int(round(y1)) + q, int(round(x0)) - q:int(round(x1)) + q] = 255
    for r in range(n):
        for c in range(n):
            if m[r, c]:
                arr[int(round(y0 + r * mod)):int(round(y0 + (r + 1) * mod)),
                    int(round(x0 + c * mod)):int(round(x0 + (c + 1) * mod))] = 0
    img.paste(Image.fromarray(arr))


def draw_qr_vector(c: canvas.Canvas, qr: dict, img_size: tuple[int, int], page: tuple[float, float]) -> None:
    """Draw the QR as filled vector rectangles over the raster (y axis flipped)."""
    m = qr["matrix"]
    n = m.shape[0]
    kx, ky = page[0] / img_size[0], page[1] / img_size[1]
    x0, y0, x1, y1 = qr["box"]
    mod_x, mod_y = (x1 - x0) * kx / n, (y1 - y0) * ky / n
    left, top = x0 * kx, page[1] - y0 * ky
    c.setFillColorRGB(1, 1, 1)
    c.rect(left - 2 * mod_x, top - (n + 2) * mod_y, (n + 4) * mod_x, (n + 4) * mod_y, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    path = c.beginPath()
    for r in range(n):
        col = 0
        while col < n:
            if m[r, col]:
                run = col
                while run < n and m[r, run]:
                    run += 1
                path.rect(left + col * mod_x, top - (r + 1) * mod_y, (run - col) * mod_x, mod_y)
                col = run
            else:
                col += 1
    c.drawPath(path, stroke=0, fill=1)


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--model", choices=MODELS, default="anime")
    ap.add_argument("--native-factor", type=int, default=4,
                    help="how much the embedded image was already blown up (default 4)")
    ap.add_argument("--final-scale", type=float, default=2.0,
                    help="final size relative to the embedded image (default 2 -> ~313 ppi)")
    ap.add_argument("--name", default="YOKO_ONO_QR_80x100_UPSCALED")
    ap.add_argument("--tilesize", type=int, default=200)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    from realesrgan_ncnn_py import Realesrgan  # heavy import, keep it after arg parsing

    jpg, page = extract_pdf_image(args.pdf)
    src = Image.open(io.BytesIO(jpg)).convert("RGB")
    print(f"embedded image {src.size}, page {page[0]:.2f} x {page[1]:.2f} pt")
    qr = find_qr(src)

    native = src.resize((src.width // args.native_factor, src.height // args.native_factor), Image.BOX)
    print(f"native resolution {native.size}; running Real-ESRGAN '{args.model}' on CPU ...")
    t = time.time()
    up = Realesrgan(gpuid=-1, model=MODELS[args.model], tilesize=args.tilesize).process_pil(native)
    print(f"\nupscaled to {up.size} in {(time.time() - t) / 60:.1f} min")

    final = (round(src.width * args.final_scale), round(src.height * args.final_scale))
    if up.size != final:
        up = up.resize(final, Image.LANCZOS)
    paint_qr_raster(up, qr, final[0] / src.width)
    ppi = final[0] / (page[0] / 72)
    print(f"final raster {final}  (~{ppi:.0f} ppi at print size)")

    jpg_out = args.outdir / f"{args.name}.jpg"
    up.save(jpg_out, quality=95, subsampling=0, dpi=(ppi, ppi))

    rl_config.useA85 = 0  # keep the PDF ~25% smaller than ASCII85 would
    pdf_out = args.outdir / f"{args.name}.pdf"
    c = canvas.Canvas(str(pdf_out), pagesize=page, pageCompression=1)
    c.setTitle("YOKO ONO | Menu QR | 80 x 100 cm (upscaled)")
    c.setAuthor("YOKO ONO Asian Kitchen")
    c.drawImage(str(jpg_out), 0, 0, width=page[0], height=page[1])  # JPEG embedded as-is
    draw_qr_vector(c, qr, src.size, page)
    c.showPage()
    c.save()
    print(f"wrote {pdf_out} and {jpg_out}")


if __name__ == "__main__":
    main()
