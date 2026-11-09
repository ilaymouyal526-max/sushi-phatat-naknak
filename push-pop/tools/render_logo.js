const { chromium } = require('playwright');
const fs = require('fs');
const S = process.argv[2];
global.window = {};
eval(fs.readFileSync(S + '/logo-path.js', 'utf8'));
const { viewBox, d } = window.LOGO_PATH;
const [vx, vy, vw, vh] = viewBox.split(' ').map(Number);
const K = 4; // px per viewBox unit
const html = `<!doctype html><html><head><style>
@font-face{font-family:M;src:url(file://${S}/montserrat-latin.woff2) format('woff2');font-weight:100 900}
html,body{margin:0;background:transparent}</style></head><body>
<svg width="${vw*K}" height="${vh*K}" viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg">
<path d="${d}" fill="#fff" fill-rule="evenodd"/>
<text x="382" y="522" text-anchor="middle" fill="#fff" font-family="M" font-weight="500" font-size="29" letter-spacing="4.2">ASIAN KITCHEN</text>
</svg></body></html>`;
fs.writeFileSync(S + '/logo.html', html);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: vw*K, height: vh*K } });
  await p.goto('file://' + S + '/logo.html'); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: S + '/logo_white.png', omitBackground: true });
  await b.close(); console.log(vx, vy, vw, vh, K);
})();
