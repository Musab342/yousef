const {chromium}=require('playwright');
(async()=>{
 const [dir,mode,out]=process.argv.slice(2);
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:mode==='full'?2:1});
 p.on('console',m=>console.log('PAGE',m.text()));
 await p.goto('file://'+dir+'/index.html?cap=1');
 await p.evaluate(()=>document.fonts.ready);
 await p.waitForFunction(()=>[...document.querySelectorAll('video')].every(v=>v.readyState>=2));
 const st=await p.$('#stage');
 const sc=await p.evaluate(()=>SCENES), DUR=await p.evaluate(()=>DUR);
 console.log('DUR',DUR);
 if(mode==='still'){
  let i=0; for(const s of sc){ for(const f of [0.08,0.92]){ const t=s.s+(s.e-s.s)*f; await p.evaluate(t=>renderAt(t),t); await st.screenshot({path:`${out}/s${String(i++).padStart(2,'0')}.png`}); } }
 } else {
  const fps=30,N=Math.round(DUR*fps);
  for(let i=0;i<N;i++){await p.evaluate(t=>renderAt(t),i/fps);await st.screenshot({path:`${out}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});}
 }
 await b.close();
})();
