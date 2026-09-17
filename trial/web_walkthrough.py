"""Loopback-only web host for the fictional Copilot rep walkthrough."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
import json
import os
import secrets
import threading
import uuid

from rep_walkthrough import Walkthrough, load_key
from investigation import OpenAIModel
from journeys import JourneyWalkthrough

ROOT=Path(__file__).resolve().parent
CASES=json.loads((ROOT/'reviewed_cases.json').read_text())
COMPLETION_CASES=json.loads((ROOT/'completion_cases.json').read_text())
SESSIONS={}
SESSION_LOCK=threading.Lock()
ALLOWED_HOSTS={'copilot-lab.localhost','localhost','127.0.0.1'}


class BrowserSession:
    def __init__(self,model=None):
        self.model=model or OpenAIModel(max_calls=30,budget=.50)
        self.lock=threading.Lock()
        self.version=0
        self.result=None
        self.last_error=None
        (ROOT.parent/'outputs'/'walkthrough').mkdir(exist_ok=True)
        self.log=ROOT.parent/'outputs'/'walkthrough'/('web-'+str(uuid.uuid4())+'.json')
        self.start('resolve_journey')

    def start(self,family):
        if family in {'resolve_journey','escalate_journey'}:
            self.walk=JourneyWalkthrough(self.model)
            self.family=family
            self.result=None
            self.last_error=None
            return
        if family in {'access','integration'}:
            case=next(c for c in CASES if c['id']==('C05' if family=='access' else 'C07'))
        else:
            case=next((c for c in COMPLETION_CASES if c['id']==family),None)
            if case is None:raise ValueError('Choose a listed example case.')
        self.walk=Walkthrough(case,self.model)
        self.family=family
        self.result=None
        self.last_error=None

    def state(self):
        w=self.walk
        return {'family':self.family,'version':self.version,'busy':self.lock.locked(),
            'customer_update':w.case['stages'][w.stage]['event']['text'],
            'account':w.case['stages'][w.stage]['event']['facts'].get('account',''),
            'step':w.stage+1,'total_steps':len(w.case['stages']),
            'progress':w.progress.snapshot(),'pending_question':w.pending_question,
            'advice':self.result,'last_error':self.last_error,
            'checks':[{'name':h['target'].replace('_',' '),'status':h.get('status','ok'),'result':h['text']}
                      for h in w.history if h.get('type')=='read'],
            'notes':[{'kind':h['type'],'text':h.get('text',h.get('message',''))}
                     for h in w.history if h.get('type') in {'rep_report','rep_answer','private_advice'}],
            'calls_used':getattr(self.model,'calls',len(w.calls))}

    def apply(self,data):
        if not isinstance(data,dict) or type(data.get('version')) is not int:
            raise ValueError('Refresh the page before continuing.')
        if data['version']!=self.version:raise ValueError('The case changed in another request. Review the current case before continuing.')
        action=data.get('action')
        w=self.walk
        if action=='start':
            w.save(self.log)
            self.start(data.get('family'))
            self.log=ROOT.parent/'outputs'/'walkthrough'/('web-'+str(uuid.uuid4())+'.json')
        elif action=='advice':
            if isinstance(self.model,OpenAIModel):load_key()
            self.result=w.advise()
        elif action in {'answer','note','finding'}:
            value=data.get('text')
            if not isinstance(value,str) or not value.strip() or len(value)>8000:
                raise ValueError('Enter a short update first (up to 8,000 characters).')
            if action=='answer':w.answer(value)
            elif action=='finding':w.finding(value)
            else:w.note(value)
            self.result=None
            if isinstance(self.model,OpenAIModel):load_key()
            self.result=w.advise()
        elif action=='accept_handoff':
            self.result=w.accept_handoff()
        elif action=='next':
            if not w.advance():raise ValueError('There are no more prepared updates. You can still add your findings.')
            self.result=None
        elif action in {'worked','failed','unclear','untried','close'}:
            if not w.progress.proposal_id or data.get('proposal_id')!=w.progress.proposal_id:
                raise ValueError('That suggestion is no longer current. Review the latest advice first.')
            outcomes={'worked':'worked','failed':'did_not_work','unclear':'unclear','untried':'not_tried'}
            w.feedback(outcomes.get(action),close=action=='close')
            if action in {'worked','close'}:self.result={'message':'Success is verified. You can close the case when ready.' if action=='worked' else 'You closed the case after confirming success.'}
            elif action=='failed':self.result={'message':'The case remains open. Describe what happened on the retry, then ask Copilot for the next investigation step.'}
            else:self.result={'message':'The outcome is not verified. The case stays open until you confirm what happened when the customer tried the fix.'}
        else:raise ValueError('Unknown action.')
        self.version+=1
        self.last_error=None


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass

    def valid_host(self):
        return self.headers.get('Host','').split(':')[0] in ALLOWED_HOSTS

    def session(self):
        try:
            cookie=SimpleCookie(self.headers.get('Cookie',''))
            item=cookie.get('copilot_lab_session')
            return SESSIONS.get(item.value) if item else None
        except Exception:return None

    def send(self,status,body,kind='application/json',cookie=None):
        raw=json.dumps(body).encode() if kind=='application/json' else body
        self.send_response(status)
        self.send_header('Content-Type',kind+'; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        if cookie:self.send_header('Set-Cookie',cookie)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self.valid_host():return self.send(403,{'error':'Local host required.'})
        if self.path=='/':
            cookie=None
            if not self.session():
                with SESSION_LOCK:
                    if len(SESSIONS)>=20:return self.send(503,{'error':'Too many browser sessions. Restart the local walkthrough server.'})
                    token=secrets.token_urlsafe(32)
                    SESSIONS[token]=BrowserSession()
                cookie='copilot_lab_session='+token+'; HttpOnly; SameSite=Strict; Path=/'
            return self.send(200,(ROOT/'web/index.html').read_bytes(),'text/html',cookie)
        if self.path in {'/app.js','/style.css'}:
            return self.send(200,(ROOT/'web'/self.path[1:]).read_bytes(),'text/javascript' if self.path.endswith('.js') else 'text/css')
        session=self.session()
        if not session:return self.send(401,{'error':'Open the walkthrough page to start your session.'})
        if self.path=='/api/state':return self.send(200,session.state())
        return self.send(404,{'error':'Not found.'})

    def do_POST(self):
        if not self.valid_host():return self.send(403,{'error':'Local host required.'})
        host=self.headers.get('Host','')
        if self.headers.get('Origin') not in {'http://'+host,'https://'+host} or self.headers.get('X-Copilot-Action')!='1':
            return self.send(403,{'error':'Use the walkthrough page for this action.'})
        session=self.session()
        if not session:return self.send(401,{'error':'Your local session expired. Reload the page.'})
        if self.path!='/api/action':return self.send(404,{'error':'Not found.'})
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.send(400,{'error':'Invalid request.'})
        if not 0<length<=20000:return self.send(413,{'error':'That update is too long.'})
        try:data=json.loads(self.rfile.read(length))
        except (ValueError,UnicodeDecodeError):return self.send(400,{'error':'Invalid update.'})
        if not session.lock.acquire(blocking=False):return self.send(409,{'error':'Copilot is still reviewing the current update.'})
        status=200
        try:
            session.apply(data)
        except ValueError as exc:
            status=400
            session.last_error={'closure_requires_rep_verified_success':'Confirm the retry worked before closing.',
                'no_pending_question':'There is no pending question. Choose “New finding or correction” instead.'}.get(str(exc),str(exc))
            # Failed requests may have recorded an update before a provider/key failure.
            session.version+=1
        except Exception:
            status=503;session.last_error='The request could not finish. Your case is kept; please try again.';session.version+=1
        finally:
            try:
                session.log.parent.mkdir(exist_ok=True)
                session.walk.save(session.log)
            finally:
                session.lock.release()
        return self.send(status,session.state())


def main():
    port=int(os.environ.get('PORT','8766'))
    print('Copilot web walkthrough listening on loopback',flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()

if __name__=='__main__':main()
