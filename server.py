#!/usr/bin/env python3
import base64, hashlib, hmac, json, os, secrets, sqlite3, time
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
HOST='127.0.0.1'; PORT=int(os.getenv('OPENMEDIA_PORT','8080')); DB=DATA/'openmedia.db'; VAULT=DATA/'provider-secrets.json'; KEY=DATA/'.vault-key'; TTL=600

def db():
    con=sqlite3.connect(DB,timeout=10);con.row_factory=sqlite3.Row
    con.executescript('''
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY,payload TEXT NOT NULL,created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS libraries(name TEXT PRIMARY KEY,created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY,payload TEXT NOT NULL,library TEXT DEFAULT '',favorite INTEGER DEFAULT 0,updated REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS progress(id TEXT PRIMARY KEY,position REAL NOT NULL,duration REAL NOT NULL,updated REAL NOT NULL);
    ''');return con

def init_db():
    with db() as con:con.execute('DELETE FROM cache WHERE created<?',(time.time()-86400*30,))

def vault_key():
    if not KEY.exists():
        KEY.write_bytes(secrets.token_bytes(32))
        try:os.chmod(KEY,0o600)
        except OSError:pass
    return KEY.read_bytes()
def stream(key,nonce,n):
    out=b'';counter=0
    while len(out)<n:
        out+=hmac.new(key,nonce+counter.to_bytes(8,'big'),hashlib.sha256).digest();counter+=1
    return out[:n]
def protect(obj):
    raw=json.dumps(obj).encode();key=vault_key();nonce=secrets.token_bytes(16);cipher=bytes(a^b for a,b in zip(raw,stream(key,nonce,len(raw))));tag=hmac.new(key,nonce+cipher,hashlib.sha256).digest();return base64.urlsafe_b64encode(nonce+tag+cipher).decode()
def unprotect(token):
    try:
        blob=base64.urlsafe_b64decode(token);nonce,tag,cipher=blob[:16],blob[16:48],blob[48:];key=vault_key()
        if not hmac.compare_digest(tag,hmac.new(key,nonce+cipher,hashlib.sha256).digest()):return {}
        return json.loads(bytes(a^b for a,b in zip(cipher,stream(key,nonce,len(cipher)))))
    except Exception:return {}
def read_secrets():
    return unprotect(VAULT.read_text()) if VAULT.exists() else {}
def write_secrets(values):
    current=read_secrets();current.update({k:v for k,v in values.items() if isinstance(v,str) and v.strip()});VAULT.write_text(protect(current))
    try:os.chmod(VAULT,0o600)
    except OSError:pass
    return current
def secret(env):return os.getenv(env,'') or read_secrets().get(env,'')

def fetch_json(url,headers=None,retries=3):
    last=None
    for attempt in range(retries):
        try:
            req=Request(url,headers={'User-Agent':'OpenMedia-Lite/1.3',**(headers or {})})
            with urlopen(req,timeout=15) as res:return json.loads(res.read().decode())
        except (HTTPError,URLError,TimeoutError) as e:
            last=e
            if isinstance(e,HTTPError) and e.code<500 and e.code!=429:break
            time.sleep(.35*(2**attempt))
    raise last

def cached(key,fn):
    with db() as con:
        row=con.execute('SELECT payload,created FROM cache WHERE key=?',(key,)).fetchone()
        if row and time.time()-row['created']<TTL:return json.loads(row['payload']),True
    value=fn()
    with db() as con:con.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?)',(key,json.dumps(value),time.time()))
    return value,False

def result(provider,ident,title,kind,thumb,url,embed='',duration=None,published=None,description=''):
    return {'id':f'{provider}:{kind}:{ident}','provider':provider,'type':kind,'title':title or 'Untitled','thumbnail':thumb or '','sourceUrl':url or '','embedUrl':embed or '','duration':duration,'publishedAt':published,'description':description or ''}
def published_after(key):
    days={'today':1,'week':7,'month':30,'year':365}.get(key);return (datetime.now(timezone.utc)-timedelta(days=days)).isoformat().replace('+00:00','Z') if days else None

def youtube_search(q,kind,limit,duration,published,order):
    key=secret('YOUTUBE_API_KEY')
    if not key:return [],['YouTube needs setup']
    params={'part':'snippet','type':kind,'maxResults':limit,'q':q,'order':order if order in ('date','title') else 'relevance','key':key}
    if kind=='video' and duration!='any':params['videoDuration']=duration
    after=published_after(published)
    if after:params['publishedAfter']=after
    data=fetch_json('https://www.googleapis.com/youtube/v3/search?'+urlencode(params));out=[]
    for x in data.get('items',[]):
        s=x.get('snippet',{});ident=x.get('id',{}).get({'video':'videoId','channel':'channelId','playlist':'playlistId'}[kind]);thumb=s.get('thumbnails',{}).get('medium',{}).get('url','')
        if not ident:continue
        if kind=='video':out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/watch?v={ident}',f'https://www.youtube-nocookie.com/embed/{ident}?autoplay=1',published=s.get('publishedAt'),description=s.get('description')))
        elif kind=='channel':out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/channel/{ident}',published=s.get('publishedAt'),description=s.get('description')))
        else:out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/playlist?list={ident}',published=s.get('publishedAt'),description=s.get('description')))
    return out,[]
