// Renders the realistic props in tools/props.html to assets/img/*.png. Run: node tools/render_props.js
const path = require("path"), fs = require("fs");
const { chromium } = require("playwright");
const ONLY = process.argv[2];
const OUT = path.join(__dirname, "..", "assets", "img");
(async () => {
  const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
  const page = await browser.newPage();
  page.on("pageerror", (e) => { console.error(e); process.exitCode = 1; });
  await page.goto("file://" + path.join(__dirname, "props.html"));
  await page.waitForFunction(() => window.ready);
  const save = async (name, js) => {
    const url = await page.evaluate(js);
    fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(",")[1], "base64"));
    console.log("wrote", name);
  };
  for (let f = 1; f <= 6; f++) await save(`die-${f}.png`, `renderDie(${f})`);
  for (let k = 0; k < 12; k++) await save(`die-roll-${k}.png`, `renderDie(${(k % 6) + 1}, [${(0.35 + 0.22 * k).toFixed(2)}, ${(0.5 * k).toFixed(2)}, ${(0.6 - 0.17 * k).toFixed(2)}])`);
  await save("receipt.png", "renderReceipt()");
  await save("coin.png", "renderCoin(0)");
  await save("knife.png", "renderKnife()");
  for (const p of ["fist", "release", "open"]) await save(`hand-${p}.png`, `renderHand("${p}")`);
  await browser.close();
})();
