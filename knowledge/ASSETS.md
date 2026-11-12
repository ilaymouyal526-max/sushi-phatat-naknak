# Yoko Ono: everything we have, and where it is

Built 2026-11-12 by going through every item. Update this file whenever something new is made, found or approved.

- **Codes** (Y001, R145, V083, C005) point to Google Drive files. `drive-inventory.json` maps each code to its Drive id.
- **Get a file** (free): `python3 knowledge/tools/drive_get.py OUT_DIR Y421 R145`. Search titles with `--find tataki`.
- **See them**: `drive-sheets/*.jpg` are labelled contact sheets (Y_01 to Y_09, R_01 to R_04, V_01 to V_03, C_01). Open one with Read before choosing a photo.

## 1. The restaurant (facts to reuse)
- **Name:** YOKO ONO, Asian Kitchen. **Address:** Achuza 124, Ra'anana (אחוזה 124, רעננה).
- **Kitchen:** sushi bar plus a hot Asian kitchen (wok noodles, General Tao, pad kapao, tonkatsu, bao, gyoza).
- **Look of the place:** red torii-style entrance with a "YOKO ONO" sign, a ceiling of paper umbrellas, a big blue dragon disc lit over the bar, pink blossom garlands, gold curtains, lounge booths with mustard cushions, a gong, live keyboard music nights.
- **Logo:** an oval badge with blossoms, mountains, a sun and a bowl with chopsticks over waves, with "YOKO ONO / ASIAN KITCHEN".
  - Files: R145 (gold on white, 3543 px), R144 (black line), R161 and R162 (gold on the navy wall), R031 and R032 (gold sign on a dark wall).
  - Vector trace: `shared/logo-path.js` on branch `ccr-501b2ecd-itqixr`.
  - Second brand: "YOKO ONO MUSIC LIVE" (R121, R143).
- **House style (approved for the dice video, a good default):** Noir & Or. Black #0b0907, gold #c9a36b, ivory #f4ecdf, red #b8322a. Frank Ruhl Libre for headings, Heebo for small text, Cormorant for Latin.
- **Dice game (happy hour):**
  - When: 16:00 to 18:00, at the end of the meal, no minimum order.
  - How: one roll per table, by one player. Both dice must hit the far wall.
  - Prizes: a double 1 to 3 gives 50% off the whole bill; a double 4 to 6 makes the meal free.
  - Not covered: the tip. Winners are photographed for social media.
  - Small print: "בכפוף לתקנון" (subject to the rules).
- **Known prices** (from `MENU_FINAL_HEBSP.pdf`, quoted in `menu-screen/index.html` on `ccr-53cee3cd-iiiipd`; the PDF itself is not in the repo or the Drive):
  - Gyoza: chicken 55 ₪, beef 59 ₪.
  - Caramel tempura chicken: 72 ₪.
  - House wok noodles: chicken 69 ₪, tempura 72 ₪, veggie 59 ₪.
- **Unknowns to ask before using them anywhere:**
  - prices and the real current menu text;
  - opening hours and phone number;
  - the Instagram handle (the dice video still shows `@[instagram]`);
  - the website domain.

## 2. Where everything lives
| Place | What | How to reach it |
|---|---|---|
| Google Drive "YOKO ONO" (shared with us, view only) | Pro photo shoot, phone photos, AI art, videos, print files | folder `1G1eDXuQpZ62a47NQ8YHMGDtQktJ-dtNH`; MCP `Google_Drive` tools; downloads with `drive_get.py` |
| Drive "יוקומגשים" | 26 photos of the party and promo trays | folder `1cSZOyKrjwz6Hr_DsOEEAORMPpnTDLzZq` |
| Higgsfield | 192 generations (`media/higgsfield/`, prompts in `generations.json`) plus 92 uploaded reference images | MCP `Higgsfield` (`show_generations`, `show_medias`) |
| This repo | Code and outputs of every project, one branch each (section 5) | `git show origin/<branch>:<path>` |
| `media/` on this branch | A copy of every media file from every branch plus all Higgsfield output | `media/README.md` |
| Gallery artifact | Browse all of the above | https://claude.ai/artifact/ETVgwKNXjN3YCS5fpauvMe |

