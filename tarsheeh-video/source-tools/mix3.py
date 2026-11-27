import json,subprocess,sys
V,VOD,OUT,CASH=sys.argv[1:5]; CASH=json.loads(CASH)
X='/tmp/claude-0/-home-user-yousef/a1a6bc2a-682e-5890-b870-35db6ace3693/scratchpad/sfx2'
d=json.load(open(f'{V}/events.json')); sc=[s for s in d['sc'] if s['e']-s['s']>0.01]; keys={s['k'] for s in sc}; DUR=sc[-1]['e']
html=open(f'{V}/index.html').read()
inputs=[];chains=[]
def add(path,t,vol,lab):
    i=len(inputs); inputs.append(path); ms=max(0,int(t*1000))
    chains.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[{lab}{i}]'); return f'[{lab}{i}]'
vo=[add(f'{VOD}/{s["k"]}_f.wav',s['s']+0.05,1.0,'v') for s in sc]
fx=[]
for s in sc[1:]:
    if s is sc[-1]: fx.append(add(f'{X}/riser.mp3',s['s']-1.15,0.35,'f')); fx.append(add(f'{X}/boom.mp3',s['s'],0.4,'f'))
    else: fx.append(add(f'{X}/whoosh.mp3',s['s']-0.18,0.45,'f'))
M={'blurin':[('click',0.16)],'punch':[('boom',0.3)],'pop':[('pop',0.25)],'slam':[('boom',0.28),('swipe',0.3)],'stamp':[('pop',0.35),('click',0.2)],
   'slideR':[('swipe',0.3)],'slideL':[('swipe',0.3)],'card':[('swipe',0.28)],'stretch':[('reverse',0.3)],'drop':[('swipe',0.32)],'line':[('swipe',0.22)],'up':[('click',0.14)],'spinin':[('pop',0.2)],'wipe':[('swipe',0.18)]}
last={}
for e in sorted([e for e in d['ev'] if e['k'] in keys],key=lambda e:e['t']):
    sd=[s for s in sc if s['k']==e['k']][0]
    if e['t']>=sd['e'] or e['t']<0.03: continue
    a=e['a']
    lst=M.get(a,[])
    if a=='pop' and e['k']=='a2': lst=[('notif',0.3)]
    for name,vol in lst:
        if e['t']-last.get(name,-9)<0.17: continue
        last[name]=e['t']; fx.append(add(f'{X}/{name}.mp3',e['t'],vol,'f'))
for k,off in CASH:
    s=[x for x in sc if x['k']==k][0]; fx.append(add(f'{X}/cash.mp3',s['s']+off,0.45,'f'))
fc=';'.join(chains)
fc+=f';{"".join(vo)}amix=inputs={len(vo)}:normalize=0,apad=whole_dur={DUR},highpass=f=70,acompressor=threshold=0.1:ratio=3:attack=5:release=120,equalizer=f=3500:t=q:w=1:g=2[vo]'
fc+=f';{"".join(fx)}amix=inputs={len(fx)}:normalize=0,apad=whole_dur={DUR},volume=0.3,alimiter=limit=0.35[fx]'
fc+=f';[vo][fx]amix=inputs=2:normalize=0:duration=longest,atrim=0:{DUR},loudnorm=I=-13:TP=-1.0:LRA=8[out]'
cmd=['ffmpeg','-v','error','-y']
for p in inputs: cmd+=['-i',p]
cmd+=['-filter_complex',fc,'-map','[out]','-ar','48000','-c:a','pcm_s16le',OUT]
r=subprocess.run(cmd,capture_output=True,text=True); print(r.stderr[-600:] or f'mix ok {DUR} fx={len(fx)}')
