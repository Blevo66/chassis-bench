const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}); const p=await b.newPage({viewport:{width:1600,height:1000}});
p.on('console',m=>console.log(m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/page.html'); const D=JSON.parse(fs.readFileSync('data.json'));
const views=[
 ['render-rear-three-quarter.png',{w:1600,h:1000,arm:-12,cam:[-2400,-1700,1000],look:[-380,0,120],fov:30}],
 ['render-side-full-bump.png',{w:1600,h:1000,arm:2.9,cam:[-380,-2600,330],look:[-380,0,250],fov:30}],
 ['render-parts.png',{w:1600,h:1000,arm:-15,split:true,cam:[-1500,900,1300],look:[-480,0,330],fov:24}],
];
for(const [n,o] of views){const u=await p.evaluate(([D,o])=>window.renderView(D,o),[D,o]); fs.writeFileSync(n,Buffer.from(u.split(',')[1],'base64')); console.log(n);}
await b.close();})();