## 3. Drive photo catalog
### images_yoko: the professional shoot (426 photos, Sony A7 IV, 2024-09-30, edited, 2.3 to 6 K)
Two backgrounds: grey concrete, and rusty dark copper. Most dishes come in several angles. These are the **best references for Higgsfield** and the right photos for the screen and the website.

**Sushi and raw**
| Dish | Codes |
|---|---|
| Nigiri saumon | Y001, Y347 to Y351 (Y347-351: chef pouring sauce, dark) |
| Nigiri thon | Y002, Y025, Y041, Y352 (bottle pour) |
| Sashimi thon | Y003, Y026, Y057, Y406 to Y409 |
| Sashimi 3 poissons / royal | Y395 to Y402, Y143 to Y147 |
| Waiter holding a sashimi platter | Y130 to Y133 |
| Maki saumon / thon mayo / thon rouge / végétarien | Y339 to Y343 |
| California (saumon avocat, spicy saumon batata, spicy tuna, thon avocat, thon mayo avocat) | Y308 to Y312 |
| Caviar roll / Salmon caviar roll | Y313 / Y393, Y394 |
| Crazy roll (rainbow) | Y324 to Y326 |
| Maguro roll / Spécial maguro | Y337, Y338 / Y415 |
| Spicy tuna roll | Y410 to Y413 |
| Tataki salmon roll | Y416 |
| Panko roll | Y358, Y359 |
| Veggie roll and avocado maki | Y422, Y249 to Y256 |
| Volcano | Y423, Y424 |
| White fish tempura (roll, spécial) | Y414, Y425, Y426 |
| Green dragon-style roll (avocado on top) | Y114, Y115, Y109, Y110 (dipped, sauce splash) |
| Crispy rice salmon / thon rouge | Y327, Y328 / Y329 to Y332 |
| Chirashi royal / saumon | Y314 to Y320 / Y321 to Y323 |
| Riz tartare saumon | Y378 to Y380; crispy salmon tartare on green plate Y111, Y112 |
| Tataki saumon | Y417 to Y420 (Y419, Y420 with an ikura spoon) |
| Tataki thon (in orange sauce) | Y038, Y044, Y058, Y066, Y068, Y421 |
| Salade sashimi / poke bowl | Y384 to Y391, Y100 to Y104, Y403 to Y405 (black sesame pour) |
| Ikura on crispy rice | Y096 to Y098 |
| Party sushi trays (boxes) | Y303 to Y306, Y099 |
| Sushi-making flat lay (mat, knife, rice) | Y262 to Y265 |

**Hot kitchen**
| Dish | Codes |
|---|---|
| Gyoza (plate / bamboo steamer) | Y017, Y032, Y049, Y062, Y073, Y078 / Y334 to Y336, Y106, Y107 |
| Chicken lemon | Y005, Y006, Y028 |
| General Tao | Y016, Y031, Y048, Y061, Y072 |
| Bœuf caramélisé | Y013, Y023 |
| Pad kapao (with fried egg) | Y018, Y035, Y052, Y064 |
| Tonkatsu | Y021, Y039, Y054, Y067, Y075 |
| Poisson du jour / White fish | Y019, Y036, Y043, Y070, Y076, Y079 / Y022 |
| Darne saumon | Y015, Y024, Y030, Y040, Y047, Y055, Y069, Y082 |
| Yakitori saumon | Y004, Y027, Y045, Y059, Y071, Y077 |
| Shrimp crispy coco | Y020, Y037, Y053, Y065, Y074 |
| Crispy chicken bao / Assado bao / bao and nems | Y014, Y029, Y046, Y060 / Y307 / Y007 |
| Nems chicken | Y009 |
| Curry poulet | Y008 |
| Noodles chicken / meat / curry / mixte / tofu / green-curry tofu | Y010, Y011, Y033, Y050 / Y012, Y034, Y051, Y063 / Y042, Y056, Y354 / Y355, Y356 / Y357, Y246, Y247 / Y353 |
| Salads (asian poulet, saumon, soja poulet, chicken) | Y381 to Y383, Y392, Y241 to Y243, Y248, Y259 to Y261 |
| Edamame | Y108, Y333 |
| Table spreads, top-down | Y083, Y084, Y270, Y273, Y274, Y288 |
| People eating at the round table (top-down) | Y289 to Y298 |

