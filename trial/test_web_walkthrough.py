import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from web_walkthrough import BrowserSession, Handler
from rep_walkthrough import Walkthrough
from test_investigation import example_case, decision, scripted_model


class WebSessionTests(unittest.TestCase):
    def test_outcome_requires_matching_version_and_proposal(self):
        s=BrowserSession(lambda p:(decision(),{}));s.walk=Walkthrough(example_case(),scripted_model)
        s.apply({'version':0,'action':'advice'})
        ident=s.walk.progress.proposal_id
        with self.assertRaises(ValueError):s.apply({'version':0,'action':'worked','proposal_id':ident})
        with self.assertRaises(ValueError):s.apply({'version':1,'action':'worked','proposal_id':'old'})
        self.assertFalse(s.walk.progress.closed)
        s.apply({'version':1,'action':'worked','proposal_id':ident})
        self.assertEqual(s.walk.progress.outcome,'worked');self.assertFalse(s.walk.progress.closed)
        s.apply({'version':2,'action':'close','proposal_id':ident})
        self.assertTrue(s.walk.progress.closed)

    def test_close_rejected_before_success(self):
        s=BrowserSession(lambda p:(decision(),{}));s.walk=Walkthrough(example_case(),scripted_model)
        s.apply({'version':0,'action':'advice'})
        with self.assertRaises(ValueError):s.apply({'version':1,'action':'close','proposal_id':s.walk.progress.proposal_id})
        self.assertFalse(s.walk.progress.closed)

    def test_answer_and_advice_use_existing_pending_question(self):
        model=lambda p:(decision(kind='ask',target='scope'),{})
        s=BrowserSession(model);s.walk=Walkthrough(example_case(),model)
        s.apply({'version':0,'action':'advice'})
        s.apply({'version':1,'action':'answer','text':'The same users are affected'})
        self.assertTrue(any(h['type']=='rep_answer' for h in s.walk.history))
        self.assertFalse(s.walk.progress.closed)

    def test_retracting_success_replaces_success_message(self):
        for action in ['unclear','untried']:
            s=BrowserSession(lambda p:(decision(),{}));s.walk=Walkthrough(example_case(),scripted_model)
            s.apply({'version':0,'action':'advice'});ident=s.walk.progress.proposal_id
            s.apply({'version':1,'action':'worked','proposal_id':ident})
            s.apply({'version':2,'action':action,'proposal_id':ident})
            self.assertNotIn('Success is verified',s.result['message'])
            self.assertEqual(s.walk.progress.snapshot()['status'],'awaiting_rep_verification')

    def test_replacement_advice_clears_previous_question(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='ask',target='scope'),{}))
        w.advise();self.assertEqual(w.pending_question,'scope')
        w.note('New information changes the investigation')
        w.model=lambda p:(decision(),{})
        w.advise();self.assertIsNone(w.pending_question)

    def test_failed_advice_clears_hidden_question(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='ask',target='scope'),{}))
        w.advise();w.note('New information changes the investigation');w.model=lambda p:([],{})
        w.advise();self.assertIsNone(w.pending_question)

    def test_repeated_source_removed_and_not_executed_again(self):
        seen=[]
        def model(prompt):
            payload=json.loads(prompt.split('\nINPUT\n')[1]);seen.append(payload)
            if len(seen)<=2:return decision(kind='read',target='record'),{}
            return decision(kind='ask',target='scope'),{}
        w=Walkthrough(example_case(),model);result=w.advise()
        self.assertEqual(len([h for h in w.history if h['type']=='read']),1)
        self.assertEqual(seen[1]['sources'],[])
        self.assertTrue(w.calls[1]['repeated_check_blocked'])
        self.assertIn('suggested_question',result)

    def test_persistent_repeated_source_is_bounded(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='read',target='record'),{}))
        result=w.advise()
        self.assertFalse(result['recommendation_available'])
        self.assertEqual(len(w.calls),3)
        self.assertNotIn('repeated a check',result['message'])
        self.assertFalse(w.progress.closed)


class LocalHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,headers=None,body=None):
        c=HTTPConnection('127.0.0.1',self.server.server_port)
        c.request(method,path,body=body,headers={'Host':'localhost',**(headers or {})})
        r=c.getresponse();result=(r.status,dict(r.getheaders()),r.read());c.close();return result
    def test_api_requires_browser_session(self):
        self.assertEqual(self.request('GET','/api/state')[0],401)
    def test_host_and_cross_site_posts_rejected(self):
        self.assertEqual(self.request('GET','/',{'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('POST','/api/action',{'Origin':'https://evil.example'},'{}')[0],403)
    def test_reload_keeps_case_cookie(self):
        status,headers,_=self.request('GET','/')
        cookie=headers['Set-Cookie'].split(';')[0]
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        self.assertIn('SameSite=Strict',headers['Set-Cookie'])
        status,again,body=self.request('GET','/',{'Cookie':cookie})
        self.assertNotIn('Set-Cookie',again)
        state=self.request('GET','/api/state',{'Cookie':cookie})
        self.assertEqual(state[0],200)
        self.assertNotIn('OPENAI_API_KEY',state[2].decode())
    def test_bad_action_cannot_change_case(self):
        _,headers,_=self.request('GET','/');cookie=headers['Set-Cookie'].split(';')[0]
        status,_,body=self.request('POST','/api/action',{'Cookie':cookie,'Origin':'http://localhost','X-Copilot-Action':'1'},json.dumps({'action':'close','version':0,'proposal_id':'fake'}))
        self.assertEqual(status,400)
        self.assertFalse(json.loads(body)['progress']['closed'])

if __name__=='__main__':unittest.main()
