# SPEC: Yoko Ono, "הטילו את הקוביות" (v5, Hebrew)

The storyboard and words live in `../dice_game_script.md` and in `build.py`. This file holds the numbers and the rules.

```text
GOAL:    A guest knows exactly how to play: happy hour 16:00–18:00, end of the meal, one roller, one valid
         throw off the far wall (a miss is re-rolled), double 1–3 = −50%, double 4–6 = the meal is on us,
         tip not included, winners filmed. Everything is subject to the house rules, which the waiter has.
OUTPUT:  HyperFrames, 1080 x 1920, 24 fps. A Reels master with SFX (no VO), a silent loop for the
         restaurant screen, and a 15 s cutdown.
TIME:    68.125 s = 1635 frames. 96 BPM: 1 beat = 15 frames = 0.625 s. A 9.375 s opening, then 14 cards
         (58.75 s), each cut on a beat.
OPENING: Three Higgsfield clips (Kling std, from gpt_image_2_5 stills, Pixar-realistic). P1, 0–3.125 s:
         the couple asks for the bill. P2, 3.125–6.875 s: the chef: "לא, לא, לא… קודם מטילים את הקוביות!".
         P3, 6.875–8.125 s: the couple is surprised. Then 8.125–9.375 s: the felt close-up in code.
         The Hebrew speech bubbles are overlays. There is no frame or footer during the opening.
LANGUAGE: Hebrew only, RTL. Times and percentages sit in LTR isolates.
LOOK:    Noir & Or poster cards. Ground #0b0907 with a warm radial #24160e, the double gold rule (static),
         and grain at 13% overlay, stepped 12x a second.
         Gold #c9a36b. Gold foil text: a gradient #a8814a→#fff1c9, swept once per card.
         Ivory #f4ecdf. Red #b8322a (seal, ribbon, stamps).
         Dice: translucent red acrylic (#ff2a45, attenuation #c4001e) with flush white pips, rendered in 3D.
         Felt #1a6b3c and walnut #9a6539 on the dice-table cards. Card 8 is a full gold ground.
         Type: Frank Ruhl Libre 800 headlines at 96–150 px, Frank Ruhl 500 sublines at 50–64 px in light
         gold, Heebo for the small type and the house-rules note (28 px footer; 34 px on the end card).
         Text band: every readable line sits within y 200–1330, except the fixed footer note.
OBJECTS: Realistic 3D renders (tools/props.html → assets/img): Vegas dice in translucent red acrylic with
         white pips (6 faces + 12 tumbling poses). The thrower's hand in three poses (fist → release → open),
         with a navy blazer sleeve, a white cuff and a gold cufflink, like the man in the opening.
         The gold dress-watch dial with a sunset aperture.
         The walnut dining table, the bill folder, and the dice table in perspective with the logo on the felt.
         The receipt with no prices, the yanagiba knife, the tip tray with coins, a phone with REC,
         the paper receipt and the gold coin as renders,
         and the guests (card 5) and winners (card 11) as Higgsfield stills of the same couple.
MOTION:  Every card is complete on its first frame. Only the action moves: the hand, the dice, the clock
         hands and sun, the folder, the knife, the coin, the camera flash, the petals, and one foil sweep.
         No draw-on, no word-by-word text, no wipes.
         Throws: hand rise power3.out 0.4 s, release on the beat, dice tumble faces every 1/12 s,
         landing expo.out. Stamps (✕, ✓) land at scale 1.7→1 in 0.2 s, power3.in.
         Nothing on screen stays still for more than 3 s (`dead_stretch` is clean).
         Cuts are hard, on the beat.
SOUND:   Bundled Pixabay SFX only, on visible actions: whoosh on throws, click on wall hits and landings,
         impact on stamps, pop on face changes, a riser into the jackpot. Music comes from the person,
         added in the platform editor.
BANNED:  The defaults in the skill, plus: any building animation, freezes in the middle of a move,
         French or English copy, prices on the receipt, real photos of guests, and the logo docked in a corner.
QA:      `check --json` clean (film_silent aside if no music), `freezedetect` on the render, and a frame
         sheet at the middle of every card.
```
