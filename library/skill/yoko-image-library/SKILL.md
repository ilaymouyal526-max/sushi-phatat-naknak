---
name: yoko-image-library
description: Finds Yoko Ono (Asian Kitchen / sushi restaurant) images, logo and brand assets the user already has, instead of asking them to upload. Use whenever a task needs a photo, dish image, logo, tray, behind-the-scenes shot, Sushi Push Pop asset, reference image or "our pictures" (תמונה, תמונות, לוגו, צילום, מגש, מנה, רול, סושי) for Yoko Ono, before asking the user for any image.
---

# Yoko Ono image library

The user is tired of being asked to upload images. **They already have everything.** Before you ask for any
image, search this library. Ask for an upload only if you searched and found nothing that fits, and then say
exactly what you searched.

## Where the images are

| What | Where | How to reach it |
|---|---|---|
| **Logo** (gold arch, cherry blossoms, mountains, "YOKO ONO / ASIAN KITCHEN", bowl and chopsticks, gold on black) | Higgsfield › Media: `616cdc78-1bc1-4fdc-8511-ffdced8b4c36.png` (Sushi Push Pop packaging that contains the full logo). A cropped copy is in the GitHub repo `sushi-phatat-naknak` at `library/brand/yoko-ono-logo_gold-on-black.png` | Higgsfield `show_medias`, or the public URL in `catalog.csv`. **Low resolution.** Ask only for a vector original when it's needed for print. |
| **Professional dish photos**: 199 named + 152 raw (`A74xxxxx.jpg`), plus 18 photos of the restaurant itself | Google Drive, shared folder **YOKO ONO › images_yoko** (folder id `1D0jUwKnMMdP8N925Z4uWGMOwv2Cq5ULA`, read-only, owner is Michael) | Drive `search_files` with `parentId = '1D0jUwKnMMdP8N925Z4uWGMOwv2Cq5ULA' and title contains '<French word>'`, then `download_file_content` |
| **Party trays** (2 Oct 2026): open, wrapped with the YOKO ONO ribbon, stacked on the bar | User's Drive: folder **יוקומגשים** and root | Drive search: `title contains 'מגש אירוח'`. Files starting with "(עותק כפול)" are duplicates; skip them |
| **Behind the scenes at the sushi bar** (22 Oct 2026, 20:30–21:31): rolling, torching, seared salmon nigiri, cucumber cups, hand rolls | User's Drive, root | Drive search: `title contains '22.10.2026'` or a Hebrew word (`ניגירי`, `טורץ׳`, `הנד-רולים`, `גביעי מלפפון`). Frames in the middle of a burst keep their camera name `20261022_HHMMSS.heic` |
| **Avocado-wrapped seared-tuna roll** (23 Sep 2026, 4 WhatsApp photos) | User's Drive, root | `title contains 'טונה צרובה'` |
| **Red Dragon tataki** (studio shot + display-screen frame) | Drive › Yoko Ono › מסך תצוגה | `title contains 'רד דרגון'` |
| **Sushi Push Pop**: packaging, how-to card, 4 ad frames, a photo of the real prototype; dragon illustrations; wok and noodles | Higgsfield › Media | `show_medias` (type image); the image-to-content map is in `catalog.csv` (`where` = Higgsfield) |

**The full index of all 662 images** is in `catalog.csv` next to this file: the id, a Hebrew description (`what`),
category, current name, location, and duplicate status. Search it first:
`grep -i "ניגירי" catalog.csv`, or filter by the `category` column.

## French → Hebrew (names in the shared folder)

nigiri saumon = ניגירי סלמון · nigiri thon = ניגירי טונה · sashimi thon = סשימי טונה · sashimi 3 poissons = סשימי 3 דגים ·
salade sashimi = סלט סשימי · chirachi = צ׳ירשי · tataki thon/saumon = טטאקי טונה/סלמון · yakitori saumon = יקיטורי סלמון ·
guioza/gyoza = גיוזה · general tao = ג׳נרל טאו · darne saumon = נתח סלמון · poisson du jour = דג היום · tonkatsu = טונקאטסו ·
pad kapao = פאד קפאו · shrimp crispy coco = שרימפס קריספי קוקוס · noodles chicken/meat/curry = נודלס עוף/בקר/קארי ·
bœuf caramélisé = בקר מקורמל · crispy chicken bann = באן עוף קריספי · crispy rice = קריספי רייס · crazy roll · volcano ·
maguro roll · panko roll · california · maki · mochi = מוצ׳י · edamame = אדממה · ambiance = אווירה במסעדה.
`wolt` in a file name means the version chosen for Wolt.

## Technical notes

- HEIC phone photos: if ImageMagick doesn't decode HEVC, use `heic2jpg.py` from this folder: `python3 -I heic2jpg.py in.heic out.jpg`.
- Drive `download_file_content` is capped at 10MB.
- The shared folder's files are link-shared: a quick thumbnail at `https://drive.google.com/thumbnail?id=<ID>&sz=w400`.
- Drive storage is full (Nov 2026), so new uploads to Drive fail. Renames and descriptions still work.
- A new image that gets created or found goes into `catalog.csv` with a Hebrew name: `<תיאור> · <DD.MM.YYYY> · <מזהה>.<ext>`.
- Spending rule: never spend credits (Higgsfield, Artlist, Adobe and so on) without the user's explicit approval. Searching and downloading are free.
