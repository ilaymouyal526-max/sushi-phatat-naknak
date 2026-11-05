# Yoko Ono: dish screen (portrait TV, 1080×1920)

Loop: logo, then the dishes one after another (dishes only). The text is mainly in English, with Hebrew underneath. One loop takes 22 seconds, plus 6 seconds for each dish you add. The dice-game slides are still in the code: set `showGame: true` in `CONFIG` to bring them back.

## Two ways to run it on the screen
- **USB / smart TV:** play `out/yoko-ono-screen-loop.mp4` on repeat (H.264, 1080×1920, 30fps).
- **Computer connected to the screen:** copy the whole repository folder, open `menu-screen/index.html` in Chrome, and press **F** for fullscreen. The page keeps the screen awake and reloads itself every 6 hours.

## Changing dishes or text
To add a dish (for example the Sushi Pop), put its photo in `images/` and add one more entry to `dishes` in `CONFIG`.
Edit the `CONFIG` block at the bottom of `index.html` (photo, names, descriptions, price, slide durations), then re-render the video:

```
node render.js out/yoko-ono-screen-loop.mp4 30
```

## Photos
The `images/*-marble.jpg` files were generated in Higgsfield (GPT Image 2.5, high, 2K, 4:5) from the kitchen photos: a black room, overhead light, and a black marble tray with gold veins.
