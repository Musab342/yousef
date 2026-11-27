import json,subprocess,sys,urllib.request,uuid
D=sys.argv[1]; gate=sys.argv[2]
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{D}/iso.wav','-af',f"highpass=f=90,{gate}"+sys.argv[3],f'{D}/clean2.wav'])
W=json.load(open(f'{D}/words.json')); PRE,POST=0.08,0.15
pieces=[]; a=W[0]['s']-PRE
for k in range(1,len(W)):
    if W[k]['s']-W[k-1]['e']>PRE+POST+0.02:
        pieces.append((a,W[k-1]['e']+POST)); a=W[k]['s']-PRE
pieces.append((a,W[-1]['e']+0.35))
fl='+'.join(f'between(t,{p0:.3f},{p1:.3f})' for p0,p1 in pieces)
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{D}/clean2.wav','-af',f"aselect='{fl}',asetpts=N/SR/TB,afade=t=in:d=0.02,loudnorm=I=-14:TP=-1:LRA=7",'-ar','48000',f'{D}/voice_clean2.wav'])
b=uuid.uuid4().hex; f=open(f'{D}/voice_clean2.wav','rb').read()
body=(f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n--{b}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\nar\r\n--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+f+f'\r\n--{b}--\r\n'.encode()
j=json.load(urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text',data=body,headers={'xi-api-key':'proxy-injected','Content-Type':f'multipart/form-data; boundary={b}'}),timeout=300))
print(j['text'][-80:])
