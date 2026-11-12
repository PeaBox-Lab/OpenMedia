import json, os, subprocess, tempfile, time, unittest
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
class OpenMediaSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port='18093';env={**os.environ,'OPENMEDIA_PORT':cls.port}
        cls.proc=subprocess.Popen(['python',str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.7)
    @classmethod
    def tearDownClass(cls):cls.proc.terminate();cls.proc.wait(timeout=5)
    def get(self,path):return json.load(urlopen(f'http://127.0.0.1:{self.port}'+path,timeout=5))
    def post(self,path,data):
        req=Request(f'http://127.0.0.1:{self.port}'+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'},method='POST')
        return json.load(urlopen(req,timeout=5))
    def test_health(self):
        data=self.get('/api/health');self.assertEqual(data['version'],'3.0.0');self.assertTrue(data['cache']['persistent'])
    def test_state_and_progress(self):
        item={'id':'Smoke:video:1','name':'Smoke item','type':'video','source':'Smoke','sourceUrl':'https://example.invalid','favorite':False,'library':'Tests'}
        self.post('/api/state',{'libraries':['Tests'],'items':[item]});self.post('/api/progress',{'id':item['id'],'position':12,'duration':60})
        data=self.get('/api/state');self.assertIn('Tests',data['libraries']);self.assertEqual(data['progress'][item['id']]['position'],12)
    def test_queue_history_preferences(self):
        payload={'libraries':[],'items':[],'queue':['Smoke:video:1'],'history':[{'id':'Smoke:video:1','playedAt':123}],'preferences':{'repeatMode':'all','shuffleOn':True}}
        self.post('/api/state',payload);data=self.get('/api/state')
        self.assertEqual(data['queue'],['Smoke:video:1']);self.assertEqual(data['history'][0]['playedAt'],123);self.assertEqual(data['preferences']['repeatMode'],'all')
    def test_backup_diagnostics_and_restore(self):
        backup=self.get('/api/backup');self.assertEqual(backup['version'],'3.0.0');self.assertIn('state',backup)
        diagnostics=self.get('/api/diagnostics');self.assertEqual(diagnostics['version'],'3.0.0');self.assertIn('databaseBytes',diagnostics)
        restored=self.post('/api/restore',{'state':{'libraries':['Restored'],'items':[],'progress':{},'queue':[],'history':[],'preferences':{}}})
        self.assertTrue(restored['restored']);self.assertIn('Restored',restored['state']['libraries'])
    def test_authoritative_deletion_and_maintenance(self):
        first={'id':'Delete:video:1','name':'Delete me','type':'video','source':'Test','sourceUrl':'https://example.invalid/delete'}
        self.post('/api/state',{'libraries':['Temp'],'items':[first],'replaceItems':True,'replaceLibraries':True})
        self.post('/api/state',{'libraries':[],'items':[],'replaceItems':True,'replaceLibraries':True})
        state=self.get('/api/state');self.assertEqual(state['items'],[]);self.assertEqual(state['libraries'],[])
        result=self.post('/api/maintenance',{'action':'clear-cache'});self.assertEqual(result['completed'],'clear-cache')
    def test_personal_metadata_and_subscriptions(self):
        item={'id':'Personal:video:1','name':'Personal','type':'video','source':'Test','sourceUrl':'https://example.invalid/personal','watchLater':True,'rating':5,'notes':'Review chapter 3'}
        prefs={'subscriptions':[{'id':'sub-1','name':'Creator','provider':'YouTube','url':'https://example.invalid/creator'}]}
        self.post('/api/state',{'items':[item],'libraries':[],'preferences':prefs,'replaceItems':True,'replaceLibraries':True})
        state=self.get('/api/state');self.assertTrue(state['items'][0]['watchLater']);self.assertEqual(state['items'][0]['rating'],5);self.assertEqual(state['items'][0]['notes'],'Review chapter 3');self.assertEqual(state['preferences']['subscriptions'][0]['name'],'Creator')
    def test_playlists_tags_reminders_accessibility(self):
        item={'id':'Tagged:video:1','name':'Tagged','type':'video','source':'Test','sourceUrl':'https://example.invalid/tagged','tags':['research','demo']}
        prefs={'playlists':[{'id':'p1','name':'Research','items':['Tagged:video:1']}],'reminders':[{'id':'r1','itemId':'Tagged:video:1','title':'Tagged','due':9999999999999,'notified':False}],'reducedMotion':True,'highContrast':True,'largeText':True}
        self.post('/api/state',{'items':[item],'libraries':[],'preferences':prefs,'replaceItems':True,'replaceLibraries':True})
        state=self.get('/api/state');self.assertEqual(state['items'][0]['tags'],['research','demo']);self.assertEqual(state['preferences']['playlists'][0]['items'],['Tagged:video:1']);self.assertTrue(state['preferences']['reducedMotion']);self.assertTrue(state['preferences']['highContrast']);self.assertTrue(state['preferences']['largeText'])
    def test_bookmarks_and_session_recovery(self):
        item={'id':'Recover:video:1','name':'Recover','type':'video','source':'Test','sourceUrl':'https://example.invalid/recover'}
        prefs={'bookmarks':[{'id':'b1','itemId':'Recover:video:1','position':33.5,'label':'Key point','note':'Review'}],'lastSession':{'itemId':'Recover:video:1','position':33.5,'playedAt':12345}}
        self.post('/api/state',{'items':[item],'libraries':[],'preferences':prefs,'replaceItems':True,'replaceLibraries':True})
        state=self.get('/api/state');self.assertEqual(state['preferences']['bookmarks'][0]['position'],33.5);self.assertEqual(state['preferences']['lastSession']['itemId'],'Recover:video:1')
    def test_provider_catalog(self):
        data=self.get('/api/providers');self.assertEqual(data['version'],'3.0.0')
        ids=[p['id'] for p in data['providers']]
        for expected in ('youtube','vimeo','dailymotion','peertube','soundcloud','twitch','tiktok','reddit','bilibili','rumble','odysee','archive','ccc','kick','niconico','piped'):
            self.assertIn(expected,ids)
        yt=next(p for p in data['providers'] if p['id']=='youtube')
        self.assertTrue(yt['keyless']);self.assertIn('apiConsole',yt);self.assertIn('signIn',yt)

if __name__=='__main__':unittest.main()