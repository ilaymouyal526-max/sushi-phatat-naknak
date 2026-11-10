# HANDOFF: Yoko Ono dice-game video

Updated after every step. **Last update: v6 is finished and delivered (master, screen loop, 15 s cut). Waiting for the user's feedback on the film.**

## v6 (current): a quality rebuild
- **Brief:** `../dice-explainer-v6-brief.md`. Content, rules and structure stay as approved; the goal is quality (cards, type, motion, rhythm, realistic objects, SFX timing).
- **Branch:** `ccr-56b6f5ef-labe3t`, built on top of v5 (`ccr-a63b5673-0h297p`).
- **Plan (approved):**
  1. Props: re-render (free) and show v5 next to v6. **Done; approved.**
  2. Stills: a mid-card frame of every card, v6 next to v5. Rewrite `build.py` (layout grid, type scale, textures). **Done; approved.**
  3. Motion and SFX from one event table, all times in beats. QA: lint 0/0, `check`, freezedetect, frame sheet. **Done.**
  4. Deliverables: master (about −16 LUFS), silent screen loop, 15 s Stories cut (`tools/derive.sh`), compressed copies. Script, SPEC and HANDOFF updated. **Done and sent.**
- **Not without a "yes":** the hand in Kling (still 0.25 + Kling std 3 s 4.5). The Instagram handle stays `@[instagram]`.

### v6 stage 1: props (done)
All renders are local and free: `node tools/render_props.js [dice|hand|receipt|coin]`. It ends with an **edge check** that
fails if any prop (or any frame of a tumble strip) touches the frame edge, so nothing is ever cut off on screen.
- **Dice** (`tools/dice.html`):
  - **Why v5 failed:** the transmission pass blurred the far pips into blobs, and the tumble was 12 random poses swapped every 1/12 s (it read as flicker).
  - **The body** is now an alpha-blended acrylic shell (front opacity 0.95, dark-red back faces). The opaque pips render first, so the far pips stay crisp and only faintly visible.
  - **The pips** are drilled and filled flush, with rounded edges (r 0.07). The cube spans about 53% of its frame, so it can spin without clipping.
  - **Bug fixed:** v5's rotation table had faces 2 and 5 swapped.
  - **Output:**
    - `die-{1..6}{a,b}.png`: 1024 px rest poses, two variants (a, b) with different yaw.
    - `die-strip-{1..6}{a,b}.webp`: 24 frames of a continuous tumble that decelerates onto that face, with motion blur (6 sub-frames, quarter-frame shutter), 512 px cells in a 6 × 4 grid.
    - Variant b uses other rolling axes, so a double never looks like a mirror copy.
  - **No baked shadow:** the film draws the shadow, so it stays on the felt while the die is in the air.
- **Hand** (`tools/hand.html`):
  - **Why v5 failed:** separate cylinders and spheres left seams, and the fist was rotated wrong.
  - **Now:** one signed distance field (round-cone bones smooth-unioned into the palm, knuckles, nails, wrist), raymarched in a shader. Wrap lighting with a red terminator for the skin; soft shadows and AO; navy sleeve, white cuff, gold cufflink. Rendered 2× and downsampled.
  - **Poses:** `hand-{open,release,fist,flat}.png` (800×1280). `flat` is new, for the waiter in card 3b. The thumb is no longer cut off.
- **Receipt** (`tools/props.html`, `receipt.png`):
  - thermal paper with torn edges and a curl at the top;
  - the logo (`assets/img/logo-ink.svg`, exported from `logo_svg` in `build.py`) and Hebrew lines: address, "חשבון לשולחן", 8 dishes, "לתשלום", a barcode, "תודה, ובהצלחה בקוביות!";
  - **no prices.**
- **Coin:** struck gold with a reeded edge (120 reeds), a rim, a bead ring and the logo's mountains and sun in relief. `coin.png` plus `coin-settle-0..11.png` (it lands and wobbles flat).
- **Removed:** v5's `die-1..6.png` and `die-roll-0..11.png`. The v5 build still references them, so stage 2 rewrites `build.py`.
- **For review** (gitignored, `review/`): `props-v5-v6.png` and `dice-tumble-v5-v6.mp4`.

