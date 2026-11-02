// Usage: node render_frames.js <outDir> [fps] [workers] [t1,t2,... for stills]
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const out = process.argv[2]; const fps = +(process.argv[3]||30); const workers = +(process.argv[4]||4);
const stills = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
fs.mkdirSync(out,{recursive:true});
const url = 'file://' + path.resolve(__dirname,'explainer.html');
(async()=>{
  const browser = await chromium.launch();
  const times = stills || Array.from({length: fps*30}, (_,i)=>i/fps);
  const chunks = Array.from({length:workers},()=>[]);
  times.forEach((t,i)=>chunks[i%workers].push([t,i]));
  await Promise.all(chunks.map(async chunk=>{
    const page = await browser.newPage({viewport:{width:1080,height:1920}});
    await page.goto(url); await page.evaluate(()=>document.fonts.ready);
    for(const [t,i] of chunk){
      await page.evaluate(t=>window.seek(t), t);
      await page.screenshot({path: path.join(out, stills?`still_${t}.png`:`f_${String(i).padStart(4,'0')}.png`)});
    }
  }));
  await browser.close();
})();
