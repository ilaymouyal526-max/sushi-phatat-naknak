// Prints tools/shotlist.html to an A4 PDF with Playwright's Chromium. Usage: node shotlist_pdf.js <html> <pdf>
const { chromium } = require("playwright");
(async () => {
  const [html, pdf] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: pdf, format: "A4", printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
