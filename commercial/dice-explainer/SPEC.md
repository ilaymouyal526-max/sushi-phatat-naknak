# SPEC: Yoko Ono, "Lancez les dés" (animated explainer)

Built from `../dice_game_script.md`. The script owns the words; this file owns the numbers.

```text
GOAL:    A guest who sees it knows exactly how to play: happy hour 16-18, end of meal, one roller,
         one valid throw off the far wall, double 1-3 = -50%, double 4-6 = free, tip still due.
OUTPUT:  HyperFrames, 1080 x 1920, 24 fps. Master with music+SFX (no VO), a silent copy, a 15 s cutdown.
TIME:    58.75 s x 24 = 1410 frames. 96 BPM: 1 beat = 15 frames = 0.625 s, 1 bar = 60 frames.
         Beat n starts at frame 15n. Scene changes land on beats (table in the script).
LOOK:    Ground: warm black #0b0907, 3% luma grain. Never an empty void: every shot has a hero
           filling >= 40% of the frame (dice, table, bill folder, the logo) or full-bleed felt.
         Gold #c9a36b: structure lines, the double frame, labels, the logo line.
         Light gold #e2c590: the English line and one highlighted word per shot.
         Ivory #f4ecdf: French display words and numbers.
         Red, only in four places: dice body #c8102e (translucent: a #c8102e cast at 35% on the felt
           under each die, no glow), the Jackpot ribbon #b8322a, the 運 seal #b8322a, and the ✕.
         Felt #1a6b3c with a radial falloff to #0f4526 at the edges; walnut rim #7a4b2a,
           top face #9a6539, inner felt walls #145a32.
         Frame: the posters' double gold rule, 1.5 px at 24 px inset + 0.75 px at 31 px, 50% alpha.
           It's the brand's own poster device, drawn once and held still.
         Type:
           FR: Cormorant 600, caps, +6% tracking. Title 120 px, rule heading 64 px, line 44 px.
           EN: Cormorant italic 600 at 0.62x the FR size, min 36 px.
           HE: Frank Ruhl 500 at 0.6x the FR size, min 36 px, dir=rtl.
           Big numbers (-50%, 100%, x1): Cormorant 700, 300-360 px.
           No reading text under 36 px.
         Safe area: every readable word sits between y=168 and y=1330, with x margins of 108 px
           (864 px line width). Below y=1330 only felt, dice, logo or decoration.
OBJECTS: Red dice: rounded cubes 1:1, white pips, sharp highlight on the top-left edge,
           translucent body (inner face 70% opacity, back faces faintly visible).
         The dice table: a rectangular tray seen from the roller's end, walnut rim, felt walls,
           the gold logo printed on the felt 60% of the way to the far wall.
         The far ("opposite") wall: the short side opposite the camera, gold-lit when named.
         The bill folder: black leather, 420 x 300 px, gold edge line, receipt inside with ruled
           lines and no prices.
         The logo: gold line art (arch, blossoms on two branches, twin peaks, YOKO ONO wordmark,
           ASIAN KITCHEN, bowl with chopsticks, three waves), stroke 4 px, drawn on by stroke-dashoffset.
         Guests and waiter: gold line figures, 4 px stroke, no faces, waiter with an apron line.
MOTION:  Enter: expo.out, 12-16 frames. Exit: power2.in, 5-6 frames (40-50% of the entrance).
         Camera and colour floods: power2.inOut, 10-14 frames. Spins: linear.
         Landings with a bounce (x1, badge, numbers): back.out(1.4). Never on opacity or colour.
         Title entrance: per word, blur 6 px -> 0 and opacity 0 -> 1 in 3 frames, 2 frames apart.
           The EN line follows 3 frames after the FR line ends, and the HE line 3 frames after that.
         Holds: 0.5 s + 0.3 s a word. A landed title doesn't move.
         Dice throw: the arc is a quadratic path, spin linear at 2.5 turns/s, the face swaps every
           2 frames while airborne. A wall hit is 1 frame of 8% squash, then the dice come back
           out on expo.out.
         Transitions (each with a cause on screen):
           Whip: the dice fly out of frame (1 -> 2).
           Ink wipe: a sumi brush stroke crosses the frame in 12 frames (2 -> 3 and 5 -> 6).
           Object becomes the world: the bill folder opens to fill the frame (3/4 -> 7).
           Colour flood: the ground goes gold in 10 frames (8).
           Dip cut (9, 12).
SHOTS:   1  f0-60      Hook. Frame 0 is already the hook: two dice at 380 px, mid-tumble, plus
                       "UN SEUL LANCER / One roll / הטלה אחת". The dice tumble 1 bar, freeze on
                       beat 3, then whip out.
         2  f60-150    The frame draws (12 f). The logo draws (f60-105). The title lands on f105.
                       The NOUVEAU badge comes in on f120, the seal stamps on f135.
         3  f150-330   A red sun sinks along a gold arc labelled 16h -> 18h (f150-210) with
                       HAPPY HOUR. Ink wipe on f210, to a top-down dining table: plates clear on
                       beats, and the folder with the dice lands on f300. Rule ① text.
         4  f330-420   Push in on the dice on the folder. x1 lands on f345, the ghost pair
                       dissolves f375-405. Rule ②.
         5  f420-510   Four guest figures round the table. A spotlight steps once per beat and
                       stops on beat 32 (f480). Rule ③.
         6  f510-750   Ink wipe to the felt (roller's view). Throw 1 f525-600: one die short, a
                       freeze with ✕ NON VALIDÉ, then ON RELANCE ! and a rewind. Throw 2 f600-690:
                       two wall hits on beats 42 and 43 (f630, f645), back onto the felt, ✓ on f675.
                       Rule ④ and the wall label.
         7  f750-870   The dice slot through doubles 1, 2, 3 on beats. The folder opens, a gold
                       knife slices on f825, -50% lands.
         8  f870-990   Doubles 4, 5, then double 6 on the logo (f915). Gold flood, ribbon,
                       100% / OFFERT, the figures jump.
         9  f990-1050  Dip to black: the dice land on 3 + 5, the folder closes. "Pas de double ?"
         10 f1050-1140 The waiter bows, a coin drops into the tray on f1095. LE SERVICE line.
         11 f1140-1260 Phone REC frame over the winners, freeze into a post card on f1215.
                       SOURIEZ line.
         12 f1260-1410 Ink mountain -> logo mountains. The dice land on double 6 (f1305),
                       title, HAPPY HOUR, CTA. Final taiko hit on f1350, seal on f1395, hold.
BANNED:  The defaults in references/spec.md, plus:
         - glow, bloom or light rays on the dice (translucency is a cast shadow, not a glow);
         - gold dust or particles as decoration (blossom petals only in 8, from the receipt);
         - all three language lines arriving at once;
         - any text moving while it's read;
         - slide-up fades;
         - the logo docked in a corner;
         - currency or prices on the receipt;
         - real faces.
QA:      f0 (hook readable), f100 (logo half drawn), f140, f200, f320, f400, f480, f590 (✕),
         f640 (wall hit), f690 (✓), f840 (-50%), f930 (jackpot), f1020, f1100, f1230, f1400.
         Each frame: every word inside y 168-1330, Hebrew reads right to left, nothing cut off,
         and the hero fills >= 40% of the frame.
```
