import sys,re,json
f,ratios=sys.argv[1],json.loads(sys.argv[2]); s=open(f).read()
parts=re.split(r'(?=<div class="sc )',s); out=[]
for p in parts:
  m=re.match(r'<div class="sc [^"]*" data-k="(\w+)"',p)
  if m and m.group(1) in ratios:
    r=ratios[m.group(1)]
    p=re.sub(r'data-(t|o)="([^"]*)"',lambda x:f'data-{x.group(1)}="{x.group(2) if float(x.group(2))>=90 else round(float(x.group(2))*r,2)}"',p)
  out.append(p)
open(f,'w').write(''.join(out))
