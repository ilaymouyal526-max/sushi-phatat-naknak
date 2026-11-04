# HANDOFF: Yoko Ono dice-game video

Updated after every step. Last update: the 3 Kling clips are generated (15 credits, approved; balance 1156.25) and wired in place of the 3D opening. Draft v5 is rendering.

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
3. ~~Integrate the clips~~ (done; lint 0/0). **Now:** draft v5 (`renders/draft-v5.mp4`), freezedetect, send to the user.
4. Make the hand and the characters in cards 1, 5, 6a, 6b, 11 and 12 match the new realistic style.
5. Rewrite `../dice_game_script.md` and `SPEC.md` in Hebrew only for the current film.
6. Final renders: the Reels master, a silent loop for the restaurant screen, and a 15 s cutdown.

## Still open with the user
- The Instagram handle for the end card (currently `@[instagram]`). The user will upload the restaurant's site.
- Feedback on the new opening characters (after the Higgsfield samples).
- Music: the user adds a track in the platform editor. Voices and VO: the user records them.
- Assumed: the chef and the two staff members agreed to appear as characters.
