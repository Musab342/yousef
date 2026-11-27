const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]+'/index.html?cap=1');
const r=await p.evaluate(()=>{const ev=[];const sc=SCENES;document.querySelectorAll('.sc').forEach((el,i)=>{const s=sc[i];
 el.querySelectorAll('.el').forEach(e=>ev.push({k:s.k,a:e.dataset.a,t:s.s+parseFloat(e.dataset.t||0)}));});return {sc,ev};});
console.log(JSON.stringify(r));await b.close();})();
