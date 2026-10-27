// Renders the side-by-side comparison sheets from the poster and screen renders.
// Run poster-dice-game/render.js and display-screen/render.js --sample first.
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  for (const sheet of ["posters", "screens"]) {
    await page.goto(`file://${path.join(__dirname, "overview.html")}?sheet=${sheet}`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth));
    await page.locator("#sheet").screenshot({ path: path.join(__dirname, `${sheet}-overview.png`) });
    console.log(`wrote previews/${sheet}-overview.png`);
  }
  await browser.close();
})();
