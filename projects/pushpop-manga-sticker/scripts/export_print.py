#!/usr/bin/env python3
"""Render layout/sticker.html to print files (free, local).

For each side (A, B):
  out/side_<X>_print.png   54x104 mm at 300 DPI (trim 50x100 + 2 mm bleed), DPI tag set
  out/side_<X>_print.pdf   artwork + "CutContour" spot-colour line at the trim, 2 mm corners
  out/side_<X>_cut.svg     the same cut line as a vector
plus out/sticker_both_sides.pdf (2 pages) and out/preview.jpg (both sides with guides).

  python3 scripts/build_layout.py && python3 scripts/build_layout.py --guides
  python3 scripts/export_print.py [--scale 2]     # --scale 2 renders 600 DPI masters
"""
import argparse, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_layout as L  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, "out")


def render(html, scale):
    """Screenshot both sides with Playwright (Node) and return {side: png bytes}."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "render.js"),
                        html, td, str(scale), "shot"], check=True)
        return {s: open(os.path.join(td, f"shot_{s}.png"), "rb").read() for s in "AB"}


def cut_pdf(png_path, pdf_path, dpi):
    from reportlab.lib.colors import CMYKColorSep
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(pdf_path, pagesize=(L.PAGE_W * mm, L.PAGE_H * mm))
    c.setTitle("Sushi Push Pop manga sticker")
    c.drawImage(png_path, 0, 0, L.PAGE_W * mm, L.PAGE_H * mm)
    cut = CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1)
    c.setStrokeColor(cut)
    c.setLineWidth(0.25)
    c.setStrokeOverprint(True) if hasattr(c, "setStrokeOverprint") else None
    c.roundRect(L.BLEED * mm, L.BLEED * mm, L.TRIM_W * mm, L.TRIM_H * mm, L.CUT_RADIUS * mm, stroke=1, fill=0)
    c.showPage()
    c.save()


def cut_svg(path):
    d = L.rect_d(L.BLEED, L.BLEED, L.TRIM_W, L.TRIM_H, L.CUT_RADIUS)
    open(path, "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{L.PAGE_W}mm" height="{L.PAGE_H}mm" '
        f'viewBox="0 0 {L.PAGE_W} {L.PAGE_H}"><g id="CutContour"><path d="{d}" fill="none" '
        f'stroke="#FF00FF" stroke-width="0.25"/></g></svg>\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    dpi = 300 * a.scale
    shots = render(os.path.join(ROOT, "layout", "sticker.html"), a.scale)
    pngs = []
    for side, data in shots.items():
        tmp = os.path.join(OUT, f"_side_{side}.png")
        open(tmp, "wb").write(data)
        im = Image.open(tmp).convert("RGB")
        want = (round(L.PX_W * a.scale), round(L.PX_H * a.scale))
        if im.size != want:
            im = im.resize(want, Image.LANCZOS)
        png = os.path.join(OUT, f"side_{side}_print.png")
        im.save(png, dpi=(dpi, dpi))
        os.remove(tmp)
        cut_pdf(png, os.path.join(OUT, f"side_{side}_print.pdf"), dpi)
        cut_svg(os.path.join(OUT, f"side_{side}_cut.svg"))
        pngs.append(png)
        print(side, im.size, f"{dpi:.0f} DPI", f"{im.size[0] / dpi * 25.4:.2f}x{im.size[1] / dpi * 25.4:.2f} mm")

    # 2-page PDF
    from pypdf import PdfWriter
    w = PdfWriter()
    for side in "AB":
        w.append(os.path.join(OUT, f"side_{side}_print.pdf"))
    w.write(os.path.join(OUT, "sticker_both_sides.pdf"))

    # preview with guides (trim = magenta, safe = blue)
    g = render(os.path.join(ROOT, "layout", "sticker_guides.html"), 2.0)
    ims = []
    for side in "AB":
        tmp = os.path.join(OUT, "_g.png")
        open(tmp, "wb").write(g[side])
        ims.append(Image.open(tmp).convert("RGB"))
        os.remove(tmp)
    pad = 40
    W = sum(i.width for i in ims) + pad * 3
    H = max(i.height for i in ims) + pad * 2
    sheet = Image.new("RGB", (W, H), (40, 37, 33))
    x = pad
    for im in reversed(ims):  # side A on the right, like the reading order
        sheet.paste(im, (x, pad))
        x += im.width + pad
    sheet.save(os.path.join(OUT, "preview.jpg"), quality=90)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
