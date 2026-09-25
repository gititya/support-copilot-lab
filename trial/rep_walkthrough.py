"""Interactive fictional case walkthrough for a human rep; no product connection."""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time
import uuid

from case_progress import CaseProgress
from investigation import OpenAIModel, ingest, public_payload, make_prompt, validate_decision


class Walkthrough:
    def __init__(self, case, model):
        self.case, self.model = deepcopy(case), model
        self.stage = -1
        self.ledger, self.history, self.calls = {}, [], []
        self.progress = CaseProgress()
        self.previous = None
        self.attempted = []
        self.pending_question = None
        self.last_note = None
        self.sources = {}
        self.cached_advice = None
        self.advance()

    def advance(self):
        if self.stage + 1 >= len(self.case['stages']):
            return False
        self.cached_advice = None
        self.progress.new_evidence()
        self.previous = None
        # The prepared stages supply a new record snapshot; previous observations stay in history.
        self.ledger = {}
        self.stage += 1
        self.sources = deepcopy(self.case['stages'][self.stage]['reads'])
        self.attempted = []
        self.pending_question = None
        self.last_note = None
        event = deepcopy(self.case['stages'][self.stage]['event'])
        ingest(self.ledger, event, 'customer_update_'+str(self.stage))
        self.event = event
        self.history.append({'type':'customer_update', **event})
        return True

    def note(self, text):
        text = text.strip()
        if not text or text == self.last_note:
            return False
        self.cached_advice = None
        self.progress.new_evidence()
        self.previous = None
        self.last_note = text
        self.pending_question = None
        self.attempted = []
        self.event = {'text':'The rep reports: '+text, 'facts':{'rep_report':text}}
        self.ledger = {}
        self.sources = {}
        ingest(self.ledger,self.event,'rep_report_'+str(len(self.history)))
        self.history.append({'type':'rep_report', **self.event})
        # Free text remains a report. It cannot verify success or close a case.
        return True

    def finding(self, text):
        """An additive observation keeps the same case scope and checked records."""
        text = text.strip()
        if not text or text == self.last_note:
            return False
        self.cached_advice = None
        self.progress.new_evidence()
        self.previous = None
        self.last_note = text
        self.pending_question = None
        key = 'rep_finding_' + str(len(self.history))
        self.event = {'text': 'New finding in the same case: '+text, 'facts': {key: text}}
        ingest(self.ledger, self.event, key)
        self.history.append({'type': 'rep_report', **self.event})
        return True

    def accept_handoff(self):
        if not self.cached_advice or 'handoff' not in self.cached_advice:
            raise ValueError('No current handoff to accept.')
        self.cached_advice = deepcopy(self.cached_advice)
        self.cached_advice['handoff']['rep_review_required'] = False
        self.cached_advice['handoff']['accepted_by_rep'] = True
        self.cached_advice['message'] = 'You accepted the handoff. Copy the case below to your receiving team. Nothing has been sent; customer recovery is still unverified.'
        self.history.append({'type': 'rep_handoff_accepted', 'handoff': deepcopy(self.cached_advice['handoff'])})
        return self.cached_advice

    def answer(self, text):
        if not self.pending_question:
            raise ValueError('no_pending_question')
        text=text.strip()
        if not text: raise ValueError('empty_answer')
        question=self.pending_question
        self.cached_advice = None
        self.progress.new_evidence()
        self.previous=None
        answer_key='answer_'+question+(('_'+str(len(self.history))) if question=='clarify' else '')
        self.event={'text':'Rep answer, with the same affected scope: '+text,
                    'facts':{answer_key:text}}
        ingest(self.ledger,self.event,'rep_answer_'+str(len(self.history)))
        self.history.append({'type':'rep_answer','question':question,**self.event})
        self.attempted.append({'kind':'ask','target':question})
        self.pending_question=None

    def feedback(self, outcome=None, close=False):
        control = {'proposal_id':self.progress.proposal_id,'close':close}
        if outcome is not None: control['outcome']=outcome
        self.progress.feedback(control)
        self.cached_advice = None
        self.history.append({'type':'rep_control', **control})

    def advise(self):
        if self.progress.closed or self.progress.outcome == 'worked':
            return {'message':'Success verified. You decide whether to close the case.', 'model_called':False}
        if self.cached_advice is not None:
            return {**deepcopy(self.cached_advice), "model_called":False, "reused_advice":True}
        self.pending_question = None
        visible = {'sources':[{**x,'revision':self.stage+1} for x in self.case['sources']], 'questions':self.case['questions']}
        rejected_repeat = False
        recovered_focus = False
        answered={key[len('answer_'):] for key in self.ledger if key.startswith('answer_')}
        # A narrow follow-up is allowed even when a broad question received only a partial answer.
        all_questions=[*self.case['questions'], {'id':'clarify','text':'Ask the specific missing detail about the current problem, using the question in the private advice.'}]
        visible['questions']=[q for q in all_questions if q['id']=='clarify' or q['id'] not in answered]
        for _ in range(5):
            consumed={a['target'] for a in self.attempted if a['kind']=='read'}
            visible['sources']=[{**x,'revision':self.stage+1} for x in self.case['sources'] if x['id'] not in consumed and self.sources.get(x['id'],{}).get('status')=='ok']
            # Full observed history here lets free-text rep corrections stay available.
            payload=public_payload(visible,self.event,self.ledger,self.history,self.previous,'baseline',self.attempted,self.progress)
            unavailable=[x['id'] for x in self.case['sources'] if self.sources.get(x['id'],{}).get('status')!='ok']
            payload['unavailable_sources']=unavailable
            payload['completed_questions']=sorted(answered)
            payload['recent_questions']=[h['message'] for h in self.history if h.get('type')=='private_advice'][-5:]
            extra='This is an interactive rep walkthrough. Rep notes may correct earlier reports. Explain conflicts rather than silently treating both as current. Ask means suggest a question to the REP; stop and let the rep answer. Never invent a customer answer. Do not repeat a failed fix. A new prepared stage supplies revised records: old unavailable results in history do not establish current availability. Check available records that can answer the question before asking the rep. If the current report already identifies the failed action, do not ask the same broad question again; seek a missing detail or check relevant records. The permitted cause labels are a limited lab vocabulary, not all possible causes.'
            prompt=make_prompt(payload,'baseline').replace('\nINPUT\n','\n'+extra+'\nINPUT\n',1)
            started=time.perf_counter()
            try:
                d,meta=self.model(prompt)
                errors=validate_decision(d,self.ledger,{'sources':self.case['sources'],'questions':all_questions})
                if not errors and d.get('cause'):
                    evidence=d['cause']['evidence']
                    if not any(self.ledger[k]['source'].startswith('record_') for k in evidence):
                        errors.append('cause_needs_product_evidence')
            except Exception as exc:
                self.calls.append({'prompt':prompt,'failed':True,'error':str(exc),'duration_ms':(time.perf_counter()-started)*1000})
                return {'message':'The model could not finish. Your case is preserved; use advice to try again.', 'error':str(exc)}
            self.calls.append({'prompt':prompt,'decision':deepcopy(d),'errors':errors,**meta})
            if errors:
                self.previous=None
                return {'message':'Copilot returned advice that failed its evidence or format checks. It has not been accepted.', 'errors':errors}
            kind=d['next']['kind'];target=d['next'].get('target','')
            if kind=='ask' and target=='clarify' and any(h.get('type')=='private_advice' and h.get('message','').strip().casefold()==d['rep_message'].strip().casefold() for h in self.history):
                self.calls[-1]['repeated_question_blocked']=True
                return self.unavailable_advice()
            violation = None
            if kind=='ask' and target in answered and target!='clarify':
                violation='That broad question already received an answer. If a needed detail is still missing, use clarify and ask only that missing detail. Otherwise choose a different useful next step.'
            if kind=='suggest_fix' and d.get('cause') is None:
                violation='No cause has been established. Do not present an experiment as a fix. If a useful diagnostic step is justified, use suggest_check and explain what it tests; otherwise ask the missing detail.'
            if violation:
                self.calls[-1]['focus_rejection']=violation
                if not recovered_focus:
                    recovered_focus=True
                    self.history.append({'type':'focus_correction','text':violation})
                    continue
                return self.unavailable_advice()
            if kind=='read':
                action={'kind':kind,'target':target}
                if action in self.attempted or target not in {x['id'] for x in visible['sources']}:
                    self.calls[-1]['repeated_check_blocked']=True
                    if not rejected_repeat:
                        rejected_repeat=True
                        self.history.append({'type':'check_already_completed','text':
                            'That record is already checked or unavailable for this scope. Do not request it again. Use current observations and ask the most useful missing detail.'})
                        continue
                    return self.unavailable_advice()
                self.attempted.append(action)
                record=deepcopy(self.sources.get(target,{'status':'unavailable','text':'No prepared record available at this point.','facts':{}}))
                ingest(self.ledger,record,'record_'+str(self.stage)+'_'+target)
                self.history.append({'type':'read','target':target,**record})
                continue
            self.previous=d
            self.progress.suggest(d)
            result={'message':d['rep_message'],'decision':d,'model_called':True}
            if kind=='ask':
                self.pending_question=target
                result['suggested_question']=d['rep_message'] if target=='clarify' else next(q['text'] for q in all_questions if q['id']==target)
            if kind=='handoff':
                result['handoff']={'delivery':'not_sent','rep_review_required':True,
                    'observations':deepcopy(list(self.ledger.values())), 'history':deepcopy(self.history),
                    'unknowns':d['open_questions'],'proposed_request':d['rep_message']}
            self.history.append({'type':'private_advice','message':d['rep_message']})
            self.cached_advice=deepcopy(result)
            return result
        return self.unavailable_advice()

    def unavailable_advice(self):
        unavailable=[h['target'] for h in self.history if h.get('type')=='read' and h.get('status')=='unavailable']
        result={'message':"I couldn't produce a reliable next recommendation from the available records. The case remains open. You can add what you learned or load the next example update.",
                'recommendation_available':False,'unavailable_checks':list(dict.fromkeys(unavailable))}
        self.pending_question=None
        self.cached_advice=deepcopy(result)
        self.history.append({'type':'private_advice','message':result['message'],'fallback':True})
        return result

    def save(self,path):
        path.write_text(json.dumps({'kind':'interactive_fictional_walkthrough','case_id':self.case['id'],
            'source_hashes':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ['rep_walkthrough.py','case_progress.py','investigation.py','SUPPORT_RULES.md']},
            'stage':self.stage,'history':self.history,'calls':self.calls,'case_progress':self.progress.snapshot(),
            'progress_history':self.progress.history,'not_a_quality_benchmark':True},indent=2)+'\n')


