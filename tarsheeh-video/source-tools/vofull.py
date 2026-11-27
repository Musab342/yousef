import json,urllib.request,uuid,sys,subprocess
D,name,text=sys.argv[1],sys.argv[2],sys.argv[3]; voice='5HAezIQAaoSgJypcI0NP'
body={'text':text,'model_id':'eleven_v3','voice_settings':{'stability':0.5,'similarity_boost':0.8}}
r=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_192',data=json.dumps(body).encode(),headers={'xi-api-key':'proxy-injected','Content-Type':'application/json'})
open(f'{D}/{name}.mp3','wb').write(urllib.request.urlopen(r,timeout=300).read())
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{D}/{name}.mp3','-ar','44100','-ac','1',f'{D}/{name}.wav'])
b=uuid.uuid4().hex; f=open(f'{D}/{name}.wav','rb').read()
bd=(f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n--{b}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\nar\r\n--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+f+f'\r\n--{b}--\r\n'.encode()
j=json.load(urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text',data=bd,headers={'xi-api-key':'proxy-injected','Content-Type':f'multipart/form-data; boundary={b}'}),timeout=300))
w=[{'t':x['text'],'s':x['start'],'e':x['end']} for x in j['words'] if x['type']=='word']
json.dump(w,open(f'{D}/{name}.json','w'),ensure_ascii=False)
print(name, subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{D}/{name}.wav'],capture_output=True,text=True).stdout.strip(), j['text'])
print([(x['t'],round(x['s'],2)) for x in w])
