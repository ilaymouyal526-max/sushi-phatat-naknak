// Interaction check: real pointer clicks and buttons, interrupted moves, tray switches; reports errors and stuck states.
const {chromium} = require('playwright');
(async()=>{
  const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const p = await b.newPage({viewport:{width:640, height:720}});
  const errs = [];
  p.on('pageerror', e=>errs.push('PAGEERROR ' + e.message));
  p.on('console', m=>{ if(m.type()==='error' && !m.text().includes('ERR_')) errs.push('CONSOLE ' + m.text()); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/three@0\.169\.0\/(.*)/, r=>{ const m = r.request().url().match(/three@0\.169\.0\/(.*)/); r.fulfill({path:'node_modules/three/'+m[1], contentType:'application/javascript'}); });
  await p.route(/cdn\.jsdelivr\.net\/npm\/camera-controls@2\.9\.0\/(.*)/, r=>{ const m = r.request().url().match(/camera-controls@2\.9\.0\/(.*)/); r.fulfill({path:'node_modules/camera-controls/'+m[1], contentType:'application/javascript'}); });
  await p.route(/fonts\./, r=>r.fulfill({body:'', contentType:'text/css'}));
  await p.goto('http://127.0.0.1:8765/index.html?q=2');
  await p.waitForFunction(()=>window.__ready, null, {timeout:240000});
  await p.waitForTimeout(3000);
  const state = ()=>p.evaluate(()=>({mode:document.body.classList.contains('focus') ? 'focus' : 'tray', hero:!!window.__yoko.hero, sheet:document.getElementById('sheet').classList.contains('open'),
    hidden:window.__yoko.pieces.filter(x=>x.hidden).length, labelsOn:document.querySelectorAll('.lbl.on:not(#tip)').length}));
  const ok = (name, cond, s)=>console.log((cond ? 'PASS ' : 'FAIL ') + name + ' ' + JSON.stringify(s));
  const until = (fn, arg)=>p.waitForFunction(fn, arg, {timeout:240000, polling:500}).catch(()=>null);
  const settled = ()=>until(()=>{ const r = document.getElementById('sheet').getBoundingClientRect(); return r.bottom <= innerHeight + 1 || !document.getElementById('sheet').classList.contains('open'); });
  const tray = ()=>until(()=>!window.__yoko.hero && window.__yoko.pieces.every(x=>!x.hidden) && !document.body.classList.contains('focus'));
  // find a piece on screen: project piece 0 and click it like a user
  const at = await p.evaluate(()=>{ const pc = window.__yoko.pieces[0], v = {x:pc.x, y:pc.y + 0.5, z:pc.z};
    const cam = window.__yoko.cc._camera; const THREE_V = cam.position.constructor; const w = new THREE_V(v.x, v.y, v.z).project(cam);
    return {x:(w.x*.5+.5)*innerWidth, y:(-w.y*.5+.5)*innerHeight}; });
  await p.mouse.click(at.x, at.y); await until(()=>!!window.__yoko.hero);
  let s = await state(); ok('click a roll opens it', s.mode === 'focus' && s.hero && s.sheet, s);
  // change of mind straight away: back before the flight ends
  await settled(); await p.click('#btnBack'); await tray();
  s = await state(); ok('back returns the piece to the tray', s.mode === 'tray' && !s.hero && s.hidden === 0 && !s.sheet, s);
  // open, take apart, chips, arrows, escape
  await p.evaluate(()=>window.__yoko.focusPiece(7)); await settled();
  await p.click('#btnExplode'); await until(()=>document.querySelectorAll('.lbl.on:not(#tip)').length >= 3);
  s = await state(); ok('take apart shows labels', s.labelsOn >= 3, s);
  await p.click('#chips .chip:nth-child(2)'); await until(()=>document.querySelectorAll('.lbl.on:not(#tip)').length === 1);
  s = await state(); const pressed = await p.$$eval('#chips .chip[aria-pressed="true"]', x=>x.length); ok('chip isolates one ingredient', s.labelsOn === 1 && pressed === 1, s);
  const name1 = await p.textContent('#heroName'); await p.click('#btnNext'); await until(n=>document.getElementById('heroName').textContent !== n, name1);
  const name2 = await p.textContent('#heroName'); ok('next arrow steps ingredient', name2 !== name1, {name1, name2});
  await p.keyboard.press('Escape'); await until(()=>document.querySelectorAll('.lbl.on:not(#tip)').length >= 3);
  s = await state(); ok('escape leaves single ingredient', s.labelsOn >= 3, s);
  await p.click('#btnExplode'); await until(()=>document.querySelectorAll('.lbl.on:not(#tip)').length === 0);
  const before = await p.textContent('#heroName');
  await p.click('#btnNext'); await until(n=>document.getElementById('heroName').textContent !== n, before);
  const after = await p.textContent('#heroName'); ok('next arrow swaps roll type', before !== after, {before, after});
  await p.keyboard.press('Escape'); await tray();
  s = await state(); ok('escape returns to tray', s.mode === 'tray' && !s.hero && s.hidden === 0, s);
  // switch trays straight after closing, and while the drop-in plays
  await p.evaluate(()=>window.__yoko.focusPiece(3)); await p.waitForTimeout(800);
  await p.evaluate(()=>window.__yoko.backToTray()); await p.waitForTimeout(200);
  await p.click('button[data-t=promoL]'); await p.waitForTimeout(300);
  await p.click('button[data-t=promoXL]'); await p.waitForTimeout(300);
  await p.click('button[data-t=party]'); await tray();
  s = await state(); ok('rapid tray switching settles', s.mode === 'tray' && s.hidden === 0, s);
  // garnish tap
  await p.evaluate(()=>window.__yoko.focusGarnish(window.__yoko.garnish.children[0])); await settled();
  const g = await p.textContent('#heroName'); ok('garnish opens its card', !!g, {g});
  await p.click('#btnNext'); await until(n=>document.getElementById('heroName').textContent !== n, g);
  const g2 = await p.textContent('#heroName'); ok('garnish arrows step', g2 !== g, {g, g2});
  await p.click('#btnBack'); await tray();
  // draw calls in the tray view
  console.log('tray view render stats (all passes):', JSON.stringify(await p.evaluate(()=>window.__yoko.info())));
  console.log('errors:', errs.length); errs.forEach(e=>console.log(e));
  await b.close();
})();