def load_key():
    if os.environ.get('OPENAI_API_KEY'): return
    key=subprocess.run(['security','find-generic-password','-a','aditya','-s','OpenAI:voice','-w'],capture_output=True,text=True,timeout=5)
    if key.returncode: raise RuntimeError('OpenAI credential unavailable. No calls made.')
    os.environ['OPENAI_API_KEY']=key.stdout.strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=['access','integration'],default='access')
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    cases=json.loads((root/'reviewed_cases.json').read_text())
    chosen='C05' if args.case=='access' else 'C07'
    case=next(c for c in cases if c['id']==chosen)
    print('\nCOPILOT — PRIVATE REP WALKTHROUGH\n')
    print('Fictional case, real AI advice. No customer messages are sent and no app is changed.')
    print('AI explanations need your review; source checks do not prove causality.')
    print('Use fictional details only. Your notes go to OpenAI and are saved locally.')
    print('30 model calls maximum per session. Stop whenever you want.\n')
    load_key()
    session=Walkthrough(case,OpenAIModel(max_calls=30,budget=.50))
    folder=root.parent/'outputs'/'walkthrough';folder.mkdir(exist_ok=True)
    log=folder/(str(uuid.uuid4())+'.json')
    print('CUSTOMER UPDATE:',session.event['text'])
    print('\nCommands: advice | next | worked | failed | unsure | untried | close | quit')
    print('Use answer YOUR ANSWER for the pending question if scope is unchanged. For corrections, type the new information directly. Enter advice to begin.\n')
    try:
        while True:
            text=input('You > ').strip()
            if text=='quit': break
            try:
                if text in {'worked','failed','unsure','untried','close'}:
                    outcomes={'worked':'worked','failed':'did_not_work','unsure':'unclear','untried':'not_tried'}
                    session.feedback(outcomes.get(text),close=text=='close')
                    print('Case:',session.progress.snapshot()['status'].replace('_',' '))
                    if text=='failed': print('The case stays open. Add what happened, or enter advice for another investigation step.')
                elif text.startswith('answer '):
                    session.answer(text[7:])
                    print('Answer recorded for the same affected scope. Enter advice.')
                elif text=='next':
                    if session.advance(): print('CUSTOMER UPDATE:',session.event['text'])
                    else: print('No more prepared updates. Add what you learned or report the outcome.')
                elif text=='advice':
                    print('Copilot is reviewing the case…',flush=True)
                    result=session.advise();print('\nCOPILOT:',result['message'])
                    if result.get('suggested_question'):print('Suggested question for you to ask:',result['suggested_question'])
                    print('Case:',session.progress.snapshot()['status'].replace('_',' '))
                elif text:
                    if session.note(text):
                        print('Your update is recorded. Old prepared records are no longer current for this custom update. Enter advice when ready, or next for the next prepared snapshot.')
                    else:print('That update is already recorded; no model call made.')
            except ValueError as exc:
                messages={'stale_or_missing_proposal':'There is no current suggested fix to verify. Get advice first.',
                          'closure_requires_rep_verified_success':'The case stays open. Confirm that the customer tried it successfully before closing.',
                          'no_pending_question':'There is no pending question. Type a new case update instead.'}
                print(messages.get(str(exc),str(exc)))
            session.save(log)
    except (EOFError,KeyboardInterrupt):
        print('\nStopped.')
    finally:
        session.save(log)
        print('\nSaved:',log)

if __name__=='__main__':main()
