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
        data=self.get('/api/health');self.assertEqual(data['version'],'1.7.0');self.assertTrue(data['cache']['persistent'])
    def test_state_and_progress(self):
        item={'id':'Smoke:video:1','name':'Smoke item','type':'video','source':'Smoke','sourceUrl':'https://example.invalid','favorite':False,'library':'Tests'}
        self.post('/api/state',{'libraries':['Tests'],'items':[item]});self.post('/api/progress',{'id':item['id'],'position':12,'duration':60})
        data=self.get('/api/state');self.assertIn('Tests',data['libraries']);self.assertEqual(data['progress'][item['id']]['position'],12)
    def test_queue_history_preferences(self):
        payload={'libraries':[],'items':[],'queue':['Smoke:video:1'],'history':[{'id':'Smoke:video:1','playedAt':123}],'preferences':{'repeatMode':'all','shuffleOn':True}}
        self.post('/api/state',payload);data=self.get('/api/state')
        self.assertEqual(data['queue'],['Smoke:video:1']);self.assertEqual(data['history'][0]['playedAt'],123);self.assertEqual(data['preferences']['repeatMode'],'all')
    def test_backup_diagnostics_and_restore(self):
        backup=self.get('/api/backup');self.assertEqual(backup['version'],'1.7.0');self.assertIn('state',backup)
        diagnostics=self.get('/api/diagnostics');self.assertEqual(diagnostics['version'],'1.7.0');self.assertIn('databaseBytes',diagnostics)
        restored=self.post('/api/restore',{'state':{'libraries':['Restored'],'items':[],'progress':{},'queue':[],'history':[],'preferences':{}}})
        self.assertTrue(restored['restored']);self.assertIn('Restored',restored['state']['libraries'])
    def test_authoritative_deletion_and_maintenance(self):
        first={'id':'Delete:video:1','name':'Delete me','type':'video','source':'Test','sourceUrl':'https://example.invalid/delete'}
        self.post('/api/state',{'libraries':['Temp'],'items':[first],'replaceItems':True,'replaceLibraries':True})
        self.post('/api/state',{'libraries':[],'items':[],'replaceItems':True,'replaceLibraries':True})
        state=self.get('/api/state');self.assertEqual(state['items'],[]);self.assertEqual(state['libraries'],[])
        result=self.post('/api/maintenance',{'action':'clear-cache'});self.assertEqual(result['completed'],'clear-cache')
if __name__=='__main__':unittest.main()
