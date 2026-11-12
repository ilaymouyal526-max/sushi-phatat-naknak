# Yoko Ono: display screen (portrait TV, 1080×1920)

The loop opens on the logo, then shows party trays and dishes in turn. Text is mainly in English, with Hebrew underneath. Each slide stays about 6–7 seconds, so a full loop takes about 48 seconds.

## Style: "Sumi" (minimal Japanese, black and gold)
- **Three font families, five sizes, nothing else:**
  - Montserrat Light/Regular for English.
  - Heebo Light for Hebrew text, with Frank Ruhl for the Hebrew dish name.
  - Shippori Mincho for Japanese.
  - The five sizes are `--xs` 20, `--s` 28, `--m` 36, `--l` 64 and `--xl` 96. They are defined once in `:root` in `index.html`.
- **Japanese layout:** each dish gets a vertical kanji column with kana on the left (`jp` / `kana` in `CONFIG`) and a red 運 hanko seal. Frames are single gold hairlines.
- **Motion:** each slide builds itself in:
  1. The photo brush-wipes in from the top.
  2. The kanji column wipes in and slowly drifts upward.
  3. The hairlines draw out from the centre and the title letters rise one after another.
  4. The Hebrew name, description and prices fade up out of a soft blur.
  5. The seal stamps down, and a light sheen sweeps across the photo and the XL box.

| # | Slide | Price on screen |
|---|---|---|
| 0 | Logo | |
| 1 | Party tray (round) | "Order ahead" (no price yet) |
| 2 | Gyoza | Chicken 55 ₪ · Beef 59 ₪ |
| 3 | Promo tray L / XL | 199 ₪ (56 pcs) / 299 ₪ (80 pcs) |
| 4 | Red Dragon Tataki | (no price yet) |
| 5 | Caramel tempura chicken | 72 ₪ |
| 6 | Sushi Push Pop ("New") | (no price yet) |
| 7 | House wok noodles | Chicken 69 · Tempura 72 · Veggie 59 ₪ |

The dice-game slides are still in the code. Set `showGame: true` in `CONFIG` to bring them back.

## Two ways to run it on the screen
- **USB / smart TV:** play `out/yoko-ono-screen-loop.mp4` on repeat (H.264, 1080×1920, 30fps).
- **Computer connected to the screen:** copy the whole repository folder, open `menu-screen/index.html` in Chrome, and press **F** for fullscreen. The page keeps the screen awake and reloads itself every 6 hours. The right arrow key or space skips to the next slide.

## Changing slides, text or prices
Everything is in the `CONFIG` block at the bottom of `index.html`. `slides` is the loop in order. Each entry takes:
- `photo`
- `name` / `he`: the title in English and Hebrew
- `jp` / `kana` (optional): the vertical Japanese column. The kanji must be in the Shippori Mincho subset (listed in `fonts/fonts.css`).
- `en` / `heDesc`: the descriptions
- one price option:
  - `price`: `"Chicken 69 ₪ · Veggie 59 ₪"` shows each label over its number. Text without numbers (`"Order ahead"`) shows as a gold note line.
  - `options`: side-by-side boxes, used for the L/XL trays
- `kicker` (optional): a small gold line above the title. Without it, the slide is numbered N° 01, N° 02, …
- `seconds` (optional): how long the slide stays on screen

To add a slide, put its photo in `images/` and add an entry. Then re-render the video:

```
node render.js out/yoko-ono-screen-loop.mp4 30
```

## Photos (all already made, no new credits used)
- `*-marble.jpg`: Higgsfield (GPT Image 2.5) from the kitchen photos, on a black marble tray.
- `party-tray.jpg`, `party-tray-2.jpg`: Higgsfield (Nano Banana 2), the round party platter from the real Yoko tray photos.
- `promo-tray.jpg`: a still from the 3D tray model (square promo tray).
- `push-pop.jpg`: Higgsfield product shot of the push pop with the new label, in the restaurant.
- `red-dragon-tataki.jpg`: crop of the Red Dragon Tataki hero image from the commercial.