**Desserts and drinks**
| What | Codes |
|---|---|
| Mochi | Y090, Y344 to Y346 |
| White ice-cream balls with red berries | Y085, Y086, Y091 to Y093 |
| Chocolate dome with caramel | Y087, Y088, Y094, Y095 |
| Lava cake with ice cream | Y089 |
| Signature cocktail (amber coupe, lime wheel, smoke) | Y203 to Y214; bartender shaking Y193 to Y202 |
| Other cocktails | Y080 (white coupe), Y142 (pink, foam), Y081 (tiki mug) |
| Bottles on grey backdrop (Coke, Sprite, Leo, Fanta, Perrier, waters, juices, Fuze Tea, Panna, San Pellegrino, rosé, Heineken, Arizona, red wine) | Y116 to Y141 |
| Wine in ice buckets / bar bottles | Y187 to Y190, Y365 / Y163, Y164, Y182 to Y186 |

**Craft (good for ads and the "made by hand" story)**
| What | Codes |
|---|---|
| Washing sushi rice by hand | Y148 to Y158 |
| Rice in cloth, seasoning in the hangiri, chef in steam | Y215 to Y240 |
| Chef and team portraits | Y299 (two chefs), Y239, Y240 |
| Waiter serving the round table | Y266 to Y272, Y371 |

**Place and brand**
| What | Codes |
|---|---|
| Logo on the navy wall | Y161, Y162, Y181 |
| Entrance and sign, day and night | Y175, Y176, Y361, Y275 to Y277, Y281 to Y287 |
| Terrace under the umbrellas | Y170 to Y174, Y191, Y192, Y360, Y367, Y373 |
| Lounge, curtains and blossom garlands | Y166 to Y169, Y278 to Y280, Y369 |
| Table settings, lamps, printed placemats | Y177 to Y180, Y244, Y245, Y362 to Y364 |
| Dragon disc art (oval, red light) | Y370 |
| Gong | Y160, Y376 |
| Guests and staff at a table | Y300 to Y302 |
| Empty background textures | Y105, Y159 |

### reseaux/Images: social media (189 images, 2024)
| What | Codes |
|---|---|
| Logos | R144, R145, R121, R143 (Music Live) |
| QR codes (flyer, menu) | R175, R176 |
| Phone photos of the venue (umbrella ceiling, bar LEDs, dragon disc, booths, menus) | R006 to R117 (HEIC, 3024×4032) |
| Live music nights (keyboard player, singer) | R013 to R015, R017 |
| Poke bowl, cocktails, plates (phone) | R084 to R099, R103, R114 to R119 |
| Roll-up banner with a geisha | R104, R105 |
| AI art: dragons, oni masks, geishas, temples, lanterns, scrolls | R001 to R005, R146 to R170, R177 to R184 |
| Banners (fanions): panda, peacock, tiger, dragon | R019 to R024, R132 to R134 |
| Dragon panels for doors, round table art | R172, R173, R169, R170, R182, R183 |
| Wall art: centre, tiger, dragon, demon, wall | R127, R186, R129, R128; R189 `yokoWall_wallOK.jpg` (101 MB) |
| Posts and stories: Tisha B'Av hours, aprem, Hag Sameach, notice, please wait | R025, R126, R142, R187, R120 |
| Gold foil and dark textures | R139 to R141, R185 |

