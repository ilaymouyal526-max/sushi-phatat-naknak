// Renders logo-mask.html (shared/logo.js, white on black) to a PNG mask for the Blender felt print.
// Usage: node make-logo-mask.js   ->  logo-mask.png (4048 x 2432)
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1012, height: 608 }, deviceScaleFactor: 4 });
  await page.goto("file://" + path.join(__dirname, "logo-mask.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, "logo-mask.png") });
  await browser.close();
  console.log("wrote blender/logo-mask.png");
})();
