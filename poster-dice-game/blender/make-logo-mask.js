// Renders logo-mask.html (shared/logo.js, white on black) to a PNG mask for the Blender felt print.
// Usage: node make-logo-mask.js   ->  logo-mask.png (5x the logo's viewBox)
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 5 });
  await page.goto("file://" + path.join(__dirname, "logo-mask.html"));
  const [, , width, height] = await page.evaluate(() => LOGO_PATH.viewBox.split(" ").map(Number));
  await page.setViewportSize({ width, height });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, "logo-mask.png") });
  await browser.close();
  console.log("wrote blender/logo-mask.png");
})();
