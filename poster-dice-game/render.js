// Renders poster.html to a print-ready A3 PDF and a 300 dpi PNG.
// Usage: node render.js [--preview]
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const preview = process.argv.includes("--preview");
const outDir = path.join(__dirname, "out");
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  // A3 = 297 x 420 mm = 1123 x 1588 CSS px; 3.125x gives ~300 dpi (3508 x 4961)
  const page = await browser.newPage({
    viewport: { width: 1123, height: 1588 },
    deviceScaleFactor: preview ? 1 : 3.125,
  });
  await page.goto("file://" + path.join(__dirname, "poster.html"));
  await page.evaluate(() => document.fonts.ready);

  const fit = await page.evaluate(() => {
    const poster = document.getElementById("poster").getBoundingClientRect();
    const last = document.querySelector(".notes").getBoundingClientRect();
    const sign = document.querySelector(".signoff").getBoundingClientRect();
    return { posterH: poster.height, notesBottom: last.bottom, signTop: sign.top };
  });
  console.log("layout:", fit);

  const poster = page.locator("#poster");
  const png = path.join(outDir, preview ? "preview.png" : "yoko-ono-grand-jeu-A3.png");
  await poster.screenshot({ path: png });
  console.log("wrote", png);

  if (!preview) {
    const pdf = path.join(outDir, "yoko-ono-grand-jeu-A3.pdf");
    await page.emulateMedia({ media: "print" });
    await page.pdf({ path: pdf, width: "297mm", height: "420mm", printBackground: true, preferCSSPageSize: true });
    console.log("wrote", pdf);
  }
  await browser.close();
})();
