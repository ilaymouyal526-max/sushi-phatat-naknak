const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const m of process.argv.slice(2)){await p.goto('file://'+__dirname+'/mock.html?m='+m);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
await p.screenshot({path:__dirname+'/out/'+m+'.png'});console.log(m);}
await b.close();})();
