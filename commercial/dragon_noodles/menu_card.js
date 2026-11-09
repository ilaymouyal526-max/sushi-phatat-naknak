// Render the House Wok Noodles slide of the dish screen (menu-screen/ on branch ccr-53cee3cd-iiiipd) as the 1080x1920 end card.
// Usage: node menu_card.js <menu-screen dir> <out.png> [seconds into the slide, default 2.5]
const path=require("path"); const {chromium}=require("playwright");
const [DIR,OUT,T]=[process.argv[2],process.argv[3],Number(process.argv[4]||2.5)];
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto("file://"+path.join(DIR,"index.html")+"?render=1");
  await p.evaluate(()=>document.fonts.ready);
  const i=await p.evaluate(()=>[...document.querySelectorAll('#slides .slide')].findIndex(s=>s.innerHTML.includes('House Wok Noodles')));
  await p.evaluate(i=>window.go(i),i);
  await p.evaluate(()=>Promise.all([...document.querySelectorAll('.ph')].map(e=>{const im=new Image();im.src=getComputedStyle(e).backgroundImage.slice(5,-2);return im.complete?0:new Promise(r=>{im.onload=im.onerror=r;});})));
  await p.evaluate(t=>{document.body.offsetHeight;for(const a of document.getAnimations()){a.pause();a.currentTime=t*1000;}},T);
  await p.screenshot({path:OUT}); await b.close(); console.log("slide",i);
})();