def youtube_playlist(pid,limit=50):
    key=secret('YOUTUBE_API_KEY')
    if not key:return [],['YouTube needs setup']
    data=fetch_json('https://www.googleapis.com/youtube/v3/playlistItems?'+urlencode({'part':'snippet,contentDetails','playlistId':pid,'maxResults':min(limit,50),'key':key}));out=[]
    for x in data.get('items',[]):
        s=x.get('snippet',{});ident=x.get('contentDetails',{}).get('videoId') or s.get('resourceId',{}).get('videoId')
        if ident:out.append(result('YouTube',ident,s.get('title'),'video',s.get('thumbnails',{}).get('medium',{}).get('url',''),f'https://www.youtube.com/watch?v={ident}',f'https://www.youtube-nocookie.com/embed/{ident}?autoplay=1',published=s.get('publishedAt'),description=s.get('description')))
    return out,[]
def vimeo(q,limit,order):
    token=secret('VIMEO_ACCESS_TOKEN')
    if not token:return [],['Vimeo needs setup']
    data=fetch_json('https://api.vimeo.com/videos?'+urlencode({'query':q,'per_page':limit,'sort':'date' if order=='date' else 'relevant','direction':'desc'}),{'Authorization':f'Bearer {token}','Accept':'application/vnd.vimeo.*+json;version=3.4'});out=[]
    for x in data.get('data',[]):
        ident=(x.get('uri') or '').split('/')[-1];pics=x.get('pictures',{}).get('sizes',[])
        if ident:out.append(result('Vimeo',ident,x.get('name'),'video',pics[-1].get('link') if pics else '',x.get('link'),f'https://player.vimeo.com/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time'),x.get('description')))
    return out,[]
def dailymotion(q,limit):
    token=secret('DAILYMOTION_ACCESS_TOKEN')
    if not token:return [],['Dailymotion needs setup']
    fields='id,title,description,thumbnail_360_url,url,duration,created_time';data=fetch_json('https://api.dailymotion.com/videos?'+urlencode({'search':q,'limit':limit,'fields':fields}),{'Authorization':f'Bearer {token}'});out=[]
    for x in data.get('list',[]):
        ident=x.get('id')
        if ident:out.append(result('Dailymotion',ident,x.get('title'),'video',x.get('thumbnail_360_url'),x.get('url') or f'https://www.dailymotion.com/video/{ident}',f'https://www.dailymotion.com/embed/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time'),x.get('description')))
    return out,[]
def peertube(q,limit,order):
    base=(secret('PEERTUBE_INSTANCE') or 'https://sepiasearch.org').rstrip('/');sort={'date':'-publishedAt','title':'name'}.get(order,'-match');data=fetch_json(base+'/api/v1/search/videos?'+urlencode({'search':q,'count':limit,'sort':sort}));out=[]
    for x in data.get('data',[]):
        ident=x.get('uuid') or x.get('shortUUID') or x.get('id');host=x.get('account',{}).get('host') or urlparse(base).netloc;thumb=x.get('thumbnailPath') or ''
        if thumb.startswith('/'):thumb=f'https://{host}{thumb}'
        if ident:out.append(result('PeerTube',str(ident),x.get('name'),'video',thumb,x.get('url') or f'https://{host}/w/{ident}',f'https://{host}/videos/embed/{ident}?autoplay=1',x.get('duration'),x.get('publishedAt'),x.get('description')))
    return out,[]
def duration_ok(seconds,key):
    if key=='any' or seconds is None:return True
    return seconds<240 if key=='short' else 240<=seconds<=1200 if key=='medium' else seconds>1200

def search(params):
    q=params.get('q',[''])[0].strip();provider=params.get('provider',['all'])[0];kind=params.get('type',['video'])[0];duration=params.get('duration',['any'])[0];published=params.get('published',['any'])[0];order=params.get('order',['relevance'])[0]
    if not q:raise ValueError('Search query is required')
    names=['youtube','vimeo','dailymotion','peertube'] if provider=='all' else [provider];out=[];warnings=[]
    for name in names:
        if kind!='video' and name!='youtube':continue
        try:
            if name=='youtube':found,w=youtube_search(q,kind,12,duration,published,order)
            elif name=='vimeo':found,w=vimeo(q,12,order)
            elif name=='dailymotion':found,w=dailymotion(q,12)
            elif name=='peertube':found,w=peertube(q,12,order)
            else:continue
            out.extend(x for x in found if kind!='video' or duration_ok(x.get('duration'),duration));warnings+=w
        except (HTTPError,URLError,TimeoutError,ValueError):warnings.append(f'{name.title()} request failed after retries')
    if order=='title':out.sort(key=lambda x:(x.get('title') or '').lower())
    elif order=='date':out.sort(key=lambda x:x.get('publishedAt') or '',reverse=True)
    return {'query':q,'results':out,'warnings':warnings}

