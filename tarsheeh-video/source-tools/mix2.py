import json,subprocess,sys
V,VOD,MAP,DING,MUSIC,OUT=sys.argv[1:7]; MAP=json.loads(MAP); DING=json.loads(DING)
d=json.load(open(f'{V}/events.json')); sc=[s for s in d['sc'] if s['e']-s['s']>0.01]; keys={s['k'] for s in sc}; DUR=sc[-1]['e']
inputs=[]; chains=[]
def add(path,t,vol,lab):
    i=len(inputs); inputs.append(path); ms=max(0,int(t*1000))
    chains.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[{lab}{i}]'); return f'[{lab}{i}]'
X='/tmp/claude-0/-home-user-yousef/a1a6bc2a-682e-5890-b870-35db6ace3693/scratchpad/v2/sfx'
vo=[add(f'{VOD}/{MAP[s["k"]]}_f.wav',s['s']+0.05,1.0,'v') for s in sc]
fx=[]
for s in sc[1:]:
    if s is sc[-1]: fx.append(add(f'{X}/riser.mp3',s['s']-1.1,0.45,'f'))
    else: fx.append(add(f'{X}/whoosh.mp3',s['s']-0.12,0.42,'f'))
last=-9
for e in sorted([e for e in d['ev'] if e['k'] in keys],key=lambda e:e['t']):
    m={'stamp':('stamp',0.55),'punch':('pop',0.38),'drop':('paper',0.45),'card':('paper',0.35),'pop':('pop',0.3),'slam':('stamp',0.4),'slideR':('pop',0.25),'slideL':('pop',0.25)}.get(e['a'])
    if not m or e['t']-last<0.15 or e['t']<0.05 or e['t']>DUR: continue
    last=e['t']; fx.append(add(f'{X}/{m[0]}.mp3',e['t'],m[1],'f'))
for k,off,name,vol in DING:
    s=[x for x in sc if x['k']==k][0]; fx.append(add(f'{X}/{name}.mp3',s['s']+off,vol,'f'))
mi=len(inputs); inputs.append(MUSIC)
fc=';'.join(chains)
fc+=f';{"".join(vo)}amix=inputs={len(vo)}:normalize=0,apad=whole_dur={DUR},asplit=2[vo][sc]'
fc+=f';{"".join(fx)}amix=inputs={len(fx)}:normalize=0,apad=whole_dur={DUR}[fx]'
fc+=f';[{mi}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{DUR},volume=0.42,afade=t=in:d=0.2,afade=t=out:st={DUR-1.4}:d=1.4[mu]'
fc+=';[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mud]'
fc+=f';[vo][fx][mud]amix=inputs=3:normalize=0:duration=longest,atrim=0:{DUR},loudnorm=I=-14:TP=-1.0:LRA=11[out]'
cmd=['ffmpeg','-v','error','-y']
for p in inputs: cmd+=['-i',p]
cmd+=['-filter_complex',fc,'-map','[out]','-ar','48000','-c:a','pcm_s16le',OUT]
r=subprocess.run(cmd,capture_output=True,text=True); print(r.stderr[-800:] or f'mix ok {DUR}')
