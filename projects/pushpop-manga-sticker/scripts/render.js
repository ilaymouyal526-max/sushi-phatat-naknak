// node scripts/render.js <html> <outdir> <scale> <prefix>
// Screenshots every <svg class="side" id="side<X>"> of the layout page to <outdir>/<prefix>_<X>.png
// (A and B for sticker.html, W for wrap.html) and writes <outdir>/<prefix>_qa.json with the
// bounding box (mm, page coordinates) of every sound effect and panel, for the safe-zone check.
const { chromium } = require('playwright');
(async () => {
  const [html, outdir, scale, prefix] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage({ deviceScaleFactor: Number(scale), viewport: { width: 1400, height: 1400 } });
  await pg.goto('file://' + html);
  await pg.evaluate(() => document.body.classList.add('print'));
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(500);
  const ids = await pg.$$eval('svg.side', els => els.map(e => e.id));
  const qa = {};
  for (const id of ids) {
    const s = id.replace(/^side/, '');
    await pg.locator('#' + id).screenshot({ path: `${outdir}/${prefix}_${s}.png` });
    qa[s] = await pg.$eval('#' + id, svg => {
      const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal, k = vb.width / r.width;
      const mm = el => { const q = el.getBoundingClientRect();
        return [(q.left - r.left) * k, (q.top - r.top) * k, (q.right - r.left) * k, (q.bottom - r.top) * k]; };
      return {
        sfx: [...svg.querySelectorAll('.sfxg text')].map(t => ({
          text: t.textContent, panel: t.parentNode.dataset.panel,
          translate: t.parentNode.getAttribute('transform'), bbox: mm(t) })),
        panels: [...svg.querySelectorAll('g.panel')].map(g => ({ id: g.id, bbox: mm(g.querySelector(':scope > [fill="none"]')) })),
      };
    });
  }
  require('fs').writeFileSync(`${outdir}/${prefix}_qa.json`, JSON.stringify(qa, null, 1));
  await b.close();
})();