def saved_state():
    with db() as con:
        libs=[r['name'] for r in con.execute('SELECT name FROM libraries ORDER BY created')]
        items=[]
        for r in con.execute('SELECT payload,library,favorite FROM items ORDER BY updated DESC'):
            x=json.loads(r['payload']);x['library']=r['library'];x['favorite']=bool(r['favorite']);items.append(x)
        progress={r['id']:{'position':r['position'],'duration':r['duration'],'updated':r['updated']} for r in con.execute('SELECT * FROM progress')}
    return {'libraries':libs,'items':items,'progress':progress}
def save_state(payload):
    libs=payload.get('libraries',[]);items=payload.get('items',[])
    with db() as con:
        for name in libs:
            if isinstance(name,str) and name.strip():con.execute('INSERT OR IGNORE INTO libraries VALUES(?,?)',(name.strip(),time.time()))
        for x in items:
            ident=x.get('id')
            if ident and x.get('source')!='Local file':con.execute('INSERT OR REPLACE INTO items VALUES(?,?,?,?,?)',(ident,json.dumps(x),x.get('library',''),int(bool(x.get('favorite'))),time.time()))
def provider_status():
    configured={'youtube':bool(secret('YOUTUBE_API_KEY')),'vimeo':bool(secret('VIMEO_ACCESS_TOKEN')),'dailymotion':bool(secret('DAILYMOTION_ACCESS_TOKEN')),'peertube':True}
    with db() as con:entries=con.execute('SELECT COUNT(*) FROM cache').fetchone()[0]
    return {'version':'1.3.0','firstRun':not VAULT.exists() and not any(configured[k] for k in ('youtube','vimeo','dailymotion')),'storage':{'database':'Ready','savedItems':len(saved_state()['items'])},'cache':{'entries':entries,'ttlSeconds':TTL,'persistent':True},'providers':{k:{'ready':v} for k,v in configured.items()}}

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        rel=urlparse(path).path.lstrip('/') or 'index.html';candidate=(ROOT/rel).resolve();return str(candidate if str(candidate).startswith(str(ROOT)) else ROOT/'index.html')
    def send_json(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
    def body(self):
        try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0')) or 0) or b'{}')
        except Exception:return {}
    def do_GET(self):
        u=urlparse(self.path);p=parse_qs(u.query)
        if u.path=='/api/health':return self.send_json(provider_status())
        if u.path=='/api/state':return self.send_json(saved_state())
        if u.path=='/api/search':
            try:
                data,hit=cached('search:'+u.query,lambda:search(p));return self.send_json({**data,'cacheHit':hit})
            except ValueError as e:return self.send_json({'error':str(e)},400)
        if u.path=='/api/playlist':
            pid=(p.get('id') or [''])[0]
            if not pid:return self.send_json({'error':'Playlist id is required'},400)
            try:
                (res,w),hit=cached('playlist:'+pid,lambda:youtube_playlist(pid));return self.send_json({'results':res,'warnings':w,'cacheHit':hit})
            except (HTTPError,URLError,TimeoutError,ValueError):return self.send_json({'error':'Playlist request failed after retries'},502)
        return super().do_GET()
    def do_POST(self):
        u=urlparse(self.path);data=self.body()
        if u.path=='/api/state':save_state(data);return self.send_json({'saved':True})
        if u.path=='/api/progress':
            if not data.get('id'):return self.send_json({'error':'Media id is required'},400)
            with db() as con:con.execute('INSERT OR REPLACE INTO progress VALUES(?,?,?,?)',(data['id'],float(data.get('position',0)),float(data.get('duration',0)),time.time()))
            return self.send_json({'saved':True})
        if u.path=='/api/settings':
            allowed={k:data.get(k,'') for k in ('YOUTUBE_API_KEY','VIMEO_ACCESS_TOKEN','DAILYMOTION_ACCESS_TOKEN','PEERTUBE_INSTANCE')};write_secrets(allowed);return self.send_json({'saved':True,'health':provider_status()})
        return self.send_json({'error':'Not found'},404)
    def log_message(self,fmt,*args):print('[OpenMedia]',fmt%args)
if __name__=='__main__':
    init_db();os.chdir(ROOT);print(f'OpenMedia Lite v1.3.0 running at http://{HOST}:{PORT}')
    try:ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
    except KeyboardInterrupt:pass
