import json,subprocess,sys,re,unicodedata
cfg=json.load(open(sys.argv[1])); S=cfg['S']
W=json.load(open(cfg['words'])); src=cfg['wav']; OUTD=cfg['outdir']; tempo=cfg['tempo']; GAP=cfg.get('maxgap',0.32)
norm=lambda s:re.sub(r'[ً-ْـ.,،:؟!?]','',s)
# segment
starts=[]; i=0
for sc,first in cfg['segments']:
    alts=first.split('|')
    while not any(norm(W[i]['t']).startswith(a) for a in alts): i+=1
    starts.append((sc,i)); i+=1
segs=[]
for n,(sc,i0) in enumerate(starts):
    i1=starts[n+1][1] if n+1<len(starts) else len(W)
    segs.append((sc,W[i0:i1]))
res={}
for sc,ws in segs:
    # build pieces with compressed gaps
    pieces=[]; t=0; newt=[]
    a=max(0,ws[0]['s']-0.06)
    for k,w in enumerate(ws):
        if k>0:
            gap=w['s']-ws[k-1]['e']
            if gap>GAP:
                pieces.append((a,ws[k-1]['e']+GAP/2)); a=w['s']-GAP/2
    end=ws[-1]['e']+0.12; pieces.append((a,end))
    # map times
    def mp(x):
        acc=0
        for p0,p1 in pieces:
            if x<p1: return (acc+max(0,x-p0))/tempo
            acc+=p1-p0
        return acc/tempo
    fl='+'.join([f"between(t,{p0:.3f},{p1:.3f})" for p0,p1 in pieces])
    out=f"{OUTD}/{sc}_f.wav"
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-af',f"aselect='{fl}',asetpts=N/SR/TB,atempo={tempo},afade=t=in:d=0.01,areverse,afade=t=in:d=0.03,areverse",'-ar','44100',out])
    d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout)
    res[sc]={'d':d,'w':[(norm(w['t']),round(mp(w['s']),3)) for w in ws]}
# cues -> html
html=open(cfg['html']).read()
def cue(sc,c):
    if isinstance(c,(int,float)): return c
    m=re.match(r'([^+#]+)(?:#(\d+))?(?:\+([\d.]+))?$',c); words,nth,off=m.group(1).split('|'),int(m.group(2) or 1),float(m.group(3) or 0)
    cnt=0
    for w,t in res[sc]['w']:
        if any(w.startswith(x) for x in words):
            cnt+=1
            if cnt==nth: return round(max(0,t-0.04)+off,2)
    raise Exception(f'cue {sc} {c} not found in {res[sc]["w"]}')
parts=re.split(r'(?=<div class="sc[ "])',html); out=[]
for p in parts:
    m=re.match(r'<div class="sc[^"]*" data-k="(\w+)"',p)
    if m and m.group(1) in cfg['cues']:
        k=m.group(1); C=[cue(k,c) for c in cfg['cues'][k]]; n=len(re.findall(r'data-t="[^"]*"',p)); assert n==len(C),(k,n,len(C)); it=iter(C)
        p=re.sub(r'data-t="[^"]*"',lambda _:f'data-t="{next(it)}"',p)
        if k in cfg.get('outs',{}):
            ov=cue(k,cfg['outs'][k]); p=re.sub(r'data-o="[^"]*"',f'data-o="{ov}"',p)
    out.append(p)
html=''.join(out)
T={}
for sc in cfg['allscenes']:
    T[sc]=round(res[sc]['d']+cfg['pad'].get(sc,cfg['pad']['_']),2) if sc in res else 0
for k,(pat,sc,c) in cfg.get('counters',{}).items():
    html=re.sub(pat,lambda m:m.group(0).split('-')[0]+'-'+f"{sc}.s-{cue(c[0],c[1])}"+')',html) if False else html
    html=re.sub(pat, f"(t-{sc}.s-{cue(c[0],c[1])})", html)
if cfg.get('timing_js'): open(cfg['timing_js'],'w').write('window.TIMING='+json.dumps(T)+';')
else: html=re.sub(r'window.TIMING=\{[^}]*\}','window.TIMING='+json.dumps(T),html,count=1)
open(cfg['html'],'w').write(html)
json.dump(res,open(f"{OUTD}/res.json",'w'),ensure_ascii=False)
print(T, round(sum(T.values()),2))
