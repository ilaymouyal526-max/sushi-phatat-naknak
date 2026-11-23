# QA review: pushpop-manga-sticker (print v1, 23.11.2026)

Read-only review. No paid tools were called and no project file was changed. Scratch crops and demos are in
`/tmp/claude-0/-home-user-sushi-phatat-naknak/520b4b8e-9f4a-55d6-8442-55581db6267d/scratchpad/qa/`.
Not reported again (decisions already made): the A3 redo without the product, and the 3 new side-A panels (thrown, fallen on his side, reads the scroll).

## TL;DR
- **Print files are not ready yet.** They are a 300 DPI RGB raster with no TrimBox or BleedBox, no output intent, and a stray Helvetica font resource. All of this can be fixed in code for free (see F1 and F2).
- **Two how-to panels show the wrong product state.** In B2 the vial is still on the tube. In B4 the vial is back on the tube and full, and there is also a double logo. These two are the only regenerations worth paying for: **1.50 credits** (B2 and B4 edits, 0.75 each).
- **Extra red appears in 6 panels (mostly torii gates).** It can be removed for free with a hue mask in code. I tested a prototype on B1 and it works.
- Resolution is not a problem. The 1k "low" panels are 760–1050 DPI at their printed size, so no upscale is needed.

## 1. Brief compliance, panel by panel

Each panel was viewed at full size, and the product was checked in zoomed crops. The tube ratio is the body height divided by its width, excluding the vial, and is approximate.

| Panel | Verdict | Findings |
|---|---|---|
| A1 forest | OK | Character from behind; no red or gold; snow, footprints and breath are present. |
| A2 entrance (v2) | OK | The sign reads YOKO ONO correctly, about 12 mm wide in print (user-approved). The torii frame is the only red. The bulb row glows warm yellow, which is a small extra gold. Minor: his sole has sneaker-like tread instead of a straw sandal, and the sword is missing (he wears it in A1, A3 and A4). Both are invisible at about 8 mm figure height. |
| A3 cut | (redo pending) | For the redo prompt: there is a red torii in the background, and the energy red is very saturated (RGB 222,23,34), which is outside the CMYK gamut and will print duller. Add "no torii, no red objects" to the redo prompt. |
| A4 landing | Fix red (free) | Red torii in the background (known), and **also a small red cushion or offering on the altar under the torii** (new). Pose: crouched with one hand on the floor, not cleanly "on one knee", but it reads well. Right hand on the hilt and sword sheathed: OK. |
| A5 reveal (v2) | OK | Product is correct: ratio about 1:4.5, full-length vial on the RIGHT, clear lid with tab and ring, base lobe. The cushion is the only red. The AI label is garbled ("YOYOOOOR"), but it is about 3 mm in print and reads as a gold mark. |
| B1 step 1 (v2) | Fix red (free) | Correct step: the vial slides up out of the ring, and the lid is closed. Ratio about 1:4.6. **Red torii in the background.** The label lettering is garbled at about 3 mm (acceptable). |
| B2 step 2 (v2) | **Wrong state (paid)** | **The vial is still attached on the right**, but by step 2 it should already be out, lying on the table. Lid with tab and ring is in his hand: OK. Ratio about 1:4.1. **Red torii, and an extra red cushion with tassels** that the prompt never asked for. The label is mirrored or garbled ("YKO OVO"). |
| B3 step 3 (v2) | Fix red (free); optional paid | The pour reads correctly and the teriyaki is a glossy amber stream (teriyaki, not soy). **Red torii, a red swirl, and a red cushion.** Product: **the tube is stubby (about 1:3.1)**, the vial is drawn as a **bottle with a neck**, and the roll already sits above the rim before the push-up. |
| B4 step 4 (v2) | **Wrong state and double logo (paid)** | **The vial is back on the tube and full** after it was poured in B3. **There is a second small arched logo above the round label.** The push-up from below is only weakly shown (thumb under the base, roll only about 1 cm up). **Red torii, a red cloth table at the left, and a red arrow.** Ratio about 1:3.7. Garbled label ("YOOO ONO"). |

- **Every extra red** (red is allowed only for the gate frame, the energy and the A5 cushion):
  - Torii gates in A3, A4, B1, B2, B3 and B4.
  - Altar cushion in A4.
  - Cushions in B2 and B3.
  - The swirl in B3.
  - The table and arrow in B4.
  - Root cause: the shared COLOUR block names a "Yoko gate frame" in red, and the SHRINE block mentions a shrine, so the model adds a torii. For every new or redone panel, add "no torii gates and no red objects anywhere in the shrine" to the SHRINE block.
