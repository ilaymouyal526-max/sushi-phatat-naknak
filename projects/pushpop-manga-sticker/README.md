# Sushi Push Pop: manga sticker (שני צדדים, 50×100 מ"מ)

Brief, decisions and open questions: `brief.md`. Every file used or made: `assets.md`.

## Pipeline (section 8 of the brief)
1. `python3 scripts/build_prompts.py`: writes `prompts/prompts.json`, with 9 panels built from fixed blocks.
2. `python3 scripts/check_prompts.py`: checks the prompts against the brief and writes `prompts/QA.md`.
3. Generate (paid, needs approval): `generate_image_batch` with `requests` from `prompts/prompts.json`. Save the results as `assets/panels/<ID>.png`.
4. `python3 scripts/build_layout.py && python3 scripts/build_layout.py --guides`: writes `layout/sticker.html` (RTL panel grid, ink frames, sound effects in Dela Gothic One, and the real logo).
5. `python3 scripts/export_print.py [--wrap]`. The side A grid and the sound effects are in `layout/side_a.json`, and `build_layout.py --placeholders ID…` makes placeholder panels.
   The export: writes the print files to `out/`.
   - `side_A/B_print.png` at 300 DPI, 54×104 mm.
   - `side_A/B_print.pdf` with a `CutContour` spot line.
   - `side_A/B_cut.svg`, `sticker_both_sides.pdf` and `preview.jpg`.

The export uses Playwright for Node (`scripts/render.js`), reportlab and pypdf.
