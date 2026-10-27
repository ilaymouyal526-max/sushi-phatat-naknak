// Renders the portrait screen slides (1080 x 1920 PNG) for each style:
// one slide per dish, plus slides of four dishes at a time.
// Usage: node render.js [--sample] [noir|washi|showa ...]
//   --sample renders only a few slides per style, for choosing a design.
const path = require("path");
const fs = require("fs");
const vm = require("vm");
const { chromium } = require("playwright");

const args = process.argv.slice(2);
const sample = args.includes("--sample");
const styles = args.filter(a => !a.startsWith("--"));
const STYLES = styles.length ? styles : ["noir", "washi", "showa"];

// Read the dish list the same way the pages do
const ctx = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "dishes.js"), "utf8"), ctx);
const count = ctx.window.DISHES.length;
const slug = s => s.toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function slides() {
  const all = [...Array(count).keys()];
  const heroes = (sample ? [0, 4] : all).map(i => ({ q: `layout=hero&dish=${i}`, name: `dish-${String(i + 1).padStart(2, "0")}-${slug(ctx.window.DISHES[i].name)}` }));
  const grids = [];
  for (let i = 0; i < count; i += 4) {
    grids.push({ q: `layout=grid&dishes=${all.slice(i, i + 4).join(",")}`, name: `menu-${grids.length + 1}` });
    if (sample) break;
  }
  return [...heroes, ...grids];
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  for (const style of STYLES) {
    const dir = path.join(__dirname, "out", sample ? "sample" : "", style);
    fs.mkdirSync(dir, { recursive: true });
    for (const s of slides()) {
      await page.goto(`file://${path.join(__dirname, style + ".html")}?${s.q}`);
      await page.evaluate(() => document.fonts.ready);
      if (errors.length) throw new Error(`${style} ${s.q}: ${errors.join("; ")}`);
      const overflow = await page.evaluate(() => {
        const screen = document.getElementById("screen").getBoundingClientRect();
        return [...document.querySelectorAll("#content *")].some(e => e.getBoundingClientRect().bottom > screen.bottom - 60);
      });
      await page.locator("#screen").screenshot({ path: path.join(dir, s.name + ".png") });
      console.log(`${style}/${s.name}.png${overflow ? "  <-- content reaches the bottom edge" : ""}`);
    }
  }
  await browser.close();
})();
