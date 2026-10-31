const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1600,height:1000}});
p.on('console',m=>console.log(m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/page.html'); await p.waitForFunction(()=>window.ready);
const views=JSON.parse(fs.readFileSync(process.argv[2]));
for(const [n,o] of views){const u=await p.evaluate(o=>window.renderView(o),o); fs.writeFileSync(n,Buffer.from(u.split(',')[1],'base64')); console.log(n);}
await b.close();})();