- **Character consistency is good.** The topknot with loose strands, the white headband with long tails, stubble and goatee, the indigo-black kimono and the white tasuki rope with its knot match across A3, A4 and B1–B4. A1 and A2 (seen from behind) are consistent too.
- **Stray text.** There is no AI text outside the approved sign and labels. The AI labels are garbled in A5 and B1–B4, but they are 2.7–3 mm in print, so this is acceptable. The real logo on side B is the original file.
- **Fonts.** Only Dela Gothic One is used (sound effects and step numbers), plus the logo image. `fonts/YujiBoku-Regular.ttf` sits in the folder unused. Keep it out of the layout, or the design hits the 2-font limit with no room left.
- **Teriyaki colour.** The B3 stream is correct. Inside the vials it looks near-black, much like soy, but this is acceptable.

## 2. Print readiness

- **Effective resolution of each panel at its printed size.** All panels are well above 300 DPI, so **1k "low" is enough for resolution** (its weak spots are hands and label lettering, not pixels):

  | Panel | Pixels | Printed size | Effective DPI | Crop |
  |---|---|---|---|---|
  | A1, A2 | 1344×576 | 45×19.3 mm | **759** | none |
  | A3, A4 | 896×1120 | 21.7×27.1 mm | **1049** | none |
  | A5 | 1344×752 | 45×24.5 mm | **759** | 2.7% of the height |
  | B1–B4 | 880×1168 | 21.7×31.4 mm | **944** | 8.4% of the width |

  - The 8-panel side A will shrink the panels and raise their DPI further.
  - **But the export throws the resolution away.** `export_print.py` rasterises everything at **300 DPI** (638×1228 px), including the vector sound effects, the step numbers and the gold logo. The logo's thinnest lines are about 0.08–0.15 mm (2–4 px at 678 DPI native), so at 300 DPI they become 1–2 px and come out soft.
- **PDF check with pypdf and pdfinfo:**
  - Page size: 54×104 mm (correct).
  - Artwork: one DeviceRGB image at 300 ppi.
  - Cut line: `/Separation /CutContour /DeviceCMYK`, 0.25 pt stroke, overprint on (/OP true), rounded rectangle at the trim with a 2 mm radius. The cut SVG matches. This is good.
  - **No TrimBox or BleedBox:** all boxes equal the MediaBox.
  - **No OutputIntent and not PDF/X.** The file is PDF 1.4.
  - **An unused, non-embedded Helvetica `/F1` resource** (added by reportlab). PDF/X preflight flags it.
  - **The outermost left and right pixel columns are grey (52,51,50).** The cause is rounding: 638/54 is not equal to 1228/104. This sits in the outer bleed, so it is harmless but sloppy.
- **Black levels:**
  - The background is RGB #0a0a0a. The panel frames are #14110f, and AI blacks go down to about RGB 0–6 (the A5 shadow strip is about 5,5,5).
  - None of it is pure K. After a RIP conversion each of these becomes a slightly different 4-colour black (roughly 280–320% total ink).
  - Side B is about 49% near-black and side A about 29%, so a patchy black or a TAC overrun is the main colour risk.
- **RGB vs CMYK:**
  - The deliverables are RGB.
  - A print shop will want one of two things: a PDF/X-4 (RGB with an output intent is fine for many digital sticker printers), or a PDF/X-1a in CMYK with their profile, usually FOGRA39 / ISO Coated v2 or FOGRA51, or their own vinyl profile. They also need a named rich-black recipe and their exact cut-spot name.
  - **I could not test a local conversion here.** Ghostscript is not installed and there is no CMYK ICC profile on the system. Pillow's ImageCms works, but only with sRGB. My attempt to install Ghostscript was blocked by the session's permission system.
  - The conversion would be free once a profile file exists. Use `ImageCms.profileToProfile(im, sRGB, "FOGRA39.icc", renderingIntent=1, outputMode="CMYK")` with black-point compensation, then force the background and gutters to one rich black. Alternatively, use `gs -sDEVICE=pdfwrite -sColorConversionStrategy=CMYK -sOutputICCProfile=...`.
- **Thin lines that may disappear:**
  - The gold logo lines (0.08–0.15 mm) and "ASIAN KITCHEN" (about 0.75 mm cap height) are **knocked out of a rich black**. A 0.1 mm registration shift will fringe them.
  - The cream outline on the sound effects is about 0.27 mm visible, which is OK.
  - The cut line is 0.09 mm, which is fine for a cutter.
  - Fine hatching in the panels is already lost at 300 DPI.
- **Sound-effect legibility at real size:**
  - ザッ, ドン!! and ズザッ are 5.4–6.2 mm Dela Gothic, ink with a cream outline. They are clearly legible.
  - **ゴゴゴ sits on A5's black strip, ink-on-black**, so only the thin cream outline shows: it reads as hollow, outlined letters and the dakuten are muddy.
  - The step numbers (3.4 mm digits in 5.4 mm seals) are legible.
