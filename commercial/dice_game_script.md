# Yoko Ono — "Lancez les dés" · Animated explainer script

**Format:** 9:16 (1080×1920), about 59 s, so it stays under the 60-second Shorts limit. 24 fps. Cuts follow a 96 BPM grid, the same as the Red Dragon spot (1 beat = 0.625 s, 1 bar = 2.5 s).
**Two uses, one master:**
- **In the restaurant:** the screen plays it muted, so the on-screen text carries every rule by itself. Supers are trilingual and stacked the same way as the posters: French, then English in italics, then Hebrew.
- **On social:** record one voiceover per language. French, English and Hebrew lines are given for every scene.

**Sources:**
- The restaurant's rules sheet (`Panneau_Regles_Jeu_Yoko_Ono.pdf`), in its own order. The wording matches the poster copy (`poster-dice-game/trilingual/copy.js` on the dice-poster branch).
- Three answers from the restaurant that aren't on the sheet:
  - If the throw isn't valid, the table rolls again.
  - The game is for happy hour, 16:00–18:00.
  - There's no minimum order.

## Look
It's the same campaign as the dice posters, so it uses the same "Noir élégant" system.
- **Colour:** black and ink (#000, #14110e), gold #c9a36b, light gold #e2c590 and ivory #f4ecdf. Red #b8322a is an accent only, for the red dice pips, the Jackpot ribbon and the seal.
- **The dice table (`reference/dice_table.jpg`):**
  - It's the restaurant's real table: a rectangular walnut frame with felt-lined inner walls and green casino felt.
  - The gold logo is printed on the felt near the far end.
  - The roller throws from the near short side toward the far short side, which is the opposite wall.
  - It's the only green in the film. Everything else stays black and gold, so the table pops whenever it appears.
- **The logo:** it's taken from the felt.
  - It's gold line art: an arch with cherry blossoms at the top and two mountain peaks behind a brush-style YOKO ONO wordmark.
  - ASIAN KITCHEN sits under the wordmark, with a bowl and chopsticks below and waves along the base.
  - It animates as a line drawing. The ink mountain from the Red Dragon ending resolves into the logo's mountains on the end card.
- **Type:**
  - Cormorant for French (caps) and English (italic).
  - Frank Ruhl Libre for Hebrew.
  - Diamond separators (◆) between languages.
  - Every super stays inside the Reels/TikTok safe area, keeping the top 250 px and bottom 400 px clear.
- **Motifs:**
  - A thin double gold frame around the screen.
  - A red 運 ("luck") hanko seal.
  - Vertical 運試し ("test of luck") down the right edge.
  - Sumi ink-brush wipes between scenes.
- **The dice:** Asian ivory dice where the 1 and 4 pips are red, as drawn by `shared/dice.js`. Double 4 shows red pips, which ties it to the seal and the ribbon. That's why the end card lands on it.
- **People:** simple gold line-art figures with no faces: guests, the roller and a waiter in a black apron. This keeps the look premium and lets any guest see themselves in it.

## Run of show
| # | Time | Beats | Scene |
|---|---|---|---|
| 1 | 0:00.0–0:02.5 | 0–4 | Hook |
| 2 | 0:02.5–0:06.3 | 4–10 | Title and logo |
| 3 | 0:06.3–0:13.8 | 10–22 | Happy hour, then ① The moment of truth |
| 4 | 0:13.8–0:17.5 | 22–28 | ② A unique chance |
| 5 | 0:17.5–0:21.3 | 28–34 | ③ A single player |
| 6 | 0:21.3–0:31.3 | 34–50 | ④ The perfect roll |
| 7 | 0:31.3–0:36.3 | 50–58 | Double 1 · 2 · 3: −50% |
| 8 | 0:36.3–0:41.3 | 58–66 | Double 4 · 5 · 6: Jackpot |
| 9 | 0:41.3–0:43.8 | 66–70 | No double |
| 10 | 0:43.8–0:47.5 | 70–76 | The service (tip) |
| 11 | 0:47.5–0:52.5 | 76–84 | Smile, you're on camera |
| 12 | 0:52.5–0:58.8 | 84–94 | End card |

---

## Script

### 1 · Hook (0:00.0–0:02.5)
**Picture:** Pure black. On beat 1, two ivory dice tumble toward camera out of the dark in slow motion. A red pip catches the light. On beat 3 they freeze mid-air, with gold dust hanging around them.
**Text:** none.
**VO:**
- FR: Un seul lancer… et votre addition peut disparaître.
- EN: One roll… and your bill could disappear.
- HE: הטלה אחת… והחשבון יכול להיעלם.

**Sound:** a taiko hit and a dice clack in a big reverb, then silence on the freeze.

### 2 · Title and logo (0:02.5–0:06.3)
**Picture:**
- The frozen dice drift apart, and the gold double frame draws itself around the screen.
- **Beats 4–7:** the logo draws itself in gold line:
  - The arch traces from bottom to top, and the blossoms pop open.
  - The mountain ridge draws across.
  - The YOKO ONO wordmark brushes in, then ASIAN KITCHEN.
  - The bowl puffs a curl of steam, and the waves ripple along the base.
- **Beats 8–10:** the title comes in under the logo, a round NOUVEAU badge spins in at −12° as on the poster, and the red 運 seal stamps in at the bottom.

**Text:**
- LE GRAND JEU ◆ *The grand game* ◆ המשחק הגדול
- **LANCEZ LES DÉS**
- *Roll the dice* ◆ הטילו את הקוביות
- Badge: NOUVEAU · *New* · חדש

**VO:**
- FR: Bienvenue au Grand Jeu de Yoko Ono.
- EN: Welcome to the Grand Game at Yoko Ono.
- HE: ברוכים הבאים למשחק הגדול של יוקו אונו.

**Sound:**
- A brush swish as the line draws.
- A wind-chime sparkle on the blossoms.
- A soft thud on the seal stamp.

### 3 · Happy hour, then ① The moment of truth (0:06.3–0:13.8)
**Picture:**
- **Beats 10–14:** a red sun, like the one on the poster photo, sinks along a gold clock arc from 16:00 to 18:00 over the ink mountains. It's golden hour.
- **Beats 14–22:**
  - An ink-brush wipe reveals a top-down view of a table at the end of a meal: four places, chopsticks resting on their rests, and the last of the soy sauce.
  - The plates clear away in stop-motion, one per beat.
  - On beat 20, the waiter's gold line-art hand slides a black bill folder to the centre, with the two dice sitting on top.

**Text:**
- HAPPY HOUR · 16h–18h · *4–6 PM* · 16:00–18:00
- ① LE MOMENT DE VÉRITÉ ◆ *The moment of truth* ◆ רגע האמת
- À la fin du repas · *At the end of the meal* · בסוף הארוחה

**VO:**
- FR: Venez pendant l'happy hour, de 16h à 18h. Le jeu se joue uniquement à la fin du repas, au moment de l'addition.
- EN: Come during happy hour, from 4 to 6 PM. The game is played only at the end of your meal, when the bill arrives.
- HE: בואו בהאפי האוור, בין ארבע לשש. משחקים רק בסוף הארוחה, כשמגיע החשבון.

**Sound:**
- A clock tick that slows down as the sun sets.
- Plate clinks on the beat.
- A soft leather pat as the folder lands.

### 4 · ② A unique chance (0:13.8–0:17.5)
**Picture:**
- Push in on the dice sitting on the bill folder.
- A large gold **×1** draws itself above them.
- A translucent second pair of dice tries to appear beside them, then dissolves like ink in water.

**Text:**
- ② UNE CHANCE UNIQUE ◆ *A unique chance* ◆ הזדמנות אחת
- Pour toute la table · *For the whole table* · לכל השולחן

**VO:**
- FR: Un seul et unique essai… pour toute la table.
- EN: One single attempt… for the entire table.
- HE: ניסיון אחד ויחיד — לכל השולחן.

**Sound:** a low koto pluck on the ×1, and a water-drip "bloop" as the ghost pair dissolves.

### 5 · ③ A single player (0:17.5–0:21.3)
**Picture:**
- Pull back to the four guests around the table, seen from above.
- A gold spotlight sweeps around the table like a roulette wheel, ticking on each beat. It slows down and stops on one guest.
- The others slide the dice over to that guest, and a gold ring settles around the chosen roller.

**Text:** ③ UN SEUL JOUEUR ◆ *A single player* ◆ שחקן אחד

**VO:**
- FR: Alors choisissez bien : une seule personne lance les dés, pour tout le monde.
- EN: So choose wisely: only one person rolls, for everyone.
- HE: אז תבחרו טוב: רק אחד מכם מטיל את הקוביות, בשביל כולם.

**Sound:** a roulette-style tick that slows down, then a rim click when the spotlight stops.

### 6 · ④ The perfect roll (0:21.3–0:31.3)
**Picture:** Ink wipe to the dice table, the first time the green felt appears.
- **The shot:** a low camera behind the roller's hand at the near end, looking down the felt past the gold logo. The far wall glows gold.
- **Beats 34–40, throw 1:**
  - One die hits the far wall, and the other stops short on the felt.
  - Freeze, with dotted trajectory lines and a red ✕.
  - Then a gold rewind sweep pulls both dice back into the roller's hand: roll again.
- **Beats 40–50, throw 2:**
  - Both dice hit the wall on two beats ("thock, thock") and bounce back onto the felt.
  - Their paths trace in gold, and a gold ✓ appears.

**Text:**
- ④ LE LANCER PARFAIT ◆ *The perfect roll* ◆ ההטלה המושלמת
- Wall label: PAROI D'EN FACE · *Opposite wall* · הקיר שממול
- After throw 1: ✕ NON VALIDÉ · *Not valid* · לא נחשב, then ON RELANCE ! · *Roll again!* · מטילים שוב!
- After throw 2: ✓

**VO:**
- FR: Pour que le résultat soit validé, les deux dés doivent rebondir sur la paroi d'en face. Sinon, on relance !
- EN: For the result to count, both dice must bounce off the opposite wall. If not, roll again!
- HE: כדי שהתוצאה תיחשב, שתי הקוביות חייבות לפגוע בקיר שממול ולקפוץ ממנו. אם לא — מטילים שוב!

**Sound:**
- Dice rolling on felt.
- A dull stop and a short buzz on the ✕.
- A tape-rewind whoosh.
- Two crisp wall hits, then a bright chime on the ✓.

*The re-roll is the restaurant's current house rule and isn't on the sheet. If it changes, cut the "Sinon, on relance" line and the rewind.*

### 7 · Double 1 · 2 · 3: −50% (0:31.3–0:36.3)
**Picture:**
- On the green felt, the dice from the valid throw spin in place like a slot machine, flashing one double per beat: double 1 (red pips), double 2, double 3.
- Cut to the bill folder opening.
- A gold yanagiba sushi knife slices the receipt clean down the middle, and one half falls away.
- **−50%** rises up in light gold.

The receipt shows no prices, so it works in any currency.
**Text:**
- DOUBLE 1 · 2 · 3
- **−50%**
- Sur toute l'addition de la table · *On the whole table's bill* · על כל החשבון של השולחן

**VO:**
- FR: Double 1, double 2 ou double 3 ? 50 % de remise sur toute l'addition de la table.
- EN: Double one, two or three? Fifty percent off the whole table's bill.
- HE: דאבל 1, 2 או 3? 50% הנחה על כל החשבון של השולחן.

**Sound:** a slot-machine tick on each double, then the knife swish and a paper slice.

### 8 · Double 4 · 5 · 6: Jackpot (0:36.3–0:41.3)
**Picture:**
- On the felt, the dice flash double 6, then double 5.
- They land on **double 4**, with red pips on both dice, right under the gold logo.
- Hard cut to full gold. The red ribbon swings in, and the whole receipt bursts into gold leaf and cherry-blossom petals, the same blossoms as in the logo.
- **100%** fills the screen, and the guests' line-art figures jump up.

**Text:**
- Ribbon: JACKPOT ! · ג'קפוט!
- DOUBLE 4 · 5 · 6
- **100%**
- OFFERT · *On the house* · עלינו

**VO:**
- FR: Double 4, 5 ou 6 ? C'est le jackpot ! Tout le repas vous est offert par la maison.
- EN: Double four, five or six? Jackpot! Your entire meal is on the house.
- HE: דאבל 4, 5 או 6? ג'קפוט! כל הארוחה על חשבון הבית.

**Sound:** a gong and a taiko roll. The music hits its peak here.

### 9 · No double (0:41.3–0:43.8)
**Picture:**
- A calm reset to black and gold.
- The dice land on 3 and 5, so no double. The bill folder closes softly.
- A guest leans back, satisfied, with steam rising from a tea cup.

**Text:** Pas de double ? · *No double?* · לא יצא דאבל?

**VO:**
- FR: Pas de double ? Juste un excellent dîner.
- EN: No double? Just a great dinner.
- HE: לא יצא דאבל? נשארתם עם ארוחה מעולה.

**Sound:** the music drops to a single koto phrase.

### 10 · The service (0:43.8–0:47.5)
**Picture:**
- Back at the jackpot table, the waiter figure gives a small bow.
- A gold coin drops into a little tip tray.

This shows that even a free meal still leaves the tip.
**Text:** LE SERVICE · Pourboire non inclus · *Tip not included* · הטיפ לא כלול

**VO:**
- FR: Seul le pourboire n'est pas inclus : il reste pour votre serveur.
- EN: Only the tip isn't included. That stays with your waiter.
- HE: רק הטיפ לא כלול: הוא נשאר לצוות, כהוקרה על השירות.

**Sound:** a coin "ching" and a warm chord.

### 11 · Smile, you're on camera (0:47.5–0:52.5)
**Picture:**
- A phone-camera overlay (REC dot, 9:16 frame) closes in on the cheering winners at the dice table.
- The image freezes into a social post card, with a few gold hearts floating up.

Later, real winner clips filmed at the table replace this shot. That's what this rule is for.
**Text:** SOURIEZ, VOUS ÊTES FILMÉS ! ◆ *Smile, you're on camera!* ◆ חייכו, אתם מצולמים!

**VO:**
- FR: Et si vous gagnez… souriez, vous êtes filmés ! On partage votre moment sur nos réseaux.
- EN: And if you win… smile, you're on camera! We'll share your moment on our socials.
- HE: ואם זכיתם… חייכו, אתם מצולמים! את הרגע שלכם נשתף ברשתות שלנו.

**Sound:** a camera shutter and crowd cheers mixed low under the music.

### 12 · End card (0:52.5–0:58.8)
**Picture:**
- The ink-mountain painting rises behind black. Its ridge redraws itself as the mountain line of the logo.
- The dice tumble across one last time and land on double 4, with the red pips, under the logo.
- The gold frame and the red seal come in.
- The last taiko hit lands on beat 1 of the final bar, the seal stamp lands on the last beat, then fade out.

**Text:**
- The logo
- **LANCEZ LES DÉS**
- *Roll the dice* ◆ הטילו את הקוביות
- HAPPY HOUR · 16h–18h · *4–6 PM* · 16:00–18:00
- RÉSERVEZ VOTRE TABLE · *Book your table* · הזמינו שולחן

**VO:**
- FR: Yoko Ono. Happy hour, de 16h à 18h. Lancez les dés.
- EN: Yoko Ono. Happy hour, 4 to 6. Roll the dice.
- HE: יוקו אונו. האפי האוור, בין ארבע לשש. הטילו את הקוביות.

---

## Sound and voice
- **Score:** taiko and rim at 96 BPM, as in the Red Dragon spot, with koto/shamisen accents. It builds through scenes 6–8, rests on scene 9 and resolves on the end card.
- **Foley:** dice on felt, wall hits, plate clinks, paper slice, coin, gong.
- **Mix:** loudness-normalized to about −14 LUFS for social.
- **Voice:** a warm, confident host with a smile and a little suspense. Think of a classy casino croupier, not a carnival barker. Use a native speaker for each language.

## 15-second cutdown (Stories and the restaurant screen)
| Time | Content |
|---|---|
| 0:00–0:02.5 | Scene 1, the hook |
| 0:02.5–0:05.0 | Throw 2 from scene 6 only: both dice bounce off the wall, ✓ |
| 0:05.0–0:08.75 | Scene 7: −50% |
| 0:08.75–0:12.5 | Scene 8: Jackpot, 100% |
| 0:12.5–0:15.0 | End card, with HAPPY HOUR 16h–18h and "Règles au restaurant · *Rules in the restaurant* · החוקים במסעדה" |

## Still open
1. **The dice:** the video uses ivory Asian dice with red 1 and 4 pips, as on the posters. If the dice on the table look different, the animation should match them.
2. **A clean logo file:** the felt photo works as a reference, but the final render needs a sharp vector. It can be traced from the photo, or the original file can come from whoever printed the felt.