### v6 stage 2: stills (done)
`build.py` is rewritten from scratch (v5's is in git at `7e7a0a6`). Lint is 0/0. `assets/dice-kit.js` is rewritten too.
- **Timing:** every card length is in beats (`card(id, beats, ...)`); the build asserts each cut is on a beat. The total is still 109 beats = 68.125 s, and the card order and lengths are the same as v5.
- **Design system** (`BASE_CSS`):
  - one type scale, embossed gold foil (`.foil`), ivory headlines with a drop shadow;
  - the rule header is a gold medallion between two hairlines (`rule(n)`);
  - every die has a shadow under it (`shadow()`);
  - the ground is a lacquer texture (`tex-noir.jpg`) with a warm glow whose height each card sets (`--glow`);
  - the frame has stepped corners.
- **Baked motion:** throws are computed in Python frame by frame and emitted as `DiceKit.bake` / `DiceKit.spin` calls (only `tl.set`, so any seek gives the exact frame). The same code calls `sfx(card, time, file, volume)`, so sound cues come from the picture's own events. `index()` merges cues that land on the same frame.
- **The dice table (6a, 6b):** `Table` is real CSS 3D: felt, three standing walls lined with felt, walnut rims. The dice are screen-space sprites placed through `Table.proj()`, the same camera. `throw_sim` is a small physics sim (gravity, bounces, wall rebound, rolling friction); `tune_throw` finds the speed that leaves a die at a chosen spot, with or without touching the far wall; the wall hit lands on beat 2.
- **Tumbles:** `spin_keys(n)` picks the strip frames. A long tumble loops the fast first 10 frames, then plays the last 14 once into the rest pose.
- **New props** (`node tools/render_props.js table` and `tex`): `plate.png`, `folder.png` (leather bill folder with the logo in gold), `tray.png` (lacquer tip tray), and the textures `tex-felt/walnut/walnutv/gold/noir.jpg`.
- **Hand:** the frames are now 800×1760, so the sleeve always runs off the screen edge.
- **Card by card, what changed from v5:**
  - **Opening felt:** real felt texture, bigger hand, long sleeve.
  - **1:** bigger dice that hang and turn in front of the lens.
  - **2:** a red scalloped "חדש" seal.
  - **3a:** the dial got a crown, a glass highlight and leather strap ends, so it reads as a wristwatch.
  - **3b:** a walnut table seen from above, with rendered plates, sake cups and the leather bill folder.
  - **4:** the dice roll in and stop under the ×1.
  - **5:** a bevelled gold picture frame and a slow spotlight on the roller.
  - **6a, 6b:** the table has real walls; wall-hit flashes; the trails appear after the dice stop.
  - **7:** no knife. The whole receipt sits under the subline and a red "−50%" stamp lands on it.
  - **8:** a gold-leaf ground with rays; the bill bursts into 8 torn pieces on the jackpot beat; petals and gold leaf fall for the whole card.
  - **9:** a gold bowl with chopsticks and moving steam.
  - **10:** the lacquer tray, bigger coins, the coin settles frame by frame, then twinkles.
  - **11:** a gold phone with a recording pill. There is no "REC" text any more (Hebrew only): a white dot and a running timer.
  - **12:** the same layout, tightened.
- **For review** (gitignored, `review/`): `stills-v5-v6-1.png`, `-2.png`, `-3.png` (18 shots, v5 next to v6).

### v6 stages 3 and 4: motion, QA and the deliverables (done)
- **QA results on the master:**
  - `lint`: 0 errors, 0 warnings.
  - `check --json`: ok. No errors or warnings in runtime, layout, contrast, craft (`dead_stretch` is clean) or audio; 19 layout infos, all the dice strips overflowing their window on purpose.
  - `freezedetect` (3 s): no freezes.
  - Every throw was looked at frame by frame (`renders/qa/throw-*.jpg`): no dropped strip frames, and the wall hits and stamps land on their beats.
  - Loudness: −16.0 LUFS integrated, peak −3.3 dBFS.
- **Gotcha:** the craft checker ignores anything under `data-layout-ignore`, so a card whose only motion is inside such an element is reported as a dead stretch. Moving elements use `data-layout-allow-overflow` instead.
- **Polish after the first draft:** the thrower's hand rises, pulls back and flicks on the release; the dice in card 1 keep turning through the hang; bigger dice in card 7; the coin's environment got warm walls so it stays gold while it tumbles.
- **Deliverables** (`renders/` is gitignored; re-render to get them back):
  - `yoko-dice-reels-master.mp4`: 68.125 s, 1080×1920, 24 fps, delivery quality, 238 MB.
  - `yoko-dice-screen-loop.mp4`: the same picture, silent.
  - `yoko-dice-15s.mp4`: 15.0 s. Beats: chef 5–11, perfect throw 55–60, −50% 65–70, jackpot 73–77, end card 99–103.
  - `*-send.mp4`: compressed copies (the master is 10 MB).
- **Decisions to confirm with the user:** the red "−50%" stamp on the receipt in card 7 (an addition, the same copy), and the timer instead of "REC" in card 11.
- **Not done:** the production-log artifact from the earlier sessions was not updated in this session.

### Commands (v6)
```bash
cd commercial/dice-explainer
export HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
node tools/render_props.js                         # only when a prop changes (about 3 min); ends with the edge check
python3 build.py                                   # index.html and compositions/
npx -y hyperframes@0.8.226 lint                    # expect 0/0
npx -y hyperframes@0.8.226 check --json            # the gate
npx -y hyperframes@0.8.226 render --quality draft -o renders/draft-v6.mp4        # about 3 min
npx -y hyperframes@0.8.226 render --quality delivery -o renders/master-raw.mp4   # about 4 min
tools/derive.sh                                    # master at -16 LUFS, screen loop, 15 s cut, chat copies
tools/qa.sh renders/yoko-dice-reels-master.mp4     # freezes, card sheet, every frame of each throw, loudness
```

---
Everything below is the history up to v5. Its file list and commands describe the v5 build.

## What this is
An animated 9:16 Hebrew ad (1080×1920, 24 fps, about 68 s) for the dice game at **Yoko Ono Asian Kitchen** (Ahuza 124, Ra'anana).
- **Built with:** HyperFrames (HTML + GSAP rendered to MP4), locally and for free.
- **Branch:** `ccr-a63b5673-0h297p`, repo `ilaymouyal526-max/sushi-phatat-naknak`.
- **Folder:** `commercial/dice-explainer/`.

## Hard rules from the user
- **Spending:** never spend credits, tokens or money without showing the tool, the cost (from `get_cost`) and getting a clear "yes" (`/CLAUDE.md`). Higgsfield is allowed only after a price check and approval.
- **Language:** Hebrew only, RTL. No French or English copy, on screen or in the VO.
- **No building animation:** every card is complete from its first frame (no draw-on, no word-by-word text, no wipes). Only the action moves, continuously, without stop-start.
- **Look:** Noir & Or cards (black #0b0907, gold #c9a36b, ivory, red #b8322a), Frank Ruhl Libre + Heebo. The objects in them must look realistic.
- **House rules:**
  - "*בכפוף לתקנון" on every card.
  - The full line on the end card: "בכפוף לתקנון. את התקנון המלא אפשר לבקש מהמלצר."
  - An invalid throw (only one die hits the far wall) is re-rolled. The user confirmed this.
- **Happy hour:** 16:00–18:00. There is no minimum order.
- **Dice:** Vegas casino dice: translucent red acrylic, white pips.
- **Workflow:** plan mode, plus a short version of the plan, before big changes. Stills before animating. Keep the production log updated, and update this file after every step.

## Structure
| Time | Part | File(s) |
|---|---|---|
| 0–9.375 s | Opening with characters (P1 asking for the bill, P2 cashier "לא, לא, לא… קודם מטילים את הקוביות!", P3 surprise, then the hand scoops the dice) | 3 Higgsfield clips as `<video>` in `index.html` (`CLIPS` in `build.py`: `assets/hf/P1-3-fit.mp4`), plus the `p1`/`p2`/`p3` overlays (bubbles, the "?!" marks, the felt close-up from 8.125 s) |
| 9.375–68.125 s | 14 explainer cards (s1 hook … s12 end card), shifted by `INTRO` | `compositions/s1…s12.html` |
| 9.375 s on | Gold frame, grain, "*בכפוף לתקנון" footer | `compositions/frame.html` |

## Key files
- `build.py`: **source of truth.** It generates `index.html` and every file in `compositions/`. Edit it and run `python3 build.py`; never hand-edit the generated HTML. It holds:
  - the cards: `card(...)` calls;
  - the per-card motion: the `MOTION` dict;
  - the SFX cues: `SFX`, shifted by `INTRO`;
  - the opening: `INTRO_CARDS`, `A3D`.
- `assets/dice-kit.js`:
  - `DiceKit.mount`, `setFace`, `setRoll` (12 tumbling poses), `tumble`, `pose` (the hand: fist, release, open).
  - The dice are now `<img>` renders from `assets/img/`.
- `assets/hf/`: the Higgsfield stills (`F1-3.png`) and the opening clips fitted to 1080×1920 at 24 fps (`P1-3-fit.mp4`; P1 is stretched to 3.125 s, P2 is trimmed to 3.75 s, and only the first 1.25 s of P3 is used). The raw Kling outputs are in `sources/`.
  - Clip jobs:
    - P1 `86a65910-b2c0-498e-aafb-11419ca2362f`;
    - P2 `cff585d6-4677-4b7b-917f-1495b7e486d1`;
    - P3 `8ffc6d23-3712-4572-ac75-576dab9e4cfe`.
  - The old Three.js opening (`avatars3d.js`, `a3d.html`) has been removed.
- `tools/props.html` + `tools/render_props.js`: realistic props rendered once with Three.js + Playwright into `assets/img/`: `die-1..6.png`, `die-roll-0..11.png`, `receipt.png`, `coin.png`, `knife.png`, `hand-fist/release/open.png`. Run it with `node tools/render_props.js`.
- `assets/vendor/`: `gsap.min.js` 3.15.0 and `three.min.js` r159. Both are local, because jsdelivr is blocked.
- `assets/sfx/`: Pixabay SFX bundled with HyperFrames, plus `manifest.json` (lengths).
- `SPEC.md`: the numbers and rules (v2). It needs updating for the opening and the realistic props.
- `../dice_game_script.md`: the original script. **Out of date** (still trilingual); it needs a Hebrew-only rewrite.
- `../reference/`: `dice_table.jpg` (green felt, walnut, gold logo) and `dice_on_table.jpg` (the real red dice).
- The user's reference images (this session's scratchpad `images/`):
  - `1.webp`: the Pixar-realistic style, and **the man who pays**.
  - `2.png`: the blue-and-gold boho booth, the couple's table.
  - `3.png`: the chef in a black cap and brown apron, and **the payment bar** with the yellow LED strip.
  - `4.png`: two staff guys.

## Commands
```bash
cd commercial/dice-explainer
export HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
python3 build.py
npx -y hyperframes@0.8.226 lint                    # expect 0/0
npx -y hyperframes@0.8.226 check --json            # gate
npx -y hyperframes@0.8.226 snapshot --at 1.6,5.6,... --output <dir>
npx -y hyperframes@0.8.226 render --quality draft -o renders/draft-vN.mp4   # ~8 min with the 3D opening
ffmpeg -i renders/x.mp4 -c:v libx264 -crf 27 -c:a aac -b:a 128k -movflags +faststart renders/x-preview.mp4   # to send
```
`renders/` and `.hyperframes/` are gitignored.

## Done so far (latest last)
1. Script, then a Hebrew-only v2: 14 Noir & Or cards, the gold watch-dial clock, action-only motion, grain and SFX. Draft v2 sent.
2. An avatar opening (SVG), then 3D Three.js Pixar-lite characters, plus Vegas dice. Drafts v3 and v4 sent. Commits up to `1b7d547`.
3. The production log artifact: https://claude.ai/artifact/UBAGerWZkhMab4mazJYhcQ. Update it after each step.
4. **Stage 5 (approved plan):**
   - **5a, the Higgsfield designer subagent.** It runs in the background: uploads the references, writes the prompts, and runs **price checks only**, with no generation.
     - F1: the man from img 1 and his girlfriend in the img 2 booth; he raises his hand.
     - F2: the img 3 bar. The chef from img 3 is behind it with the two guys from img 4 next to him; the man from img 1 hands over a card; the chef wags his finger and points at the dice table.
     - F3: the couple, surprised.
     - F4: a hand scooping the dice off the felt.
     - Clips on seedance_2_5 or kling3_0. intone for lip-sync, though Hebrew lip-sync probably isn't possible.
     - The subagent stopped early because its video price checks were rejected. The main session finished the price checks:
       - images (`gpt_image_2_5`, 9:16, with refs): low 1k 0.25, medium 0.5, high 1k 1.5, high 2k 2.75;
       - clips (`kling3_0`): std 3 s 4.5, std 4 s 6, pro 4 s 7; `seedance_2_5`: 720p 28, 1080p 64.
     - The user chose **the cheapest route**: low-quality stills and Kling std. The whole opening comes to about 15.75 credits.
     - **Uploads:** `upload.higgsfield.ai` was blocked by the network policy; the user then allowed it. Refs uploaded and confirmed:
       - img1 man `e333d4b9-5746-42c4-884c-68d064c389bc`;
       - img2 booth `d692f40a-ec03-45c8-96e0-a9a06d90b57b`;
       - img3 chef/bar `ad5dadd3-f5f7-4ac2-946d-d7cc8d094cf7`;
       - img4 staff `7f7d5e29-faae-4fe6-87d8-f3a6884f0ba5`.
     - **Samples generated (approved, 0.25 each):** saved in `assets/hf/`.
       - F1 (job `6f90e3ba-7198-4452-9524-274d056db80c`) → `F1.png`;
       - F2 (job `ba72fdcf-ea0b-4bbf-83a3-dc2b8997d92d`) → `F2.png`.
       - F3, the couple surprised (job `7f5ea3e2-4055-4783-a85e-f8f6195d0923`) → `F3.png`. It used F1 as a reference so the couple stays identical.
     - **Balance check:** 1183 → 1171.5. The transactions show this session's 2 × 0.25 (15:13 on 4/11), plus 4 GPT Image high 2k spends at 2.75 each, 11 credits in all, made outside this session (3 at 23:04 on 3/11, 1 at 13:43 on 4/11). The user was told.
   - **5b, realistic props (free, in progress).**
     - Rendered: translucent dice (6 faces + 12 rolls), receipt, coin, knife.
     - DiceKit now uses the dice images. Cards 7 (receipt, knife) and 10 (coins) use the renders.
     - **Reviewed and tuned:**
       - tighter die framing, soft shadow (radius 18);
       - the receipt's right half uses `receipt.png#right-half` to clear lint's duplicate-media warning.
     - Lint 0/0. Snapshots look right on s1, s2, s3b, s4, s7, s8, s11 and s12.

## Next steps
1. ~~Snapshot and tune the props~~ (done).
1b. ~~Realistic hand~~ (done): `renderHand(pose)` in `tools/props.html` builds the hand.
    - **Hand:** a superellipsoid palm; tapered fingers with real joints; nails; a thumb mound.
    - **Clothing:** white cuff, gold cufflink, navy blazer sleeve.
    - **Output:** renders to `assets/img/hand-{fist,release,open}.png`. `hand_svg()` in `build.py` now stacks those 3 images, and `DiceKit.pose` switches them (same API).
    - Lint 0/0. Snapshots look right in p3, s1, s3b, s6a, s6b and s12.
2. ~~Cost table, sample stills F1 and F2~~ (done). **Now:** wait for the user's verdict on F1 and F2. Next spends, each with its own approval:
   - F3 (0.25);
   - Kling std clips P1 3 s (4.5), P2 4 s (6), P3 3 s (4.5).

   F4 (the hand scooping the dice) stays in code.
3. ~~Integrate the clips~~ (done; lint 0/0). Draft v5 (`renders/draft-v5.mp4`) was rendered, freezedetect found no freezes, and the preview was sent. **Waiting on the user's feedback.**
4. ~~Characters in cards 5 and 11~~ (done). The user approved 2 more stills at 0.25 each, 0.5 in all; the balance is now 1155.75.
   - `assets/hf/S5.png` (job `8ed8d89f-a83f-4032-bab4-f937244d1d3b`): four friends point at the man holding the dice. It sits in a gold frame (900×1080) with a slow push-in.
   - `assets/hf/S11.png` (job `59180353-76ea-41a9-a4dd-05286936674f`): the couple celebrate a double six. It sits inside the enlarged phone with a punch-in on each flash.
   - The old drawn diners and figures were removed. Lint is 0/0 and `check` passes.
5. ~~Rewrite `../dice_game_script.md` (Hebrew only) and `SPEC.md` (v5)~~ (done).
6. ~~Final renders~~ (done; `renders/` is gitignored, so re-render to get them back):
   - `yoko-dice-reels-master.mp4`: delivery quality, 68.125 s, −16.1 LUFS, peak −1.6 dBFS, no freezes.
   - `tools/derive.sh` → `yoko-dice-screen-loop.mp4`: silent.
   - `tools/derive.sh` → `yoko-dice-15s.mp4`: the chef, the perfect throw, −50%, the jackpot and the end card.
   - The `*-send.mp4` files are compressed copies for chat.
7. When the user sends the Instagram handle: replace `@[instagram]` in `build.py` (card s12), then re-render the master and run `tools/derive.sh`.

## Feedback round 1 (after the finals)
- **Card 7:** the knife moved sideways while the receipt split top to bottom, which looked odd. The user asked to drop it. The knife, the split and their two SFX are removed; the whole receipt now sits under the subline (430 px wide). `knife.png` and `renderKnife` are deleted.
- **Dice:** they "didn't look like dice". There were two causes: the camera was framed too tight, so the die was cut off at the image edges, and the high transmission refracted the far pips into blobs. Fixed with a rounded cube (r 0.06), denser acrylic (transmission 0.35), a wider camera ([0.32, 4.3, 1.55]) and tumble height 0.62. DiceKit draws each image at 144% so the dice keep their size on screen.
- **Hand:** the user wants the hand scene made in Kling too. Priced: still 0.25 + Kling std 3 s clip 4.5. **Not generated; waiting for a yes.**

## Still open with the user
- The Instagram handle for the end card (currently `@[instagram]`). The user will upload the restaurant's site.
- Feedback on the new opening characters (after the Higgsfield samples).
- Music: the user adds a track in the platform editor. Voices and VO: the user records them.
- Assumed: the chef and the two staff members agreed to appear as characters.

## Shot list for the owner
- `../yoko-dice-shotlist.pdf` (8 A4 pages, 0.5 MB): 18 shots, each with a thumbnail, the time, the on-screen text, what happens, and boxes for להשאיר / להעיף / לשנות. The last page lists what still needs a decision.
- To rebuild it from a new draft: `NODE_PATH=$(npm root -g) python3 tools/shotlist.py renders/draft-vN.mp4`, which also runs `tools/shotlist_pdf.js`.
