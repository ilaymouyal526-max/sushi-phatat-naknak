// Renders one full loop of the dish screen to an MP4 (1080x1920, H.264) for TVs that play video from USB.
// Steps every CSS animation frame by frame, so the video matches the live page exactly.
// Usage: node render.js [out.mp4] [fps] [style]   (style: framed, cinema or mix; default from CONFIG)
const path = require("path");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const OUT = path.resolve(process.argv[2] || path.join(__dirname, "out", "yoko-ono-screen-loop.mp4"));
const FPS = Number(process.argv[3] || 30);

(async () => {
  require("fs").mkdirSync(path.dirname(OUT), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  const STYLE = process.argv[4];   // optional: framed, cinema or mix
  await page.goto("file://" + path.join(__dirname, "index.html") + "?render=1" + (STYLE ? "&style=" + STYLE : ""));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.images, ...[...document.querySelectorAll(".ph,.photo")]
    .map(e => { const i = new Image(); i.src = getComputedStyle(e).backgroundImage.slice(5, -2); return i; })]
    .map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
  if (errors.length) throw new Error(errors.join("; "));

  const slides = await page.evaluate(() => window.SLIDES);
  const total = slides.reduce((a, b) => a + b, 0);
  const frames = Math.round(total * FPS);
  console.log(`${slides.length} slides, ${total}s, ${frames} frames → ${OUT}`);

  const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], { stdio: ["pipe", "inherit", "inherit"] });

  // Each animation is pinned to (now - the moment it first appeared)
  await page.evaluate(() => { window.__born = new WeakMap(); window.__step = t => {
    document.body.offsetHeight;
    for (const a of document.getAnimations()) {
      if (!__born.has(a)) __born.set(a, t);
      a.pause(); a.currentTime = (t - __born.get(a)) * 1000;
    }
  }; });

  let slide = -1, edge = 0;
  for (let f = 0; f < frames; f++) {
    const t = f / FPS;
    while (slide < 0 || t >= edge) { slide++; edge += slides[slide]; await page.evaluate(i => window.go(i), slide); }
    await page.evaluate(t => window.__step(t), t);
    ff.stdin.write(await page.screenshot({ type: "jpeg", quality: 95 }));
    if (f % (FPS * 5) === 0) process.stdout.write(`  ${Math.round(t)}s\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log("done");
})();
