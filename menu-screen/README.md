# Yoko Ono: display screen (portrait TV, 1080×1920)

The loop opens on the logo, then shows party trays and dishes in turn. Text is mainly in English, with Hebrew underneath. Each slide stays about 6–7 seconds, so a full loop takes about 48 seconds.

## Three styles, one design system
Set `style` in `CONFIG`, or add `?style=cinema` to the address in Chrome.

| Style | Look |
|---|---|
| `framed` (default) | The photo sits in a gold hairline frame, with the full text: titles, descriptions and prices. |
| `cinema` | A full-bleed film frame in the style of the Red Dragon ad's supers. The photo fills the screen and fades into black. It has a slow dolly-in (wide photos pan sideways, `pan: true`), a warm light leak drifting across, film grain and a vignette. Text is minimal: a widely tracked title, the Hebrew name and prices, with no descriptions. |
| `mix` | Alternates `framed` and `cinema` from slide to slide. |

All three share the "Sumi" system below.

## Five colour themes
Set `theme` in `CONFIG`, or add `?theme=washi` to the address. Styles and themes combine, for example `?style=cinema&theme=aka`.

| Theme | Colours |
|---|---|
| `noir` (default) | Black and gold |
| `washi` 和紙 | Light: rice paper, sumi ink and vermilion red |
| `aka` 朱漆 | Red lacquer and gold, with a gold seal |
| `ai` 藍 | Indigo and silver, with a red seal |
| `matcha` 抹茶 | Deep green and antique gold |

Every colour is a token in `:root`, and each theme overrides those tokens in one block (`#screen[data-theme=…]`). To add a theme, copy a block and change its values.

## "Sumi" design system (minimal Japanese, black and gold)
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
- **USB / smart TV:** play one of `out/yoko-ono-screen-framed.mp4`, `-cinema.mp4` or `-mix.mp4` on repeat (H.264, 1080×1920, 30fps).
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
- `pan: true` (optional, cinema): pans across a wide photo instead of the dolly-in

To add a slide, put its photo in `images/` and add an entry. Then re-render the video:

```
node render.js out/yoko-ono-screen-framed.mp4 30 framed
node render.js out/yoko-ono-screen-cinema.mp4 30 cinema
node render.js out/yoko-ono-screen-mix.mp4 30 mix
node render.js out/yoko-ono-screen-mix-washi.mp4 30 mix washi   # 4th argument: colour theme
```

## Photos (all already made, no new credits used)
- `*-marble.jpg`: Higgsfield (GPT Image 2.5) from the kitchen photos, on a black marble tray.
- `party-tray.jpg`, `party-tray-2.jpg`: Higgsfield (Nano Banana 2), the round party platter from the real Yoko tray photos.
- `promo-tray.jpg`: a real square tray from the professional photo shoot (Drive `Y304`, file `A7402524.jpg`), not the 3D model.
- `push-pop.jpg`: Higgsfield product shot of the push pop with the new label, in the restaurant.
- `red-dragon-tataki.jpg`: the finished row of Red Dragon Tataki on the board, a 9:16 film frame made for the ad (Higgsfield GPT Image 2.5, `…5cd9f208058d`).
