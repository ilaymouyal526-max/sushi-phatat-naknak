// confirms the four scanned garnish meshes load from their base64 modules
const {chromium} = require('playwright');
(async()=>{
  const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p = await b.newPage({viewport:{width:640, height:640}});
  const errs = []; p.on('pageerror', e=>errs.push(e.message)); p.on('console', m=>{ if(m.type()==='error' && !m.text().includes('ERR_')) errs.push(m.text()); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/three@0\.169\.0\/(.*)/, r=>{ const m = r.request().url().match(/three@0\.169\.0\/(.*)/); r.fulfill({path:'node_modules/three/'+m[1], contentType:'application/javascript'}); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/camera-controls@2\.9\.0\/(.*)/, r=>{ const m = r.request().url().match(/camera-controls@2\.9\.0\/(.*)/); r.fulfill({path:'node_modules/camera-controls/'+m[1], contentType:'application/javascript'}); });
  await p.route(/fonts\./, r=>r.fulfill({body:'', contentType:'text/css'}));
  await p.goto('http://127.0.0.1:8765/index.html?q=2');
  await p.waitForFunction(()=>window.__ready, null, {timeout:240000});
  const kinds = await p.evaluate(()=>window.__yoko.garnish.children.map(o=>{ let n = 0; o.traverse(m=>{ if(m.isMesh && m.geometry.index && m.geometry.index.count > 30000) n++; }); return o.userData.kind + (n ? ':scan' : ':built'); }));
  console.log(JSON.stringify(kinds)); console.log('errors:', errs.length, errs.slice(0,3).join(' | '));
  await p.screenshot({path:'n_meshcheck.png'});
  await b.close();
})();
