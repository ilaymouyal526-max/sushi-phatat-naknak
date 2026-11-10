# SPEC: Yoko Ono, "הטילו את הקוביות" (v6, Hebrew)

The storyboard and words live in `../dice_game_script.md` and in `build.py`. This file holds the numbers and the rules.

```text
GOAL:    A guest knows exactly how to play: happy hour 16:00–18:00, end of the meal, one roller, one valid
         throw off the far wall (a miss is re-rolled), double 1–3 = −50%, double 4–6 = the meal is on us,
         tip not included, winners filmed. Everything is subject to the house rules, which the waiter has.
OUTPUT:  HyperFrames, 1080 x 1920, 24 fps. A Reels master with SFX (no VO), a silent loop for the
         restaurant screen, and a 15 s cutdown.
TIME:    109 beats = 68.125 s = 1635 frames. 96 BPM: 1 beat = 15 frames = 0.625 s.
         Card lengths in beats: p1 5, p2 6, p3 4 | s1 4, s2 6, s3a 6, s3b 6, s4 6, s5 6, s6a 6, s6b 10,
         s7 8, s8 8, s9 4, s10 6, s11 8, s12 10. build.py asserts that every cut is on a beat.
OPENING: Three Higgsfield clips (Kling std, from gpt_image_2_5 stills, Pixar-realistic). P1, beats 0–5:
         the couple asks for the bill. P2, beats 5–11: the chef: "לא, לא, לא… קודם מטילים את הקוביות!".
         P3, beats 11–13: the couple is surprised. Then beats 13–15: the felt close-up in code (the hand
         scoops the dice). The Hebrew speech bubbles are overlays. No frame or footer during the opening.
LANGUAGE: Hebrew only, RTL. Times and percentages sit in LTR isolates. No English on screen except the
         restaurant's own logo; the phone in card 11 shows a dot and a timer, not "REC".
LOOK:    Noir & Or poster cards. Ground: black lacquer #0b0907 (tex-noir.jpg) with a warm glow whose
         height each card sets (--glow). The double gold rule with stepped corners (static), and grain at
         11% overlay, stepped 12x a second.
         Gold #c9a36b. Gold foil text: a gradient #a8814a→#fff1c9, embossed (a 3 px dark edge and a soft
         drop shadow), swept once per card. Ivory #f4ecdf headlines with a drop shadow.
         Red #b8322a (seal, ribbon, stamps).
         Card 8 is a gold-leaf ground (tex-gold.jpg) with slow rays.
         Type: Frank Ruhl Libre 800 headlines at 100–156 px, Frank Ruhl 500 sublines at 50–64 px in
         light gold, Frank Ruhl 700 figures at 300–430 px, Heebo for small type and the house-rules note
         (28 px footer; 34 px on the end card). Rule cards open with the rule number in a gold medallion.
         Text band: every readable line sits within y 190–1330, except the fixed footer note.
OBJECTS: Realistic 3D renders (tools/*.html → assets/img, `node tools/render_props.js`):
         Dice: Vegas dice in translucent red acrylic with flush white pips. An alpha-blended shell, so
         the far pips stay crisp. Rest poses at 1024 px and 24-frame motion-blurred tumble strips onto
         each face, two variants. No baked shadow: the film draws the shadow on the surface.
         Hand: one SDF surface raymarched in a shader; poses open, release, fist, flat; navy sleeve,
         white cuff, gold cufflink; frames are 800 x 1760 so the sleeve runs off the screen.
         Receipt: Hebrew thermal paper with the logo, torn edges, NO prices.
         Coin (reeded, with relief) and its 12-frame settle; lacquer tip tray; leather bill folder with
         the logo in gold; stoneware plate with chopsticks; felt, walnut, gold-leaf and lacquer textures.
         The render fails if any prop touches its frame edge.
         The dice table (6a, 6b) is CSS 3D: felt, three standing walls, walnut rims, the logo on the felt.
         The guests (card 5) and winners (card 11) are Higgsfield stills of the same couple.
MOTION:  Every card is complete on its first frame. Only the action moves: the hand, the dice, the clock
         hands and sun, the folder, the coin, stamps, the camera flash, petals, and one foil sweep.
         No draw-on, no word-by-word text, no wipes. Cuts are hard, on the beat.
         Throws are simulated in build.py (gravity, bounces, wall rebound, rolling friction) and baked
         frame by frame as tl.set calls; the die shows one tumble-strip frame per film frame and settles
         continuously into its rest pose. Key hits land on beats: the wall hit on beat 2 of 6a and 6b,
         stamps (scale 1.7→1 in 0.2 s, power3.in) on beats 3–5, face changes in cards 7 and 8 on every
         beat, the jackpot burst on beat 2 of card 8.
         Nothing on screen stays still for more than 3 s (`dead_stretch` is clean).
SOUND:   Bundled Pixabay SFX only, on visible actions, placed by the same code that moves the picture
         (`sfx(card, time, file, volume)`): whoosh on throws, click on wall hits and landings, impact on
         stamps, pop on bubbles, a riser into the jackpot. Music comes from the person, added in the
         platform editor. Master at about −16 LUFS.
BANNED:  The defaults in the skill, plus: any building animation, freezes in the middle of a move,
         French or English copy, prices on the receipt, real photos of guests, the logo docked in a
         corner, the knife in card 7.
QA:      `lint` 0/0, `check --json` clean, `freezedetect` on the render, a frame sheet at the middle of
         every card, and a look at the tumbles frame by frame (no dropped strip frames).
```
