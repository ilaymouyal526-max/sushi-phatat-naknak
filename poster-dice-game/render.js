// Renders A3 poster HTML files to a print-ready PDF and a 300 dpi PNG.
// Usage: node render.js [--preview] [file.html ...]   (default: every poster)
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const args = process.argv.slice(2);
const preview = args.includes("--preview");
const POSTERS = {
  "poster.html": "yoko-ono-grand-jeu-A3",
  "trilingual/noir.html": "yoko-ono-grand-jeu-FR-EN-HE-noir-A3",
  "trilingual/washi.html": "yoko-ono-grand-jeu-FR-EN-HE-washi-A3",
  "trilingual/showa.html": "yoko-ono-grand-jeu-FR-EN-HE-showa-A3",
  "trilingual/noir-photo.html": "yoko-ono-grand-jeu-FR-EN-HE-noir-photo-A3",
};
const files = args.filter(a => !a.startsWith("--"));
const outDir = path.join(__dirname, "out");
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  for (const file of files.length ? files : Object.keys(POSTERS)) {
    const name = POSTERS[file] || path.basename(file, ".html");
    // A3 = 297 x 420 mm = 1123 x 1588 CSS px; 3.125x gives ~300 dpi (3508 x 4961)
    const page = await browser.newPage({ viewport: { width: 1123, height: 1588 }, deviceScaleFactor: preview ? 1 : 3.125 });
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.goto("file://" + path.join(__dirname, file));
    await page.evaluate(() => document.fonts.ready);
    if (errors.length) throw new Error(`${file}: ${errors.join("; ")}`);

    // Report content that runs past the bottom padding of .content
    const fit = await page.evaluate(() => {
      const content = document.querySelector(".content");
      const limit = content.getBoundingClientRect().bottom - parseFloat(getComputedStyle(content).paddingBottom);
      const bottom = Math.max(...[...content.querySelectorAll("*")].map(e => e.getBoundingClientRect().bottom));
      return { bottom: Math.round(bottom), limit: Math.round(limit) };
    });
    console.log(`${file}: content ends at ${fit.bottom}px (limit ${fit.limit}px)${fit.bottom > fit.limit ? "  <-- OVERFLOW" : ""}`);

    const poster = page.locator("#poster");
    if (preview) {
      await poster.screenshot({ path: path.join(outDir, `preview-${name}.png`) });
    } else {
      await poster.screenshot({ path: path.join(outDir, `${name}.png`) });
      await page.emulateMedia({ media: "print" });
      await page.pdf({ path: path.join(outDir, `${name}.pdf`), width: "297mm", height: "420mm", printBackground: true, preferCSSPageSize: true });
      console.log(`  wrote out/${name}.png and .pdf`);
    }
    await page.close();
  }
  await browser.close();
})();
