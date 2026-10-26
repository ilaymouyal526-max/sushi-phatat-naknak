// Render harness for the tray page: serves three.js and camera-controls from node_modules, waits for the page to be ready,
// then runs a list of steps. Usage: node shot4.js <name> <step> [<step> ...]
//   steps: tray:<id>  view:<angle|top|low>  focus:<pieceIndex>  explode  iso:<i>  back  swap:<dir>  garn:<i>  wait:<ms>  shot:<file>  q:<level>
const {chromium} = require('playwright');
(async()=>{
  const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const vp = (process.env.VP || '1000x1000').split('x').map(Number);
  const p = await b.newPage({viewport:{width:vp[0], height:vp[1]}});
  const errs = [];
  p.on('pageerror', e=>{ errs.push(e.message); console.log('PAGEERROR', e.message); });
  p.on('console', m=>{ if(m.type()==='error' && !m.text().includes('ERR_')){ errs.push(m.text()); console.log('CONSOLE', m.text()); } if(m.type()==='warning') console.log('WARN', m.text().slice(0,200)); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/three@0\.169\.0\/(.*)/, r=>{ const m = r.request().url().match(/three@0\.169\.0\/(.*)/); r.fulfill({path:'node_modules/three/'+m[1], contentType:'application/javascript'}); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/camera-controls@2\.9\.0\/(.*)/, r=>{ const m = r.request().url().match(/camera-controls@2\.9\.0\/(.*)/); r.fulfill({path:'node_modules/camera-controls/'+m[1], contentType:'application/javascript'}); });
  await p.route(/fonts\./, r=>r.fulfill({body:'', contentType:'text/css'}));
  const t0 = Date.now();
  await p.goto('http://127.0.0.1:8765/index.html?q=' + (process.env.Q || '0'));
  await p.waitForFunction(()=>window.__ready, null, {timeout:240000});
  console.log('ready in', (Date.now()-t0)/1000, 's');
  for(const step of process.argv.slice(2)){
    const [k, v] = step.split(':');
    if(k === 'wait') await p.waitForTimeout(+v);
    else if(k === 'tray') { await p.evaluate(t=>document.querySelector(`button[data-t=${t}]`).click(), v); await p.waitForTimeout(6000); }
    else if(k === 'view') { await p.evaluate(t=>document.querySelector(`button[data-v=${t}]`).click(), v); await p.waitForTimeout(5000); }
    else if(k === 'focus') { await p.evaluate(i=>window.__yoko.focusPiece(+i), v); await p.waitForTimeout(5000); }
    else if(k === 'explode') { await p.evaluate(()=>window.__yoko.toggleExplode()); await p.waitForTimeout(5000); }
    else if(k === 'iso') { await p.evaluate(i=>window.__yoko.isolate(+i), v); await p.waitForTimeout(4500); }
    else if(k === 'back') { await p.evaluate(()=>window.__yoko.backToTray()); await p.waitForTimeout(5000); }
    else if(k === 'swap') { await p.evaluate(d=>window.__yoko.swapRoll(+d), v); await p.waitForTimeout(4500); }
    else if(k === 'garn') { await p.evaluate(i=>window.__yoko.focusGarnish(window.__yoko.garnish.children[+i]), v); await p.waitForTimeout(4500); }
    else if(k === 'fills') { await p.waitForFunction(()=>window.__fills, null, {timeout:400000}); }
    else if(k === 'info') { console.log(await p.evaluate(()=>JSON.stringify({calls:window.__yoko.cc && 0}))); }
    else if(k === 'shot') { await p.screenshot({path:v, timeout:300000}); console.log('shot', v); }
  }
  console.log('errors:', errs.length);
  await b.close();
})();
