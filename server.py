#!/usr/bin/env python3
import json, mimetypes, os, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
HOST, PORT = '127.0.0.1', int(os.getenv('OPENMEDIA_PORT', '8080'))

def fetch_json(url, headers=None):
    req = Request(url, headers={'User-Agent':'OpenMedia-Lite/1.1', **(headers or {})})
    with urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode('utf-8'))

def item(provider, ident, title, thumb, url, embed=None, duration=None, published=None):
    return {'id':f'{provider}:{ident}','provider':provider,'type':'video','title':title or 'Untitled','thumbnail':thumb or '',
            'sourceUrl':url,'embedUrl':embed or '', 'duration':duration, 'publishedAt':published}

def youtube(q, limit):
    key=os.getenv('YOUTUBE_API_KEY','')
    if not key: return [], 'YOUTUBE_API_KEY is not configured'
    data=fetch_json('https://www.googleapis.com/youtube/v3/search?'+urlencode({'part':'snippet','type':'video','maxResults':limit,'q':q,'key':key}))
    out=[]
    for x in data.get('items',[]):
        vid=x.get('id',{}).get('videoId'); s=x.get('snippet',{})
        if vid: out.append(item('YouTube',vid,s.get('title'),s.get('thumbnails',{}).get('medium',{}).get('url'),f'https://www.youtube.com/watch?v={vid}',f'https://www.youtube-nocookie.com/embed/{vid}?autoplay=1',published=s.get('publishedAt')))
    return out, None

def vimeo(q, limit):
    token=os.getenv('VIMEO_ACCESS_TOKEN','')
    if not token: return [], 'VIMEO_ACCESS_TOKEN is not configured'
    data=fetch_json('https://api.vimeo.com/videos?'+urlencode({'query':q,'per_page':limit,'sort':'relevant'}),{'Authorization':f'Bearer {token}','Accept':'application/vnd.vimeo.*+json;version=3.4'})
    out=[]
    for x in data.get('data',[]):
        ident=(x.get('uri') or '').split('/')[-1]; pics=x.get('pictures',{}).get('sizes',[])
        if ident: out.append(item('Vimeo',ident,x.get('name'),pics[-1].get('link') if pics else '',x.get('link') or f'https://vimeo.com/{ident}',f'https://player.vimeo.com/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time')))
    return out, None

def dailymotion(q, limit):
    token=os.getenv('DAILYMOTION_ACCESS_TOKEN','')
    if not token: return [], 'DAILYMOTION_ACCESS_TOKEN is not configured'
    fields='id,title,thumbnail_360_url,url,duration,created_time'
    data=fetch_json('https://api.dailymotion.com/videos?'+urlencode({'search':q,'limit':limit,'fields':fields}),{'Authorization':f'Bearer {token}'})
    out=[]
    for x in data.get('list',[]):
        ident=x.get('id')
        if ident: out.append(item('Dailymotion',ident,x.get('title'),x.get('thumbnail_360_url'),x.get('url') or f'https://www.dailymotion.com/video/{ident}',f'https://www.dailymotion.com/embed/video/{ident}?autoplay=1',x.get('duration'),x.get('created_time')))
    return out, None

def peertube(q, limit):
    base=os.getenv('PEERTUBE_INSTANCE','https://sepiasearch.org').rstrip('/')
    data=fetch_json(base+'/api/v1/search/videos?'+urlencode({'search':q,'count':limit,'sort':'-match'}))
    out=[]
    for x in data.get('data',[]):
        ident=x.get('uuid') or x.get('shortUUID') or x.get('id'); host=x.get('account',{}).get('host') or urlparse(base).netloc
        page=x.get('url') or f'https://{host}/w/{ident}'; thumb=x.get('thumbnailPath') or ''
        if thumb.startswith('/'): thumb=f'https://{host}{thumb}'
        if ident: out.append(item('PeerTube',str(ident),x.get('name'),thumb,page,f'https://{host}/videos/embed/{ident}?autoplay=1',x.get('duration'),x.get('publishedAt')))
    return out, None

PROVIDERS={'youtube':youtube,'vimeo':vimeo,'dailymotion':dailymotion,'peertube':peertube}
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        rel=urlparse(path).path.lstrip('/') or 'index.html'
        return str((ROOT/rel).resolve()) if str((ROOT/rel).resolve()).startswith(str(ROOT)) else str(ROOT/'index.html')
    def send_json(self, data, status=200):
        raw=json.dumps(data,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/api/health':
            return self.send_json({'version':'1.1.0','providers':{'youtube':bool(os.getenv('YOUTUBE_API_KEY')),'vimeo':bool(os.getenv('VIMEO_ACCESS_TOKEN')),'dailymotion':bool(os.getenv('DAILYMOTION_ACCESS_TOKEN')),'peertube':True}})
        if u.path=='/api/search':
            p=parse_qs(u.query); q=(p.get('q') or [''])[0].strip(); selected=(p.get('provider') or ['all'])[0].lower()
            if not q: return self.send_json({'error':'Search query is required'},400)
            names=list(PROVIDERS) if selected=='all' else [selected]
            results=[]; warnings=[]
            for name in names:
                if name not in PROVIDERS: continue
                try:
                    found,warn=PROVIDERS[name](q,12); results.extend(found)
                    if warn: warnings.append(warn)
                except (HTTPError,URLError,TimeoutError,ValueError) as e: warnings.append(f'{name}: provider request failed')
            return self.send_json({'query':q,'results':results,'warnings':warnings})
        return super().do_GET()
    def log_message(self, fmt, *args): print('[OpenMedia]',fmt%args)

if __name__=='__main__':
    os.chdir(ROOT); print(f'OpenMedia Lite v1.1.0 running at http://{HOST}:{PORT}')
    try: ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
    except KeyboardInterrupt: pass
