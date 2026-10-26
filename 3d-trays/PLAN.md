# Plan: ultra-realistic Yoko trays, smoother handling, ingredient inspection

## Context
The 3D tray artifact (https://claude.ai/artifact/T4kXJSfCbqVD8ErwXrpFsL, version 4) now uses:
- photo cut faces and photo surface tiles
- the party layout traced from the photo
- the restyled real Yoko promo trays

You asked for three more things on top of the earlier plan (kept in full in Part A):
1. **Ultra-realistic textures.** The textures are shown at 512 px now. The fillings you see when a roll comes apart are still hand-drawn, and there are no depth or shine maps.
2. **Smoother handling.**
   - Every move locks the controls until it finishes (`busy`).
   - Camera moves fight the orbit controls.
   - The first tap stutters while shaders compile.
   - Auto-rotate never comes back.
3. **Inspecting single ingredients, like the earlier 3D models.** The Red Dragon model (https://claude.ai/artifact/ReC8CVFLamGZGh4BjdJr7o) and the nigiri model (https://claude.ai/artifact/CWPJZy5yBHovbj66F9mQQ9) took a piece apart with a gold pointer line and a name label for every layer. The tray page still has that label styling (`.lbl`, `#lines`) but lost the code, and it spreads the parts out generically.

**Your decisions:**
- **Uses:** stills, the live site and video.
- **Views:** every view as close to the photos as possible.
- **Textures:** 2k for the fillings, plus free upgrades for the rest.
- **Garnish:** detailed 3D meshes for all four (kimchi, ginger rose, wasabi, frisée).
- **Promo tray:** match the real trays.

**Spending rule (CLAUDE.md):** each paid batch below is listed with its tool, model, settings, purpose and checked price. Approving this plan approves exactly those batches. Right before running one, I re-check the price (free). If anything differs, or a retry, variant or extra item is needed, I stop and ask again.

---

## Part A: the earlier plan (kept)

### Inputs (done)
- **Real photos:** Drive folder "יוקומגשים" (id `1cSZOyKrjwz6Hr_DsOEEAORMPpnTDLzZq`), 26 photos.
  - Decoded copies are in `scratchpad/photos/raw/`.
  - Copies at ≤2048 px are in `scratchpad/photos/jpg/`.
  - Higgsfield reference ids:
    - WA0031 `55615fa7-…` (pink, sesame, white flake, tuna maki, avocado)
    - WA0037 `2c8bcd55-…` (tataki, wasabi)
    - WA0038 `51f45471-…` (avocado rolls)
    - WA0045 `45ec1c20-…` (bowl, cut faces)
    - WA0032 `ea09642b-…` (ginger, pink, sesame)
  - Other garnish source photos:
    - kimchi: phone photo 20261002_105621, HEIC on Drive (id `1m2e1wvS0M5jCp_Sh89H7p55L2SWSf2Qw`)
    - lettuce: 20261002_125157 (id `1xZheyOPOx--xDoMrBYECOCmXVYL9SlYY`)
    - ginger: WA0032 (Drive id `1HqRzsrozr3zxA1p_KpgbfcAk2k3N0r8H`)
    - wasabi: WA0037
- **Reference photos:** `scratchpad/refs/trayCut.jpg` (top-down, 1000²) and `scratchpad/refs/trayB.jpg` (counter shot).

### Step 1: layout and proportions (done)
- The party tray copies `trayCut` piece by piece: 36 pieces in `PARTY_SLOTS`, some standing and some lying on their side, with garnish in `PARTY_GARNISH`.
- Roll size is about 1/9 of the tray.
- The key light comes from the upper left, as in the photo.
- The top camera position is `(0,h,0.001)`, which matches the photo's orientation.
- The square promo tray matches the real Yoko tray:
  - black print with gold chevrons and red blossom medallions
  - seven veg maki standing in the center
  - ginger and wasabi in the corners
  - lettuce in wedges 0, 2 and 4
  - white panko
  - XL uses the same layout as L.

### Step 2: Batch A, cut faces (done)
- 10 images, `gpt_image_2_5`, high, 1k: 15 credits.
- Tuna-mayo maki (`nmk`) and veg maki (`mcc`) faces come from the real photos.
- The face images are cut to round discs with transparent backgrounds (`finalize.py`) and drawn on both ends of each piece.

### Step 3: Batch B, surface tiles (done)
- 7 tiles at 1k: 10.5 credits. Rice, sesame, pink panko, white panko flakes, tempura, avocado and nori.
- Each tile is made seamless locally (offset and blend, feather 96).

### Generated media to keep
- **Higgsfield job ids (gpt_image_2_5, high, 1k):**
  - Cut faces: pnk `8563e08f`, ses `bc39b6c2`, ins `177d560b`, drg `3b761491`, tmp `c2ba7f9a`, tmy `339440a0`, sap `ce2a9ec2`, sat `1dd6a704`, vgp `1b5844e5`, tmc `32eac549`.
  - Tiles: rice `ab5eeffa`, ses `0d9391dc`, pink `5565a661`, flake `3ed0c339`, avo `a75640d1`, nori `a0f93dac`, tempura `e2b0b2e4`.
  - Results live at `https://d8j0ntlcm91z4.cloudfront.net/user_3JoptmBPugci1QhYLrCOcuUL5MN/` (full ids are in the transcript).
- **Raw-salmon samples (7 credits, today):**
  - 2k `f94d1957-9fb9-40e7-b51d-f0ce206df856`, 2048 px, V-shaped fat pattern.
  - 4k `f6ea4aeb-86d5-4367-9ae7-98047e6f2cd2`, 2880 px, parallel fat lines. **This one becomes the raw-salmon texture.**
  - Comparison images are in `scratchpad/samples/`.

### Step 4: 3D garnish, Batches C + D (approved: detailed, 74 credits)
1. **Batch C:** 4 clean source photos on a neutral background, `gpt_image_2_5` medium 1k at 0.5 each (2 credits): kimchi mound in the black bowl, frisée bunch, pickled-ginger rose, wasabi ball.
   - References are the photos listed under Inputs.
   - The kimchi photo is HEIC. In the Higgsfield sandbox I download it from its Drive link, convert it to JPG and upload it there, because the sandbox can reach Higgsfield's upload host and this container can't. This step is free.
2. **Batch D:** 4 × `generate_3d` with `tripo_h3_1_image_to_3d`, detailed texture and geometry, 18 each (72 credits).
3. **Slim and transfer (free):**
   - In the sandbox, `npx @gltf-transform/cli optimize` brings each mesh to ≤1.5 MB: WebP textures ≤1024, simplified geometry, meshopt compression.
   - The GLB bytes travel to this container packed into PNG files through `sandbox_exec` `image_paths` (≤480 KB each), which arrive byte-exact. I unpack them locally and check them against their SHA-256 hash.
4. **Code:**
   - Load the meshes with `GLTFLoader` (with `MeshoptDecoder` from `three/addons/libs/meshopt_decoder.module.js`).
   - Kimchi goes in the bowl; ginger, wasabi and frisée go in the `PARTY_GARNISH` spots and the promo-tray corners and wedges.
   - Their materials join `dimmables`.
   - The hand-built `makeFrisee` / `makeGinger` / `makeWasabi` / `kimchi` stay as the fallback.

### Step 5: ship the assets
- Assets publish as supporting files under `assets/` and load by relative path.
- If `.glb` is refused as a file type, I serve the meshes as base64 inside a `.js` module.
- A `THREE.LoadingManager` drives a "טוען…" overlay with progress.

### Step 6: stills and video (optional, priced per use)
- Stills: an image-to-image pass over "שמור פריים" frames.
- Video: camera moves recorded from the live model.
- Each still or clip is priced and approved on its own when you ask; none of it is in this plan's credits.

---

## Part B: new work

### Step 7: ultra-realistic textures
**7a. Free upgrades (no credits)**
- **Full-size originals:**
  - Download the full 1024 px originals of the 17 Batch A + B images in the sandbox. Bring them over one or two per `image_paths` call as JPEG q92.
  - Rebuild them with `scratchpad/photos/finalize.py`: faces at 1024 RGBA, tiles at 1024, seamless.
- **Depth and shine maps** for every tile, filling and face, built with a new local script `scratchpad/photos/pbr.py`:
  - a **normal map** from brightness (Sobel, strength per material)
  - a **roughness map**: glossy fish and avocado, matte rice and crumbs
- **Material wiring:** in `index.html` the materials switch from `bumpMap` to `normalMap` + `roughnessMap`, and the photo textures get full anisotropy.

**7b. Batch E: 8 filling textures at 2k (approved: 22 credits)**
- **Job:** `generate_image_batch` with `gpt_image_2_5`, quality high, resolution 2k, 1:1. 8 × 2.75 = 22 credits.
- **Textures:** seared salmon (tataki top), cooked salmon, spicy salmon, tuna mayo, avocado flesh, cucumber (seeded flesh with skin edge), carrot, green onion.
- **Prompt:** the same pattern as the salmon sample: "seamless tileable macro texture, filling the frame, flat even light, top-down". The fat lines and grain run parallel, not in a V.
- **References:** WA0031 for avocado, cucumber, carrot and tuna mayo; WA0037 for tataki; WA0045 for cooked and spicy.
- **Transfer:** each 2k result comes over as four 1024 JPEG quarters through `image_paths` and is stitched back together locally. I fix the seams, then make normal and roughness maps.
- **Code:** these replace the hand-drawn `salmonTex`, `searTex`, `cookedTex`, `tunaMayoTex`, `spicyTex`, `avoInTex` and the flat-colour `cuc`, `carrot` and `onion` materials. They're loaded only on the first tap of a roll, so the tray opens fast.

**7c. Rendering realism (free)**
- **Studio reflections:** replace `RoomEnvironment` with a studio environment of soft light panels baked through `PMREMGenerator`. One big softbox sits at the upper left over the key light and a strip light sits behind, so the lacquer, fish and avocado show real reflections.
- **Fish and avocado:** `MeshPhysicalMaterial` with sheen, clearcoat and a soft light-wrap tweak (`onBeforeCompile`) so salmon and tuna look translucent instead of plastic.
- **Effects:** an `EffectComposer` from three's addons:
  - `GTAOPass` darkens the contact points between rolls and in the tray corners. This is the biggest realism gain.
  - `BokehPass` adds a gentle depth of field only in the close-up of one piece.
  - `SMAAPass` and `OutputPass` finish the frame.
  - On slow devices the effects switch off automatically (see 8d).
- **Close-up geometry (hero piece only):**
  - instanced rice grains (about 1,500) on the outer rice and the cut faces
  - instanced panko and tempura flakes on the coating
  - sesame seeds, which already exist
  - The tray copies keep the textures, so performance holds.

### Step 8: smoother handling
**8a. Camera**
- Replace `OrbitControls` and the camera tweens with `camera-controls@2.9.0` from jsdelivr: `CameraControls.install({THREE})`. I'll confirm the version on npm before use.
- It gives damped moves that you can grab mid-flight (`setLookAt(...,true)`, `fitToBox`).
- Pinch to zoom, zoom toward the cursor, and double-tap to zoom in.

**8b. No more locks**
- Drop the `busy` gate.
- The hero position, take-apart amount and tray dimming each ease toward a target every frame (`THREE.MathUtils.damp`). A new tap simply sets new targets, so changing your mind mid-move is smooth.
- Changing trays plays a short staggered drop-in of the pieces instead of an instant swap.

**8c. Feedback**
- On a computer, hovering over a roll lifts it slightly and shows its name in a small label. The cursor becomes a pointer.
- Auto-rotate comes back slowly after 6 seconds without input.
- "‹ ›" buttons in the bottom sheet jump to the next or previous roll type without going back to the tray.

**8d. Frame rate**
- **No first-tap stutter:** `renderer.compileAsync` and a hidden prebuilt hero piece compile every shader during loading.
- **Fewer draw calls:** the static tray meshes merge into one mesh per material (`BufferGeometryUtils.mergeGeometries`).
- **Cheaper shadows:** `shadowMap.autoUpdate = false`; shadows refresh only while something moves.
- **Adaptive sharpness:** the pixel ratio steps 2 → 1.5 → 1 if frames run over about 22 ms, with ambient occlusion and depth of field off at the lowest step.
- **Idle rendering:** when nothing moves, the page renders only on demand, which saves battery.

### Step 9: inspecting single ingredients (like the Red Dragon and nigiri models)
- **Layers:** each `ROLLS` entry gets a layer table, built in `rollPartsBase()` with a label (Hebrew name + one-line description), a take-apart offset, a label anchor and a side.
  - The labels come from `FILL_HE` / `COAT_HE`, expanded. For example: "אבוקדו · פרוס דק בתוך הרול", "נורי · עוטף את המילוי", "פנקו ורוד · פירורים פריכים".
- **Take-apart layout:** the same as Red Dragon:
  - the rice slides left
  - the nori goes between
  - the fillings fan out to the right in a row
  - the coat and seeds lift up
  - Maki have their own variant.
  - The camera frames the whole set with `fitToBox`, so it fits a phone held upright.
- **Labels:**
  - Port `updateLabels()` from Red Dragon: `.lbl` pills with gold pointer lines into `#lines`.
  - Labels never overlap (a quick spacing pass on screen) and stay inside the screen.
  - The labels can be tapped.
- **One ingredient up close:** tap a part, its label, or its chip in the sheet (a new row of ingredient chips). That ingredient:
  - moves forward and grows 1.6×
  - the others fade to 15% (transparent copies of their materials, hero only)
  - the camera moves in, and the sheet shows the ingredient's name and description
  - "‹ ›" steps through the ingredients; "כל המרכיבים" or tapping empty space goes back.
- **Faces:** the photo cut faces stay on the whole piece and fade out as it comes apart, so taking it apart shows the real layers.
- **Garnish:** kimchi, ginger, wasabi and frisée can be tapped too. The camera glides to them and shows a name label.

---

## Verification
1. **Renders:** extend `scratchpad/trays/shot3.js`.
   - It routes `camera-controls` and three to local `node_modules` and waits for a `window.__ready` flag.
   - Shots: party top / 3/4, promoL top / 3/4, a piece close up, taken apart with labels, a single ingredient up close, and the garnish.
   - Build side-by-side images against `trayCut` / `trayB` and check the colors, contact shadows and labels on screen.
2. **Interaction script (same browser):**
   - tap a roll, then press back at once
   - switch trays during a move
   - take apart, then use the chips, the ‹ › arrows and Escape
   - It asserts no console errors, a return to the tray state, and labels hidden in tray mode.
   - It logs `renderer.info` draw calls before and after the mesh merge.
3. **Size budget:**
   - The tray view loads ≤10 MB of assets (faces, tiles, garnish meshes); the fillings load only on the first tap.
   - Every file stays under the artifact limits.
4. **Publish and show:**
   - Publish to the same 3D link.
   - Update the comparison canvas (https://claude.ai/artifact/YKotpQpHV1MKYLMLfox8mg): upload the new renders as assets and point `Main.dc.html` at them.
   - Report what changed, credits per batch, and what still differs from the photos.

## Credits
| Batch | Tool / model / settings | Credits | Status |
|---|---|---|---|
| A, cut faces ×10 | generate_image_batch / gpt_image_2_5 / high 1k | 15 | spent |
| B, tiles ×7 | same | 10.5 | spent |
| Salmon samples ×2 | gpt_image_2_5 / high 2k + 4k | 7 | spent |
| E, fillings ×8 | generate_image_batch / gpt_image_2_5 / high 2k | 22 | approved |
| C, garnish photos ×4 | generate_image_batch / gpt_image_2_5 / medium 1k | 2 | approved |
| D, garnish meshes ×4 | generate_3d / tripo_h3_1_image_to_3d / detailed | 72 | approved |
| **Total** | | **128.5** (32.5 spent + 96 to run) | about 307 of 436 left after |

---

## Status: version 5 published (2026-10-26)
- **Live:** https://claude.ai/artifact/T4kXJSfCbqVD8ErwXrpFsL (version 5). Comparison canvas updated: https://claude.ai/artifact/YKotpQpHV1MKYLMLfox8mg (version 3).
- **Done:** Steps 4, 5, 7, 8 and 9 as planned, with these differences:
  - The artifact host refuses `.glb`, so the four scanned meshes ship as base64 inside `assets/g-<name>.glb.js` modules. The raw meshes are kept in `meshes/`.
  - On narrow screens the taken-apart layers sit in two columns, and the camera frames boxes per axis rather than a sphere.
  - In single-ingredient view the other layers fade out completely.
- **Credits actually spent this round (103):**
  - Salmon samples: 7
  - Batch E: 22
  - Batch C: 2
  - Batch D: 72. The first kimchi and ginger meshes failed on Higgsfield's side and were refunded; your approved retry cost 36.
  - Balance: 307.5.
- **Generated media:**
  - Fillings (gpt_image_2_5 high 2k): sear `08b2b9d3`, cooked `260e69e7`, spicy `9d464dca`, tuna mayo `0b7abda6`, avocado `79f8c077`, cucumber `ddd7d5ee`, carrot `ca4f6f0a`, green onion `bca839c7`.
  - Garnish photos (medium 1k): kimchi `66ecac66`, ginger `0f006db5`, wasabi `9366c6ad`, lettuce `a0fbf313`.
  - Meshes (Tripo detailed): wasabi `ef3a44d2`, lettuce `824d153c`, kimchi `ea69a09e`, ginger `32db1546`.
  - Garnish reference uploads: kimchi `e842cffb`, ginger `d7896430`, wasabi `7684ab4f`, lettuce `9151c174`.
- **Not finished:**
  - The interaction test (`tools/interact.js`) was stopped mid-run. Its fixed waits are too short for the slow software renderer, and it needs condition-based waits before it can pass.
  - A real-device check of frame rate on a phone.
