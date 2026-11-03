# Yoko Ono: dish screen (portrait TV, 1080×1920)

Loop: logo, then each dish followed by the dice game ("Le Grand Jeu"). The text is in French, English and Hebrew. One loop takes 64 seconds.

## Two ways to run it on the screen
- **USB / smart TV:** play `out/yoko-ono-screen-loop.mp4` on repeat (H.264, 1080×1920, 30fps).
- **Computer connected to the screen:** copy the whole repository folder, open `menu-screen/index.html` in Chrome, and press **F** for fullscreen. The page keeps the screen awake and reloads itself every 6 hours.

## Changing dishes or text
Edit the `CONFIG` block at the bottom of `index.html` (photo, names, descriptions, price, slide durations), then re-render the video:

```
node render.js out/yoko-ono-screen-loop.mp4 30
```

## Photos
The `images/*-marble.jpg` files were generated in Higgsfield (GPT Image 2.5, high, 2K, 4:5) from the kitchen photos: a black room, overhead light, and a black marble tray with gold veins.
