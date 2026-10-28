# Yoko Ono — "Lancez les dés" · Animated explainer script

**Format:** 9:16 (1080×1920), about 52 s, 24 fps. Cuts follow a 96 BPM grid, the same as the Red Dragon spot (1 beat = 0.625 s, 1 bar = 2.5 s).
**Two uses, one master:**
- **In the restaurant:** the screen plays it muted, so the on-screen text carries every rule by itself. Supers are trilingual and stacked the same way as the posters: French, then English in italics, then Hebrew.
- **On social:** record one voiceover per language. French, English and Hebrew lines are given for every scene.

**Source:** the restaurant's rules sheet (`Panneau_Regles_Jeu_Yoko_Ono.pdf`), in its own order. The wording matches the poster copy (`poster-dice-game/trilingual/copy.js` on the dice-poster branch). Nothing here goes beyond what the sheet says.

## Look
It's the same campaign as the dice posters, so it uses the same "Noir élégant" system.
- **Colour:** black and ink (#000, #14110e), gold #c9a36b, light gold #e2c590 and ivory #f4ecdf. Red #b8322a is an accent only, for the red dice pips, the Jackpot ribbon and the seal.
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
  - The ink-mountain painting from the Red Dragon ending, reused faintly on the end card.
- **The dice:** Asian ivory dice where the 1 and 4 pips are red, as drawn by `shared/dice.js`. Double 4 shows red pips, which ties it to the seal and the ribbon. That's why the end card lands on it.
- **People:** simple gold line-art figures with no faces: guests, the roller and a waiter in a black apron. This keeps the look premium and lets any guest see themselves in it.
- **The table:** the restaurant's dice table with its padded opposite wall. Until Natan's photo arrives, it's drawn as a dark wood tray with a back wall. See open questions.

## Run of show
| # | Time | Beats | Scene |
|---|---|---|---|
| 1 | 0:00.0–0:02.5 | 0–4 | Hook |
| 2 | 0:02.5–0:05.0 | 4–8 | Title |
| 3 | 0:05.0–0:10.0 | 8–16 | ① The moment of truth |
| 4 | 0:10.0–0:13.8 | 16–22 | ② A unique chance |
| 5 | 0:13.8–0:17.5 | 22–28 | ③ A single player |
| 6 | 0:17.5–0:25.0 | 28–40 | ④ The perfect roll |
| 7 | 0:25.0–0:30.0 | 40–48 | Double 1 · 2 · 3: −50% |
| 8 | 0:30.0–0:35.0 | 48–56 | Double 4 · 5 · 6: Jackpot |
| 9 | 0:35.0–0:37.5 | 56–60 | No double |
| 10 | 0:37.5–0:41.3 | 60–66 | The service (tip) |
| 11 | 0:41.3–0:46.3 | 66–74 | Smile, you're on camera |
| 12 | 0:46.3–0:52.5 | 74–84 | End card |

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

### 2 · Title (0:02.5–0:05.0)
**Picture:**
- The frozen dice drift apart.
- The gold double frame draws itself around the screen in two clockwise strokes.
- YOKO ONO / ASIAN KITCHEN fades in at the top, and 運試し brushes in down the right edge.
- A round NOUVEAU badge spins in at −12°, as on the poster.
- The red 運 seal stamps in at the bottom.

**Text:**
- LE GRAND JEU ◆ *The grand game* ◆ המשחק הגדול
- **LANCEZ LES DÉS**
- *Roll the dice* ◆ הטילו את הקוביות
- Badge: NOUVEAU · *New* · חדש

**VO:**
- FR: Bienvenue au Grand Jeu de Yoko Ono.
- EN: Welcome to the Grand Game at Yoko Ono.
- HE: ברוכים הבאים למשחק הגדול של יוקו אונו.

**Sound:** a brush swish as the frame draws, and a soft thud on the seal stamp.

### 3 · ① The moment of truth (0:05.0–0:10.0)
**Picture:**
- An ink-brush wipe reveals a top-down view of a table at the end of a meal: four places, chopsticks resting on their rests, and the last of the soy sauce.
- The plates clear away in stop-motion, one per beat.
- On beat 13, the waiter's gold line-art hand slides a black bill folder to the centre, with the two dice sitting on top.

**Text:**
- ① LE MOMENT DE VÉRITÉ ◆ *The moment of truth* ◆ רגע האמת
- À la fin du repas · *At the end of the meal* · בסוף הארוחה

**VO:**
- FR: Le jeu se joue uniquement à la fin du repas, au moment de l'addition.
- EN: It's played only at the end of your meal, when the bill arrives.
- HE: משחקים רק בסוף הארוחה, כשמגיע החשבון.

**Sound:** plate clinks on the beat, then a soft leather pat as the folder lands.

### 4 · ② A unique chance (0:10.0–0:13.8)
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

### 5 · ③ A single player (0:13.8–0:17.5)
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

### 6 · ④ The perfect roll (0:17.5–0:25.0)
**Picture:** The screen splits into two panels stacked top and bottom. Both show a side view of the dice table, with the roller's hand at the near end and the opposite wall glowing gold at the far end.
- **Top panel:** one die hits the wall and the other stops short. Freeze, with dotted trajectory lines and a red ✕.
- **Bottom panel:** both dice fly, hit the wall on two beats ("thock, thock") and bounce back. Their paths trace in gold, and a gold ✓ appears.

Showing the two cases side by side keeps it clear that this is an example, not a second try.

**Text:**
- ④ LE LANCER PARFAIT ◆ *The perfect roll* ◆ ההטלה המושלמת
- Wall label: PAROI D'EN FACE · *Opposite wall* · הקיר שממול
- Top panel: ✕ NON VALIDÉ · *Not valid* · לא נחשב
- Bottom panel: ✓

**VO:**
- FR: Pour que le résultat soit validé, les deux dés doivent rebondir sur la paroi d'en face. Les deux !
- EN: For the result to count, both dice must bounce off the opposite wall. Both of them!
- HE: כדי שהתוצאה תיחשב, שתי הקוביות חייבות לפגוע בקיר שממול ולקפוץ ממנו. שתיהן!

**Sound:**
- Dice rolling on wood.
- A dull stop and a short buzz on the ✕.
- Two crisp wall hits, then a bright chime on the ✓.

### 7 · Double 1 · 2 · 3: −50% (0:25.0–0:30.0)
**Picture:**
- The dice from the valid roll spin in place like a slot machine, flashing one double per beat: double 1 (red pips), double 2, double 3.
- The bill folder opens.
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

### 8 · Double 4 · 5 · 6: Jackpot (0:30.0–0:35.0)
**Picture:**
- The dice flash double 6, then double 5.
- They land on **double 4**, with red pips on both dice.
- Hard cut to full gold. The red ribbon swings in, and the whole receipt bursts into gold leaf and cherry-blossom petals.
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

### 9 · No double (0:35.0–0:37.5)
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

### 10 · The service (0:37.5–0:41.3)
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

### 11 · Smile, you're on camera (0:41.3–0:46.3)
**Picture:**
- A phone-camera overlay (REC dot, 9:16 frame) closes in on the cheering winners.
- The image freezes into a social post card, with a few gold hearts floating up.

Later, real winner clips filmed in the restaurant replace this shot. That's what this rule is for.
**Text:** SOURIEZ, VOUS ÊTES FILMÉS ! ◆ *Smile, you're on camera!* ◆ חייכו, אתם מצולמים!

**VO:**
- FR: Et si vous gagnez… souriez, vous êtes filmés ! On partage votre moment sur nos réseaux.
- EN: And if you win… smile, you're on camera! We'll share your moment on our socials.
- HE: ואם זכיתם… חייכו, אתם מצולמים! את הרגע שלכם נשתף ברשתות שלנו.

**Sound:** a camera shutter and crowd cheers mixed low under the music.

### 12 · End card (0:46.3–0:52.5)
**Picture:**
- The dice tumble across black one last time and land on double 4, centred, with the red pips.
- The gold frame, logo and red seal come in.
- The ink-mountain painting rises faintly behind them, as a callback to the Red Dragon ending.
- The last taiko hit lands on beat 1 of the final bar, the seal stamp lands on the last beat, then fade out.

**Text:**
- YOKO ONO · ASIAN KITCHEN
- **LANCEZ LES DÉS**
- *Roll the dice* ◆ הטילו את הקוביות
- À la fin de votre repas · *At the end of your meal* · בסוף הארוחה
- RÉSERVEZ VOTRE TABLE · *Book your table* · הזמינו שולחן

**VO:**
- FR: Yoko Ono. Lancez les dés.
- EN: Yoko Ono. Roll the dice.
- HE: יוקו אונו. הטילו את הקוביות.

---

## Sound and voice
- **Score:** taiko and rim at 96 BPM, as in the Red Dragon spot, with koto/shamisen accents. It builds through scenes 6–8, rests on scene 9 and resolves on the end card.
- **Foley:** dice on wood, wall hits, plate clinks, paper slice, coin, gong.
- **Mix:** loudness-normalized to about −14 LUFS for social.
- **Voice:** a warm, confident host with a smile and a little suspense. Think of a classy casino croupier, not a carnival barker. Use a native speaker for each language.

## 15-second cutdown (Stories and the restaurant screen)
| Time | Content |
|---|---|
| 0:00–0:02.5 | Scene 1, the hook |
| 0:02.5–0:05.0 | The bottom panel of scene 6 only: both dice bounce off the wall, ✓ |
| 0:05.0–0:08.75 | Scene 7: −50% |
| 0:08.75–0:12.5 | Scene 8: Jackpot, 100% |
| 0:12.5–0:15.0 | End card, with "Règles au restaurant · *Rules in the restaurant* · החוקים במסעדה" in place of the "at the end of your meal" line |

## Open questions before production
1. **Invalid roll:** if the two dice don't both hit the wall, does the table roll again or lose its one try? The sheet doesn't say, so the script only shows "not valid". Once the restaurant answers, a line can be added to scene 6.
2. **The betting table photo** (from Natan): scene 6 should match the real table and its wall.
3. **The logo file:** scenes 2 and 12 use a text stand-in until it arrives, same as the posters.
4. **Conditions:** the sheet sets no minimum order, visit limit or dine-in rule, so the video doesn't mention any. If there are conditions, they should go into scene 3 or the end card.
5. **Voiceover languages:** which ones to record first.