### Videos (reseaux/videos 130, cocktail 6; up to 377 MB each)
| What | Codes |
|---|---|
| Logo animations and outros | V078 (Yoko Ono Piano, 16/09/24), V098, V099 |
| Dish zooms (stills animated) | V124 to V130 |
| Cocktails | V069 to V072, C001 to C003 |
| Live music, crowd, dancing | V021 to V025, V036 to V048, V055 to V066, V084 to V088, V097 |
| Kitchen and serving | V027 to V030, V052, V053, V103, V114, V121 |
| AI clips (Gen-3, Luma): moon trumpet, geisha, temple, dragon, scooter delivery | V001 to V020, V073 to V083, V105 to V112, V122, V123 |
| New Year wishes FR / HE | C005, C006 |

### Print files (huge PDFs, open on Drive only)
- Restaurant wall, `mur resto`: left 1.16 GB, right 824 MB.
- Cash-register area, `caisse`: left, centre, right, about 160 MB each.

## 4. Higgsfield
- **Output:** 192 generations from 2026-09-26 to 2026-11-09, in `media/higgsfield/`. Each one's prompt, model and date is in `media/higgsfield/generations.json`.
  - Red Dragon Tataki ad: 49 images, 32 videos.
  - Push Pop: 28 images.
  - Dragon noodles: 11 images, 3 videos.
  - Dice explainer: 10 images, 3 videos.
  - Gyoza, crispy and wok dishes: 8 images, 2 videos.
  - Trays: 6 images.
  - 3D models: 5.
  - Other: about 35.
- **Uploaded references:** 92 images (`show_medias`). Known ids:
  - dragon `b4483813…`, noodles `376931f5…`, start frame `c7ea0266…`;
  - tray photos `55615fa7…`, `2c8bcd55…`, `51f45471…`, `45ec1c20…`, `ea09642b…`;
  - push-pop renders `1ca4c7a3…`, `afa766fc…`.
- **Models the team liked:**
  - GPT Image 2.5/2.6 (high, 2K) for stills from real photos.
  - Seedance 2.5 for video (480p draft first, then a 1080p finalize from the draft id).
  - Kling 3.0 for character shots.
- **Using a Drive photo as a reference** (free up to the generation):
  1. Download it: `drive_get.py`, or the thumbnail service for HEIC.
  2. Upload it: `media_upload`, then a curl PUT, then `media_confirm`.
  3. Pass the media id in `medias`.
  4. Price check, then ask for approval (see the CLAUDE.md spending rule).

