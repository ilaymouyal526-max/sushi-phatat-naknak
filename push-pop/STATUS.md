# Sushi Push Pop: product reference status

Prompt: `push-pop/higgsfield-product-prompt.md`

## 2026-11-09: drafts (a) and (b)
- **Model and settings:** GPT Image 2.5, low, 1K, 4:5. Cost 0.25 + 0.25 = **0.5 credits** (approved).
- **References:**
  - Background: the gyoza screen photo, job `726d4428-bede-48ee-8654-75d0f479fedc`.
  - Product: earlier Push Pop renders `1ca4c7a3-4779-42ab-bf62-fb882941c736` and `afa766fc-d52c-405c-9120-3cdd62d93ead`. The 7 real photos and the video were not available in this session.
- **Jobs:**
  - (a) front: `74e42e85-e25f-47b1-9c6e-9c3b5af6543f` → `drafts/a_front_draft.png`
  - (b) 3/4: `1aa70135-3579-436c-9e44-c0bec358386b` → `drafts/b_34_draft.png`
- **What worked:**
  - Background matches the screen style: black room, overhead spot, black marble with gold veins.
  - Label is blank (slate blue, gold rim), ready for the logo composite.
  - Vial is full height with black caps, and the base has a lobe.
  - Rim light keeps the tube separate from the background.
- **What did not work:**
  - The tube is stubby (height about 2× width, not 3.4×). It followed the old renders rather than the text.
  - (b) came out almost at eye level, not 35° from above, so the lid is barely seen from the top.
- **Not run:** (c) underside. It needs a real photo of the base.

## Next
1. Get the 7 real photos and the video into the session, and check the spec against them.
2. Re-run the drafts with the real photos as product references. Price check and approval first.
3. Finals at high, 2K (2.75 credits each), each approved separately.
4. Composite the real logo and "Sushi push pop" lettering locally.

## 2026-11-09: real logo on the drafts (local, 0 credits)
- **Logo source:** `shared/logo-path.js` (traced from the restaurant logo), rendered in gold with "ASIAN KITCHEN" in Montserrat.
- **Method:** cylindrical wrap with the shading taken from the blank label, so the paper grain shows through the foil.
- **Outputs:** `drafts/a_front_logo.png` and `drafts/b_34_logo.png`
- **Tools:**
  - `tools/render_logo.js <dir with logo-path.js + montserrat-latin.woff2>`
  - `tools/composite_logo.py <draft> <logo_white.png> <out> '<json>'`
- **Settings used:**
  - (a): `{"tube_cx":418,"R":129,"lcx":419,"lcy":506,"fit_r":98}`
  - (b): `{"tube_cx":428,"R":132,"lcx":401,"lcy":512,"fit_r":104}`
- **Not added yet:** the "Sushi push pop" lettering at the bottom. It needs a crop from a real photo.
