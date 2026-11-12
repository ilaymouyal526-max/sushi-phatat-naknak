# Yoko Ono: display screen (portrait TV, 1080×1920)

The loop opens on the logo, then shows party trays and dishes in turn. Text is mainly in English, with Hebrew underneath. Each slide stays about 6–7 seconds, so a full loop takes about 48 seconds.

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
- `en` / `heDesc`: the descriptions
- one price option:
  - `price`: a single gold box
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
