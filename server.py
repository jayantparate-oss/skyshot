from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
import json,random,time,secrets,threading,os,re
host=os.environ.get('HOST_SECRET') or secrets.token_urlsafe(18); lock=threading.RLock(); state={'players':{},'status':'lobby','end':0,'used_text':set(),'used_options':set()}
diwali=[
 ('What is a traditional oil lamp used during Diwali called?', ['Diya','Kite','Drum','Umbrella'],0),
 ('Which colourful decoration is often made on the floor during Diwali?', ['Rangoli','Kite','Snowman','Lantern fish'],0),
 ('Diwali is widely known as the festival of what?', ['Colours','Lights','Rain','Harvest'],1),
 ('Which is a safer way to celebrate Diwali?', ['Burn crackers indoors','Keep water nearby and follow adult guidance','Touch a lit sparkler','Run towards fireworks'],1),
 ('Which sweet is commonly shared during Diwali?', ['Ladoo','Sandwich','Soup','Noodles'],0),
]
eng=[('Choose the correct sentence.', ['She have finished her homework.','She has finished her homework.','She finishing her homework.','She have finish her homework.'],1),('Choose the antonym of “ancient”.',['Old','Modern','Historic','Past'],1),('Choose the correct preposition: The book is ___ the table.',['on','at','by','from'],0),('Which word is an adjective in “The bright lamp glowed”?',['lamp','glowed','bright','the'],2),('Choose the correct past tense of “write”.',['writed','written','wrote','writes'],2),('Choose the correct pronoun: Riya and I went home. ___ were tired.',['She','We','He','It'],1),('Choose the adverb: The child spoke softly.',['child','spoke','softly','the'],2),('Choose the correct article: He is ___ honest person.',['a','an','the','no article'],1)]
sci=[('Which part of a plant absorbs water from the soil?',['Leaves','Roots','Flowers','Fruits'],1),('Which process allows green plants to make food?',['Respiration','Photosynthesis','Digestion','Transpiration'],1),('Which device measures temperature?',['Thermometer','Barometer','Compass','Balance'],0),('Which acid is present in an ant sting?',['Formic acid','Citric acid','Acetic acid','Lactic acid'],0),('What is the basic unit of speed?',['metre per second','kilogram','litre','degree Celsius'],0),('Which component of blood helps fight infection?',['Red blood cells','White blood cells','Platelets','Plasma only'],1),('What is the mode of heat transfer through direct contact?',['Conduction','Radiation','Reflection','Evaporation'],0),('Which of these is a physical change?',['Rusting iron','Burning paper','Melting ice','Cooking food'],2),('Which organ absorbs most digested food in humans?',['Small intestine','Stomach','Food pipe','Large intestine'],0),('Which type of mirror is used as a rear-view mirror?',['Plane','Convex','Concave','None'],1)]
# The bank is generated from the supplied PDF, including its answer key.
with open(os.path.join(os.path.dirname(__file__),'questions.json'), encoding='utf-8') as f:
 bank=json.load(f)
for i,(text,options,answer) in enumerate(eng):
 bank.append({'id':f'english:{i}','type':'english','text':text,'options':options,'answer':str(answer)})
def normal(s):
 s=s.casefold().strip()
 s=re.sub(r'^(in a classroom quiz,|choose the best answer:)\s*','',s)
 return re.sub(r'[^\w]+','',s)
def unused(q):
 return normal(q['text']) not in state['used_text'] and tuple(sorted(normal(o) for o in q.get('options',[]))) not in state['used_options']
def reserve(q):
 state['used_text'].add(normal(q['text']))
 if q.get('options'): state['used_options'].add(tuple(sorted(normal(o) for o in q['options'])))
 return q
def question(p):
 # The first five attempts are randomly selected Diwali questions.
 if p['attempts']>=5 and p['correct']>=6 and (time.time()-p['started'])/p['correct']<=20 and random.random()<.4:
  for _ in range(100):
   a=random.randint(2,9);x=random.randint(2,12);b=random.randint(1,12)
   q={'type':'equation','text':f'{a}x + {b} = {a*x+b}. What is x?','answer':str(x)}
   if normal(q['text']) not in state['used_text']: return reserve(q)
 candidates=[q for q in bank if (p['attempts']>=5 or q['type']=='diwali') and unused(q)]
 if not candidates: return None
 return reserve(random.choice(candidates).copy())

def update():
 if state['status']=='running' and time.time()>=state['end']: state['status']='finished'
