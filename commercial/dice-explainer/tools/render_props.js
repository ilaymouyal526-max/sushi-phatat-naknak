// Renders the film's props to assets/img/*.png (free, local Three.js + Playwright). Run from commercial/dice-explainer:
//   node tools/render_props.js            all props
//   node tools/render_props.js dice       one group: dice | hand | receipt | coin
// Then it checks every image (and every cell of each tumble strip): nothing may touch the frame edge, so a prop is
// never cut off on screen. The check decodes the images back in the browser.
const path = require("path"), fs = require("fs");
const { chromium } = require("playwright");
const ONLY = process.argv[2];
const OUT = path.join(__dirname, "..", "assets", "img");
const want = (g) => !ONLY || ONLY === g;

(async () => {
  const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--allow-file-access-from-files"] });
  const written = [];
  async function open(file) {
    const page = await browser.newPage();
    page.on("pageerror", (e) => { console.error(e); process.exitCode = 1; });
    await page.goto("file://" + path.join(__dirname, file));
    await page.waitForFunction(() => window.ready, null, { timeout: 30000 });
    return page;
  }
  async function save(page, name, js, cells = null) {
    const url = await page.evaluate(js);
    fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(",")[1], "base64"));
    written.push([name, cells]); console.log("wrote", name);
  }

  if (want("dice")) {
    const p = await open("dice.html");
    for (const v of ["a", "b"]) for (let f = 1; f <= 6; f++) {
      await save(p, `die-${f}${v}.png`, `renderStill(${f}, "${v}", 1024)`);
      // 24 frames of a tumble that lands on face f, 512 px each, in a 6 x 4 grid
      await save(p, `die-strip-${f}${v}.webp`, `renderStrip(${f}, "${v}", 512, 24, 6, 6)`, [6, 4]);
    }
  }
  if (want("hand")) {
    const p = await open("hand.html");
    for (const pose of ["open", "release", "fist", "flat"]) await save(p, `hand-${pose}.png`, `renderHand("${pose}", 800, 1280, 2)`);
  }
  if (want("receipt") || want("coin")) {
    const p = await open("props.html");
    if (want("receipt")) await save(p, "receipt.png", "renderReceipt()");
    if (want("coin")) {
      await save(p, "coin.png", "renderCoin(0, 0.3)");
      // the tip coin settling: it lands on its edge and wobbles flat while it turns, 12 frames
      for (let k = 0; k < 12; k++) {
        const t = k / 11, tilt = 1.25 * Math.pow(1 - t, 1.6) * Math.cos(t * 9.5), spin = 0.3 - 2.2 * Math.pow(1 - t, 2);
        await save(p, `coin-settle-${k}.png`, `renderCoin(${tilt.toFixed(4)}, ${spin.toFixed(4)})`);
      }
    }
  }

  // Edge check: the alpha bounding box of each image (or grid cell) must keep a margin from the frame.
  const page = await browser.newPage();
  const bad = [];
  for (const [name, cells] of written) {
    const b64 = fs.readFileSync(path.join(OUT, name)).toString("base64");
    const res = await page.evaluate(async ({ b64, cells, mime }) => {
      const img = new Image(); img.src = `data:image/${mime};base64,` + b64; await img.decode();
      const [cx, cy] = cells || [1, 1], w = img.width / cx, h = img.height / cy;
      const c = document.createElement("canvas"); c.width = img.width; c.height = img.height; const g = c.getContext("2d"); g.drawImage(img, 0, 0);
      const out = [];
      for (let j = 0; j < cy; j++) for (let i = 0; i < cx; i++) {
        const d = g.getImageData(i * w, j * h, w, h).data; let x0 = w, y0 = h, x1 = -1, y1 = -1;
        for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (d[(y * w + x) * 4 + 3] > 8) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
        out.push({ cell: j * cx + i, x0, y0, x1, y1, w, h });
      }
      return out;
    }, { b64, cells, mime: name.endsWith(".webp") ? "webp" : "png" });
    for (const r of res) {
      // the hand's sleeve is meant to run off the bottom of its frame
      const edgeOk = name.startsWith("hand-") ? r.x0 > 2 && r.y0 > 2 && r.x1 < r.w - 3 : r.x0 > 2 && r.y0 > 2 && r.x1 < r.w - 3 && r.y1 < r.h - 3;
      if (!edgeOk) bad.push(`${name}${cells ? " cell " + r.cell : ""}: bbox ${r.x0},${r.y0}-${r.x1},${r.y1} in ${r.w}x${r.h}`);
    }
  }
  await browser.close();
  if (bad.length) { console.error("Props touching the frame edge:\n  " + bad.join("\n  ")); process.exitCode = 1; }
  else console.log(`edge check: ${written.length} images clean`);
})();
