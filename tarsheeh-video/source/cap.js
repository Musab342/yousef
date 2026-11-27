const {chromium}=require('playwright');
(async()=>{
 const [dir,mode,out]=process.argv.slice(2);
 const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:mode==='full'?2:1});
 await p.goto('file://'+dir+'/index.html?cap=1');
 await p.evaluate(()=>document.fonts.ready);
 await p.waitForFunction(()=>document.getElementById('v').readyState>=2);
 const st=await p.$('#stage');
 if(mode==='still'){
  const ts=[1.2,3.2,4.9,6.6,8.4,10.6,13,16.6,19.3,20.9,22.8,25.9,28];
  for(let i=0;i<ts.length;i++){await p.evaluate(t=>renderAt(t),ts[i]);await st.screenshot({path:`${out}/s${String(i).padStart(2,'0')}.png`});}
 } else {
  const fps=30,N=Math.round(29*fps);
  for(let i=0;i<N;i++){await p.evaluate(t=>renderAt(t),i/fps);await st.screenshot({path:`${out}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
 }
 await b.close();
})();
