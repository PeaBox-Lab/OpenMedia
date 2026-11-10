#!/usr/bin/env python3
import json, os, time
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parent; HOST='127.0.0.1'; PORT=int(os.getenv('OPENMEDIA_PORT','8080')); CACHE={}; TTL=600

def fetch_json(url, headers=None):
    req=Request(url,headers={'User-Agent':'OpenMedia-Lite/1.2',**(headers or {})})
    with urlopen(req,timeout=15) as res:return json.loads(res.read().decode())
def cached(key, fn):
    hit=CACHE.get(key)
    if hit and time.time()-hit[0]<TTL:return hit[1],True
    value=fn(); CACHE[key]=(time.time(),value); return value,False
def result(provider,ident,title,kind,thumb,url,embed='',duration=None,published=None,description=''):
    return {'id':f'{provider}:{kind}:{ident}','provider':provider,'type':kind,'title':title or 'Untitled','thumbnail':thumb or '', 'sourceUrl':url or '', 'embedUrl':embed or '', 'duration':duration,'publishedAt':published,'description':description or ''}
def published_after(key):
    days={'today':1,'week':7,'month':30,'year':365}.get(key)
    return (datetime.now(timezone.utc)-timedelta(days=days)).isoformat().replace('+00:00','Z') if days else None

def youtube_search(q,kind,limit,duration,published,order):
    key=os.getenv('YOUTUBE_API_KEY','')
    if not key:return [],['YouTube needs setup']
    params={'part':'snippet','type':kind,'maxResults':limit,'q':q,'order':order if order in ('date','title') else 'relevance','key':key}
    if kind=='video' and duration!='any':params['videoDuration']=duration
    after=published_after(published)
    if after:params['publishedAfter']=after
    data=fetch_json('https://www.googleapis.com/youtube/v3/search?'+urlencode(params)); out=[]
    for x in data.get('items',[]):
        s=x.get('snippet',{}); ident=x.get('id',{}).get({'video':'videoId','channel':'channelId','playlist':'playlistId'}[kind]); thumb=s.get('thumbnails',{}).get('medium',{}).get('url','')
        if not ident:continue
        if kind=='video':out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/watch?v={ident}',f'https://www.youtube-nocookie.com/embed/{ident}?autoplay=1',published=s.get('publishedAt'),description=s.get('description')))
        elif kind=='channel':out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/channel/{ident}',published=s.get('publishedAt'),description=s.get('description')))
        else:out.append(result('YouTube',ident,s.get('title'),kind,thumb,f'https://www.youtube.com/playlist?list={ident}',published=s.get('publishedAt'),description=s.get('description')))
    return out,[]
def youtube_playlist(pid,limit=50):
    key=os.getenv('YOUTUBE_API_KEY','')
    if not key:return [],['YouTube needs setup']
    data=fetch_json('https://www.googleapis.com/youtube/v3/playlistItems?'+urlencode({'part':'snippet,contentDetails','playlistId':pid,'maxResults':min(limit,50),'key':key}));out=[]
    for x in data.get('items',[]):
        s=x.get('snippet',{}); ident=x.get('contentDetails',{}).get('videoId') or s.get('resourceId',{}).get('videoId')
        if ident:out.append(result('YouTube',ident,s.get('title'),'video',s.get('thumbnails',{}).get('medium',{}).get('url',''),f'https://www.youtube.com/watch?v={ident}',f'https://www.youtube-nocookie.com/embed/{ident}?autoplay=1',published=s.get('publishedAt'),description=s.get('description')))
    return out,[]
def vimeo(q,limit,order):
    token=os.getenv('VIMEO_ACCESS_TOKEN','')
    if not token:return [],['Vimeo needs setup']
    data=fetch_json('https://api.vimeo.com/videos?'+urlencode({'query':q,'per_page':limit,'sort':'date' if order=='date' else 'relevant','direction':'desc'}),{'Authorization':f'Bearer {token}','Accept':'application/vnd.vimeo.*+json;version=3.4'});out=[]
    for x in data.get('data',[]):
        ident=(x.get('uri') or '').split('/')[-1];pics=x.get('pictures',{}).get('sizes',[])
        if ident:out.append(result('Vimeo',ident,x.get('name'),'video',pics[-1].get('link') if pics else '',x.get('link'),f'https://player.vimeo.com/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time'),x.get('description')))
    return out,[]
def dailymotion(q,limit):
    token=os.getenv('DAILYMOTION_ACCESS_TOKEN','')
    if not token:return [],['Dailymotion needs setup']
    fields='id,title,description,thumbnail_360_url,url,duration,created_time';data=fetch_json('https://api.dailymotion.com/videos?'+urlencode({'search':q,'limit':limit,'fields':fields}),{'Authorization':f'Bearer {token}'});out=[]
    for x in data.get('list',[]):
        ident=x.get('id')
        if ident:out.append(result('Dailymotion',ident,x.get('title'),'video',x.get('thumbnail_360_url'),x.get('url') or f'https://www.dailymotion.com/video/{ident}',f'https://www.dailymotion.com/embed/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time'),x.get('description')))
    return out,[]
def peertube(q,limit,order):
    base=os.getenv('PEERTUBE_INSTANCE','https://sepiasearch.org').rstrip('/');sort={'date':'-publishedAt','title':'name'}.get(order,'-match')
    data=fetch_json(base+'/api/v1/search/videos?'+urlencode({'search':q,'count':limit,'sort':sort}));out=[]
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
        except (HTTPError,URLError,TimeoutError,ValueError):warnings.append(f'{name.title()} request failed')
    if order=='title':out.sort(key=lambda x:(x.get('title') or '').lower())
    elif order=='date':out.sort(key=lambda x:x.get('publishedAt') or '',reverse=True)
    return {'query':q,'results':out,'warnings':warnings}

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        rel=urlparse(path).path.lstrip('/') or 'index.html';candidate=(ROOT/rel).resolve();return str(candidate if str(candidate).startswith(str(ROOT)) else ROOT/'index.html')
    def send_json(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        u=urlparse(self.path);p=parse_qs(u.query)
        if u.path=='/api/health':return self.send_json({'version':'1.2.0','cache':{'entries':len(CACHE),'ttlSeconds':TTL},'providers':{'youtube':{'ready':bool(os.getenv('YOUTUBE_API_KEY'))},'vimeo':{'ready':bool(os.getenv('VIMEO_ACCESS_TOKEN'))},'dailymotion':{'ready':bool(os.getenv('DAILYMOTION_ACCESS_TOKEN'))},'peertube':{'ready':True,'instance':os.getenv('PEERTUBE_INSTANCE','https://sepiasearch.org')}}})
        if u.path=='/api/search':
            try:
                key=('search',u.query);data,hit=cached(key,lambda:search(p));data={**data,'cacheHit':hit};return self.send_json(data)
            except ValueError as e:return self.send_json({'error':str(e)},400)
        if u.path=='/api/playlist':
            pid=(p.get('id') or [''])[0]
            if not pid:return self.send_json({'error':'Playlist id is required'},400)
            try:
                (res,w),hit=cached(('playlist',pid),lambda:youtube_playlist(pid));return self.send_json({'results':res,'warnings':w,'cacheHit':hit})
            except (HTTPError,URLError,TimeoutError,ValueError):return self.send_json({'error':'Playlist request failed'},502)
        return super().do_GET()
    def log_message(self,fmt,*args):print('[OpenMedia]',fmt%args)
if __name__=='__main__':
    os.chdir(ROOT);print(f'OpenMedia Lite v1.2.0 running at http://{HOST}:{PORT}')
    try:ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
    except KeyboardInterrupt:pass
