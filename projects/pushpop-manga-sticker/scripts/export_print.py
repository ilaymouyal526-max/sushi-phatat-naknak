#!/usr/bin/env python3
"""Render the layouts to print files (free, local).

For each side (A, B):
  out/side_<X>_print.png   54x104 mm at 300 DPI (trim 50x100 + 2 mm bleed), DPI tag set
  out/side_<X>_print.pdf   artwork + "CutContour" spot-colour line at the trim, 2 mm corners
  out/side_<X>_cut.svg     the same cut line as a vector
plus out/sticker_both_sides.pdf (2 pages) and out/preview.jpg (both sides with guides).

With --wrap, also one wrap-around label, side B on the LEFT and side A on the RIGHT:
  out/wrap_print.png / .pdf / _cut.svg   104x104 mm (trim 100x100 + 2 mm bleed)
  out/wrap_preview.jpg                   with guides (trim magenta, safe blue, A/B seam yellow)

Every run checks that each sound effect sits inside the 3 mm safe zone and inside its own panel.

  python3 scripts/build_layout.py && python3 scripts/build_layout.py --guides
  python3 scripts/export_print.py [--wrap] [--scale 2]     # --scale 2 renders 600 DPI masters
"""
import argparse, json, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_layout as L  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, "out")


def render(html, scale):
    """Screenshot every side of a layout page with Playwright (Node): ({side: png bytes}, qa dict)."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "render.js"),
                        html, td, str(scale), "shot"], check=True)
        qa = json.load(open(os.path.join(td, "shot_qa.json")))
        return {s: open(os.path.join(td, f"shot_{s}.png"), "rb").read() for s in qa}, qa


def cut_pdf(png_path, pdf_path, trim_w=L.TRIM_W):
    from reportlab.lib.colors import CMYKColorSep
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    page_w = trim_w + 2 * L.BLEED
    c = canvas.Canvas(pdf_path, pagesize=(page_w * mm, L.PAGE_H * mm))
    c.setTitle("Sushi Push Pop manga sticker")
    c.drawImage(png_path, 0, 0, page_w * mm, L.PAGE_H * mm)
    cut = CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1)
    c.setStrokeColor(cut)
    c.setLineWidth(0.25)
    c.setStrokeOverprint(True) if hasattr(c, "setStrokeOverprint") else None
    c.roundRect(L.BLEED * mm, L.BLEED * mm, trim_w * mm, L.TRIM_H * mm, L.CUT_RADIUS * mm, stroke=1, fill=0)
    c.showPage()
    c.save()


def cut_svg(path, trim_w=L.TRIM_W):
    page_w = trim_w + 2 * L.BLEED
    d = L.rect_d(L.BLEED, L.BLEED, trim_w, L.TRIM_H, L.CUT_RADIUS)
    open(path, "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{L.PAGE_H}mm" '
        f'viewBox="0 0 {page_w} {L.PAGE_H}"><g id="CutContour"><path d="{d}" fill="none" '
        f'stroke="#FF00FF" stroke-width="0.25"/></g></svg>\n')


def save_png(data, path, want, dpi):
    tmp = path + ".tmp.png"
    open(tmp, "wb").write(data)
    im = Image.open(tmp).convert("RGB")
    os.remove(tmp)
    if im.size != want:
        im = im.resize(want, Image.LANCZOS)
    im.save(path, dpi=(dpi, dpi))
    return im


def inside(poly, x, y, pad=0.0):
    """Point inside a convex polygon (clockwise in SVG coordinates), at least `pad` mm from each edge."""
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        ln = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        if ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) / ln < pad:
            return False
    return True


def check_sfx(qa, x_off=0.0):
    """Each sound effect (text cell box, measured in the browser) must sit inside the 3 mm safe zone
    and inside its own panel's shape (slanted panels included), clear of the ink frame."""
    ok = True
    safe = (L.BLEED + L.SAFE, L.BLEED + L.SAFE, L.BLEED + L.TRIM_W - L.SAFE, L.BLEED + L.TRIM_H - L.SAFE)
    shapes = {p.id: list(p.pts) for p in L.side_a()}
    for s in qa["sfx"]:
        x0, y0, x1, y1 = s["bbox"]
        x0, x1 = x0 - x_off, x1 - x_off              # wrap: side A sits 50 mm to the right
        msgs = []
        if x0 < safe[0] or y0 < safe[1] or x1 > safe[2] or y1 > safe[3]:
            msgs.append("OUTSIDE SAFE ZONE")
        if not all(inside(shapes[s["panel"]], x, y, 0.4) for x in (x0, x1) for y in (y0, y1)):
            msgs.append(f"crosses the frame of panel {s['panel']}")
        margin = min(x0 - safe[0], y0 - safe[1], safe[2] - x1, safe[3] - y1)
        print(f"  sfx {s['text']:<4} on {s['panel']:<3} {x1 - x0:4.1f}x{y1 - y0:4.1f} mm at "
              f"{x0 - L.BLEED:4.1f},{y0 - L.BLEED:4.1f} (trim)  safe margin {margin:4.1f} mm  {'; '.join(msgs) or 'ok'}")
        ok &= not msgs
    return ok