- **Logo size.** It is 26 mm wide (the minimum is 25), with 3.9 mm (15%) of clear space. OK.
- **Safe zone and cut tolerance:**
  - All type is inside the 3 mm safe zone. ズザッ is the closest at about 3.5 mm from the trim; the seals' right edge is at about 3.6 mm.
  - **The panel art starts 2.5 mm from the trim, which is inside the 3 mm safe line.** With a typical die-cut tolerance of ±0.5–1 mm, the black border will look uneven, anywhere from 1.5 to 3.5 mm.
- **Gutters and bleed.** The gutters and the bleed are black, so no white sliver can appear at the cut. The cream "torn" panel edges come from the rough-frame filter and are intended. The cut-line corner radius is 2 mm. OK.
- **File-name hazard.** `A2_final.png`, `A5_final.png` and `B1–B4_final.png` are the **v1 images without a logo**. The layout uses `<ID>.png`, which is the v2 image (identical to `*_v2_final.png`). Any script that picks `*_final.png` would silently print the old art.

## 3. Prioritized fix list (most important first)

| # | Fix | Free or paid | How |
|---|---|---|---|
| 1 | **B2: wrong step state** (vial still attached) | **Paid, 0.75, recommended** | Edit B2 v2 (6217a8c0): "Remove the teriyaki vial from the right side of the tube; it lies on the table beside the tube; the base lobe is empty; keep everything else identical." |
| 2 | **B4: vial reattached, double logo, weak push-up** | **Paid, 0.75, recommended** | Edit B4 v2 (ffb7efe5): "Remove the vial from the tube (base lobe empty), remove the small arched emblem above the round label, push the roll visibly ~3 cm higher out of the top, and remove the red arrow and the red table; keep everything else identical." |
| 3 | Export at 600 DPI or as vector | Free | Run `export_print.py --scale 2`, which is already supported. Better: render the vector PDF with Playwright `page.pdf()`, so text and logo stay sharp and the panels keep their native DPI. Also make the pixel size match the 54:104 ratio exactly, which removes the grey edge column. |
| 4 | PDF boxes and clean-up | Free | With pypdf: TrimBox = MediaBox inset by 2 mm (5.669 pt), BleedBox = MediaBox. Remove the unused `/Font /F1`. Add an OutputIntent once the printer's profile is known. |
| 5 | Remove the extra red (torii in A4 and B1–B4, A4 altar cushion, B3 swirl, B4 table) | Free | Add a cleaning step (for example `scripts/clean_panels.py`) that writes `*_clean.png` and never overwrites. Inside a bounding box per item, take pixels with hue < 18 or > 235 and saturation > 70, and replace them with luminance × 0.62 with a warm-ink tint. Tested on the B1 torii: it reads as an ink torii (`.../scratchpad/qa/demo_B1_torii_grey.png`). If fix 2 is not bought, darken the **B4 arrow** to ink (it then disappears on the kimono) and draw a vector arrow in paper colour in the layout. The **B2 and B3 cushions** are for the user to decide: keeping them echoes A5; otherwise neutralise them the same way. |
| 6 | ゴゴゴ legibility | Free | Add an `invert` flag to the sound-effect list: paper fill with an ink stroke when the effect sits on a dark area. |
| 7 | Black plan for print | Free (needs the printer's answer) | Ask the printer for their profile, TAC limit, rich-black recipe and cut-spot name. In the CMYK step, map everything below about RGB 12 to one rich black (for example C60 M40 Y40 K100), and keep the area under the gold logo simple (K-only or a light rich black) to protect the 0.1 mm lines. Ask whether the gold should be a spot or foil colour. |
| 8 | Panel margin vs cut tolerance | Free | In `build_layout.py`, set `MARGIN = 3.0`. The 8-panel re-layout is a good moment to do it. |
| 9 | File naming | Free | Rename the v1 `*_final.png` files to `*_v1.png`, or document `<ID>.png` as the single source of truth. |
| 10 | B3: stubby tube (1:3.1), necked bottle, roll above the rim | Paid, 0.75, **optional, not recommended** | Edit B3 v2 (77b6ddc5): "Make the tube taller and slimmer (1:4.2), the pouring vial a slim straight test-tube vial with a black ribbed cap, the roll flush with the rim; remove the red swirl." It is the least visible of the three at 21.7 mm. |
| 11 | Garbled AI labels (A5, B1–B4) and the A2 sneaker sole | Skip | At 2.7–3 mm they read as a gold mark and are invisible in print. |
| 12 | A3 redo and the 3 new panels | (already planned) | Add to their prompts: "no torii gates, no red objects except the energy wave; vermilion, not pure red (avoid RGB 220,20,30)". |

**Recommended paid budget: 1.50 credits** (fixes 1 and 2, 2 × 0.75 on GPT Image 2.6 low 1k). The ceiling with the optional B3 edit is 2.25 credits. Per CLAUDE.md, run `estimate_image_cost` first and get the user's "yes" for each specific job.
