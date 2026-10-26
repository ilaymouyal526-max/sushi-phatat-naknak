const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1000,height:1000}});
p.on('pageerror',e=>console.log('E',e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_'))console.log('C',m.text())});
await p.route(/cdn.jsdelivr.net\/npm\/three@0.169.0\/(.*)/,r=>{const m=r.request().url().match(/three@0.169.0\/(.*)/);r.fulfill({path:'node_modules/three/'+m[1],contentType:'application/javascript'})});
await p.route(/fonts/,r=>r.fulfill({body:'',contentType:'text/css'}));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(15000);
for(const spec of process.argv.slice(2)){ const [t,v]=spec.split(':');
  await p.evaluate(t=>document.querySelector(`button[data-t=${t}]`).click(),t); await p.waitForTimeout(3000);
  await p.evaluate(v=>document.querySelector(`button[data-v=${v}]`).click(),v); await p.waitForTimeout(4000);
  await p.screenshot({path:`s_${t}_${v}.png`,timeout:300000}); console.log('shot',t,v);}
await b.close();})();