def public(p):return {k:p[k] for k in ['id','name','status','score','correct','algebra']}
class H(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def sendj(self,o,code=200):
  b=json.dumps(o).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=='/music.mp3':
   path=os.path.join(os.path.dirname(__file__),'music.mp3')
   if not os.path.isfile(path):return self.send_error(404,'Music file not found')
   size=os.path.getsize(path); start=0; end=size-1; partial=False
   range_header=self.headers.get('Range')
   if range_header:
    match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header.strip())
    if not match or (not match.group(1) and not match.group(2)):
     self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
    if match.group(1):
     start=int(match.group(1));end=min(int(match.group(2)),size-1) if match.group(2) else size-1
    else:
     count=int(match.group(2));start=max(0,size-count)
    if start>=size or end<start:
     self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
    partial=True
   self.send_response(206 if partial else 200);self.send_header('Content-Type','audio/mpeg');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
   if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.end_headers()
   with open(path,'rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     chunk=f.read(min(65536,remaining))
     if not chunk:break
     self.wfile.write(chunk);remaining-=len(chunk)
   return
  if u.path in ('/','/index.html','/host','/host.html'):
   b=open('host.html' if u.path in ('/host','/host.html') else 'index.html','rb').read();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b);return
  if u.path!='/api/state':return self.send_error(404)
  q=parse_qs(u.query); token=q.get('token',[''])[0]
  with lock:
   update(); p=state['players'].get(token); data={'status':state['status'],'remaining':max(0,int(state['end']-time.time()+.999)),'exhausted':bool(p and p['status']=='approved' and state['status']=='running' and p['question'] is None),'players':[public(v) for v in state['players'].values() if v['status']!='rejected'],'me':public(p) if p else None,'isHost':q.get('host',[''])[0]==host}
   if p and p['status']=='approved' and state['status']=='running' and p['question']:data['question']={k:v for k,v in p['question'].items() if k!='answer'}
   self.sendj(data)
 def do_POST(self):
  try:
   d=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0')))); path=urlparse(self.path).path
   with lock:
    update()
    if path=='/api/join':
     name=str(d.get('name','')).strip()[:24]
     if not name:raise ValueError('Enter your name.')
     if state['status']!='lobby':raise ValueError('The competition has already started.')
     if sum(p['status']!='rejected' for p in state['players'].values())>=20:raise ValueError('The waiting list is full.')
     t=secrets.token_urlsafe(18);state['players'][t]={'id':secrets.token_urlsafe(12),'name':name,'status':'pending','score':0,'correct':0,'algebra':0,'question':None,'started':0,'attempts':0};return self.sendj({'token':t})
    if path in ['/api/approve','/api/reject','/api/start','/api/reset'] and d.get('host')!=host:return self.sendj({'error':'Host access required.'},403)
    if path in ['/api/approve','/api/reject']:
     if state['status']!='lobby':raise ValueError('The game has already started.')
     p=next((v for v in state['players'].values() if v['id']==d.get('id')),None)
     if not p:raise ValueError('Player not found.')
     if path.endswith('approve') and sum(v['status']=='approved' for v in state['players'].values())>=5:raise ValueError('Five players are already approved.')
     p['status']='approved' if path.endswith('approve') else 'rejected'
    elif path=='/api/start':
     if state['status']!='lobby':raise ValueError('Already started.')
     ps=[p for p in state['players'].values() if p['status']=='approved']
     if not ps:raise ValueError('Approve at least one player first.')
     state['end']=time.time()+max(30,min(600,int(d.get('duration',180))));state['status']='running'
     for p in ps:p['started']=time.time();p['question']=question(p)
    elif path=='/api/reset':state.update(players={},status='lobby',end=0,used_text=set(),used_options=set())
    elif path=='/api/answer':
     p=state['players'].get(d.get('token'))
     if not p or p['status']!='approved' or state['status']!='running' or not p['question']:raise ValueError('Cannot answer right now.')
     correct=str(d.get('answer','')).strip().lower()==p['question']['answer'].lower();typ=p['question']['type']
     p['attempts']+=1
     if correct:p['correct']+=1;p['score']+=3 if typ=='equation' else 1;p['algebra']+=int(typ=='equation')
     p['question']=question(p);return self.sendj({'correct':correct,'type':typ})
    else:return self.sendj({'error':'Not found'},404)
    self.sendj({'ok':True})
  except Exception as e:self.sendj({'error':str(e)},400)
print('HOST LINK: /?host='+host,flush=True)
ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8000'))),H).serve_forever()
