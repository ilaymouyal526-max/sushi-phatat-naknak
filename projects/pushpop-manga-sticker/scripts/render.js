// node scripts/render.js <html> <outdir> <scale> <prefix>
// Screenshots #sideA and #sideB of the layout page to <outdir>/<prefix>_A.png and _B.png.
const { chromium } = require('playwright');
(async () => {
  const [html, outdir, scale, prefix] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage({ deviceScaleFactor: Number(scale), viewport: { width: 1400, height: 1400 } });
  await pg.goto('file://' + html);
  await pg.evaluate(() => document.body.classList.add('print'));
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(500);
  for (const s of ['A', 'B']) {
    await pg.locator('#side' + s).screenshot({ path: `${outdir}/${prefix}_${s}.png` });
  }
  await b.close();
})();
