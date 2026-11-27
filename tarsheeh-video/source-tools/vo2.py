import json,subprocess,sys,urllib.request,uuid
out=sys.argv[1]; tempo=sys.argv[2]; voice='zhVs7gPm7IjLzqtwu2gb'
L=json.loads(open(sys.argv[3]).read())
def stt(path):
  b=uuid.uuid4().hex; f=open(path,'rb').read()
  body=(f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n--{b}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\nar\r\n--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+f+f'\r\n--{b}--\r\n'.encode()
  r=urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text',data=body,headers={'xi-api-key':'proxy-injected','Content-Type':f'multipart/form-data; boundary={b}'})
  j=json.load(urllib.request.urlopen(r,timeout=120)); return j['text'],[(x['text'],round(x['start'],2)) for x in j['words'] if x['type']=='word']
res={}
for i,(k,t) in enumerate(L):
  body={'text':t,'model_id':'eleven_multilingual_v2','voice_settings':{'stability':0.4,'similarity_boost':0.85,'style':0.4,'use_speaker_boost':True,'speed':1.08},
        'previous_text':L[i-1][1] if i>0 else None,'next_text':L[i+1][1] if i+1<len(L) else None}
  req=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_192',data=json.dumps(body).encode(),headers={'xi-api-key':'proxy-injected','Content-Type':'application/json'})
  open(f'{out}/{k}.mp3','wb').write(urllib.request.urlopen(req,timeout=120).read())
  subprocess.run(['ffmpeg','-v','error','-y','-i',f'{out}/{k}.mp3','-af',f'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tempo}','-ar','44100',f'{out}/{k}_f.wav'])
  d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{out}/{k}_f.wav'],capture_output=True,text=True).stdout)
  txt,w=stt(f'{out}/{k}_f.wav'); res[k]={'d':round(d,2),'w':w}; print(k,round(d,2),txt,w,flush=True)
json.dump(res,open(f'{out}/words_{sys.argv[4]}.json','w'),ensure_ascii=False)
