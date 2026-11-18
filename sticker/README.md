# Sushi Push Pop sticker – v5 "Ink Ronin"

v4 (chibi anime kid) was rejected by the owner as too kitschy. v5 is a seinen-manga sumi-ink look: a ronin-chef drawn in black ink, set on an all black-and-gold layout (brand palette): gold logo, gold title and captions, gold brush frames and gold seal step numbers, with the same gold logo on the tube in every panel.

## Files (`v5/`)
- `sticker_v5_preview.jpg`: preview of the 4-step how-to sticker.
- `sticker_v5_print.png` / `.pdf`: print files.
  - Trim is 90×120 mm, with 2 mm bleed and 300 DPI.
  - The PDF carries a `CutContour` spot-colour line with 3 mm corners.
- `sticker_v5_cut.svg`: the cut line as a vector.
- `wrap_v5_preview.jpg`: preview of the tube wrap label.
- `wrap_v5_guides.jpg`: the same wrap with zone guides (seam | front | soy-clip side | back | seam, same zones as wrap_v1).
- `panels/`: the generated art (4 steps, hero, character options) and the extracted gold logo. `*_branded.jpg` = the same images with the gold Yoko Ono logo and "SUSHI PUSH POP" composited onto the tube label by `brand_tube.py`; `compose_v5.py` uses them when present.

The masters (`*_master.png`, `wrap_v5_flat.png`) are git-ignored. Regenerate them with:

```
python3 sticker/compose_v5.py --assets sticker/v5/panels --fonts <dir with ShipporiB1-500.ttf, ShipporiB1-800.ttf> --out sticker/v5 [--sticker-mm 90x120] [--wrap-mm WxH]
```

Fonts: Shippori Mincho B1 (Google Fonts, OFL).

## Generation (Higgsfield, GPT Image 2.5)
- **Character options** (3× medium 1K, 1.5 credits). A was picked: job `2abdddcd-b151-4797-836d-019ebd38bdb9`.
- **Step panels** (4× high 2K, 11 credits):
  - 1: `59027fc7-61ae-4ef9-8ead-4410203daa20`
  - 2: `a3556baa-052d-480e-87fc-fc4718ebfc50`
  - 3: `d35738d3-d181-4ce1-8eee-b2934210328b`
  - 4: `3d8df4a0-9376-4657-a216-fc612ba44e7e`
- **References:**
  - Sumi-e test from Oct 6, used for style only.
  - Black-tube product shots from Nov 9 (3/4 and front views), used for exact product shape.
  - Push-up shot from Nov 4, used for the sushi.

**Style block**, copied verbatim into every prompt:

> Japanese seinen samurai-manga ink illustration. Expressive sumi brush linework with dry-brush edges and strongly varying line weight, realistic adult anatomy, fine-pen cross-hatching in the shadows, sparse grey ink wash, generous bare cream washi paper, a few ink splatters, calm intense mood. Black ink only, except the product's thin gold label rim and the natural colours of the sushi. No screentone, no chibi, no sparkles, no cute elements. No text, no letters, no seals with characters, no logo.

**Character block:** a Japanese ronin-chef in his 30s, long black hair in a rough topknot, light stubble, dark kimono with tasuki, white cloth headband, serious calm face.