## 5. Projects and where they stand
| Project | Branch | State | Next |
|---|---|---|---|
| Red Dragon Tataki spot (9:16 cut, v2 director's cut, v3 painting ending) | `claude/repo-setup-0cat8s` (`commercial/`) | Done. No credits used in the finishing. | — |
| Dice game explainer video (68 s, Hebrew) | `ccr-56b6f5ef-labe3t` (`commercial/dice-explainer/`) | v6 delivered 2026-11-10: master, screen loop, 15 s Stories cut | Waiting for feedback. Hand in Kling needs a "yes". Instagram handle missing. |
| Dice posters (A3, FR/EN/HE, noir, showa, washi, elegant) | `ccr-501b2ecd-itqixr` (`poster-dice-game/`) | Rendered with the real logo | — |
| In-store display screen (3 styles, 6 sample dishes) | `ccr-501b2ecd-itqixr` (`display-screen/`) | All 6 dishes still use drawn placeholders, `photo: null` | Put real photos in: Nigiri saumon Y351, California Y308, Poke Y385, Gyoza Y334, Tataki Y421. Push Pop has no real photo yet. |
| Dish screen loop (portrait TV, 1080×1920 MP4) | `ccr-53cee3cd-iiiipd` (`menu-screen/`) | Working. 4 black-marble Higgsfield photos (crispy chicken, gyoza, wok noodles, dice). | Add dishes from the pro shoot. Each one needs a photo, a name and an optional price. |
| QR menu poster 80×100 cm (upscale and vector QR) | `ccr-1a3bb758-bwhv30` (`print/`) | Script ready | — |
| Dragon Wok noodles spot (cartoon v2) | `ccr-6a122bd3-g7a5xs` (`commercial/dragon_noodles/`) | 480p draft done (38.25 credits spent) | 1080p finalize quoted at 160 credits, not approved |
| Sushi Push Pop product shots | `ccr-681e7663-npukbh` (`push-pop/`) | Drafts with the real logo wrapped on | Needs the 7 real Push Pop photos. Finals 2.75 credits each, after approval. |
| Push Pop wrap label and sticker (Fuji/Hokusai, kids) | `claude/nifty-knuth-jl7x3n` (`sticker/`) | v4 label, wrap mockups, 2 restaurant product shots | — |
| 3D sushi trays (party, promo; take a roll apart) | `claude/pensive-sagan-05qfc1` (`3d-trays/`) | v5 with photo textures, GLB garnish | Plan for 2K textures and smoother controls in `PLAN.md` |
| Lead finder for other businesses (`/find-leads`) | `claude/jolly-meitner-s4e01m` | Working | Not Yoko Ono |
| Skill security audit | `ccr-b0a7ee3d-623rnm` | Done 2026-11-05. Everything approved; caution on `draw-your-font`. | — |

Related artifacts:
- 3D trays: https://claude.ai/artifact/T4kXJSfCbqVD8ErwXrpFsL
- Red Dragon roll model: https://claude.ai/artifact/ReC8CVFLamGZGh4BjdJr7o
- Nigiri model: https://claude.ai/artifact/CWPJZy5yBHovbj66F9mQQ9
- Media gallery: https://claude.ai/artifact/ETVgwKNXjN3YCS5fpauvMe

## 6. "I want X": what we have and what's missing
- **Screen ideas, proposed 2026-11-12:** https://claude.ai/artifact/JKbLdLudNQpziHbySXNeN2
  - Six mocked-up concepts:
    - fresh this morning;
    - one dish per screen;
    - menu board;
    - programmed by the clock (happy hour from 16:00 to 18:00);
    - atmosphere mosaic;
    - QR and social.
  - Plus a recommended loop of about 2 minutes.
  - The mock source is `knowledge/screen-mock/mock.html` (open it with `?m=A1`, `A2`, `A3`, `B`, `C`, `D`, `E` or `F`); the photos are fetched with `drive_get.py`.
  - Waiting for the user to pick one.
- **Display screen or menu TV:**
  - Have: both screen projects, the pro dish photos, the logo, the fonts.
  - Missing: the final dish list, prices, and a Push Pop photo.
  - Best photos: the grey-concrete set (consistent light). For the black-marble look, run them through Higgsfield as the menu-screen did, with approval.
- **Website:**
  - Have: logo (R145 or the vector trace), hero shots (entrance Y276 and Y277 at night, terrace Y171 to Y174, umbrella ceiling), a dish photo for almost every menu item, a team photo Y299, a craft series (rice), the music nights, QR codes.
  - Missing: no website project exists yet. Also missing: hours, phone, prices, menu text, domain, Instagram.
- **New ad or reel:**
  - Have: the craft series (rice Y148 to Y240, sauce pours Y347 to Y351, black sesame Y403 to Y405, ikura Y096 to Y098), the cocktail series, the dragon disc Y370, the AI clip style (V-series), and the approved Noir & Or style.
  - Use existing footage first. A generation needs a price check and a "yes".
- **Print (flyer, poster, menu):**
  - Have: the poster system on `ccr-501b2ecd-itqixr`, gold textures R139 to R141, logo R145, QR codes R175 and R176.
  - The 80×100 QR poster has an upscale script.
- **3D or trays:** the party trays Y303 to Y306, the tray folder `יוקומגשים`, and the 3D tray project.
