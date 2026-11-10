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
        data=self.get('/api/health');self.assertEqual(data['version'],'1.3.0');self.assertTrue(data['cache']['persistent'])
    def test_state_and_progress(self):
        item={'id':'Smoke:video:1','name':'Smoke item','type':'video','source':'Smoke','sourceUrl':'https://example.invalid','favorite':False,'library':'Tests'}
        self.post('/api/state',{'libraries':['Tests'],'items':[item]});self.post('/api/progress',{'id':item['id'],'position':12,'duration':60})
        data=self.get('/api/state');self.assertIn('Tests',data['libraries']);self.assertEqual(data['progress'][item['id']]['position'],12)
if __name__=='__main__':unittest.main()