def preview_sheet(images, path, pad=40):
    W = sum(i.width for i in images) + pad * (len(images) + 1)
    H = max(i.height for i in images) + pad * 2
    sheet = Image.new("RGB", (W, H), (40, 37, 33))
    x = pad
    for im in images:
        sheet.paste(im, (x, pad))
        x += im.width + pad
    sheet.save(path, quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--wrap", action="store_true", help="also export the 100x100 mm wrap-around label")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    dpi = 300 * a.scale
    L.build(False)
    L.build(True)
    for pnl in L.side_a():
        vx0, vy0, vx1, vy1 = pnl.visible_fraction()
        print(f"  {pnl.id:<3} {pnl.w:4.1f}x{pnl.h:4.1f} mm  aspect {pnl.w / pnl.h:4.2f}  shows image "
              f"x {vx0:4.0%}–{vx1:4.0%}, y {vy0:4.0%}–{vy1:4.0%}  focal {pnl.focal}")

    shots, qa = render(os.path.join(ROOT, "layout", "sticker.html"), a.scale)
    ok = check_sfx(qa["A"])
    for side in "AB":
        png = os.path.join(OUT, f"side_{side}_print.png")
        im = save_png(shots[side], png, (round(L.PX_W * a.scale), round(L.PX_H * a.scale)), dpi)
        cut_pdf(png, os.path.join(OUT, f"side_{side}_print.pdf"))
        cut_svg(os.path.join(OUT, f"side_{side}_cut.svg"))
        print(side, im.size, f"{dpi:.0f} DPI", f"{im.size[0] / dpi * 25.4:.2f}x{im.size[1] / dpi * 25.4:.2f} mm")

    from pypdf import PdfWriter
    w = PdfWriter()
    for side in "AB":
        w.append(os.path.join(OUT, f"side_{side}_print.pdf"))
    w.write(os.path.join(OUT, "sticker_both_sides.pdf"))

    # preview with guides (trim = magenta, safe = blue); side A on the right, like the reading order
    g, _ = render(os.path.join(ROOT, "layout", "sticker_guides.html"), 2.0)
    preview_sheet([Image.open(__import__("io").BytesIO(g[s])).convert("RGB") for s in "BA"],
                  os.path.join(OUT, "preview.jpg"))

    if a.wrap:
        shots, qa = render(os.path.join(ROOT, "layout", "wrap.html"), a.scale)
        ok &= check_sfx(qa["W"], x_off=L.TRIM_W)
        png = os.path.join(OUT, "wrap_print.png")
        im = save_png(shots["W"], png, (round(L.WRAP_PX_W * a.scale), round(L.PX_H * a.scale)), dpi)
        cut_pdf(png, os.path.join(OUT, "wrap_print.pdf"), L.WRAP_TRIM_W)
        cut_svg(os.path.join(OUT, "wrap_cut.svg"), L.WRAP_TRIM_W)
        print("wrap", im.size, f"{dpi:.0f} DPI", f"{im.size[0] / dpi * 25.4:.2f}x{im.size[1] / dpi * 25.4:.2f} mm")
        g, _ = render(os.path.join(ROOT, "layout", "wrap_guides.html"), 2.0)
        preview_sheet([Image.open(__import__("io").BytesIO(g["W"])).convert("RGB")],
                      os.path.join(OUT, "wrap_preview.jpg"))
    print("wrote", OUT)
    if not ok:
        print("WARNING: sound effect placement problems above")


if __name__ == "__main__":
    main()
