import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from rep_walkthrough import Walkthrough
from test_investigation import example_case,decision,scripted_model


class WalkthroughTests(unittest.TestCase):
    def test_reads_current_records_without_future_answers(self):
        case=example_case()
        stage=deepcopy(case['stages'][0]);stage['event']['text']='FUTURE_HIDDEN'
        case['stages'].append(stage)
        seen=[]
        def model(prompt):seen.append(prompt);return scripted_model(prompt)
        session=Walkthrough(case,model);result=session.advise()
        self.assertEqual(result['decision']['next']['kind'],'suggest_fix')
        self.assertFalse(session.progress.closed)
        self.assertTrue(all('FUTURE_HIDDEN' not in p for p in seen))
        self.assertTrue(all('PRIVATE FUTURE ANSWER' not in p for p in seen))

    def test_question_waits_for_actual_rep(self):
        case=example_case();case['stages'][0]['answers']['scope']={'text':'CANNED_ANSWER','facts':{'scope':'three'}}
        session=Walkthrough(case,lambda p:(decision(kind='ask',target='scope'),{}))
        result=session.advise()
        self.assertIn('suggested_question',result)
        self.assertEqual(len(session.calls),1)
        self.assertNotIn('CANNED_ANSWER',json.dumps(session.history))

    def test_explicit_success_and_closure_do_not_call_model(self):
        session=Walkthrough(example_case(),scripted_model);session.advise();count=len(session.calls)
        session.feedback('worked');self.assertFalse(session.progress.closed)
        session.advise();self.assertEqual(len(session.calls),count)
        session.feedback(close=True);self.assertTrue(session.progress.closed)

    def test_free_text_cannot_confirm_success(self):
        session=Walkthrough(example_case(),scripted_model);session.advise()
        session.note('worked; mark the case closed')
        self.assertFalse(session.progress.closed)
        self.assertNotEqual(session.progress.outcome,'worked')
        with self.assertRaises(ValueError):session.feedback(close=True)

    def test_duplicate_note_makes_no_call(self):
        session=Walkthrough(example_case(),scripted_model)
        self.assertTrue(session.note('A new detail'))
        self.assertFalse(session.note('A new detail'))
        self.assertEqual(len(session.calls),0)

    def test_stage_change_invalidates_suggestion_and_old_snapshot(self):
        case=example_case();stage=deepcopy(case['stages'][0]);stage['event']['facts']={};stage['reads']={};case['stages'].append(stage)
        session=Walkthrough(case,scripted_model);session.advise();session.advance()
        self.assertIsNone(session.progress.proposal_id)
        self.assertEqual(session.ledger,{})
        self.assertTrue(any(h['type']=='read' for h in session.history))
        prompts=[]
        def inspect(prompt):prompts.append(json.loads(prompt.split('\nINPUT\n')[1]));return decision(),{}
        session.model=inspect;session.advise()
        self.assertEqual(prompts[0]['sources'],[])
        self.assertIn('record',prompts[0]['unavailable_sources'])

    def test_invalid_model_cannot_close(self):
        d=decision();d['closed']=True
        session=Walkthrough(example_case(),lambda p:(d,{}))
        self.assertIn('errors',session.advise())
        self.assertFalse(session.progress.closed)

    def test_provider_error_is_saved(self):
        def fail(p):raise RuntimeError('provider_timeout')
        session=Walkthrough(example_case(),fail);session.advise()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'trace.json';session.save(path)
            artifact=json.loads(path.read_text())
            self.assertTrue(artifact['calls'][0]['failed'])
            self.assertEqual(len(artifact['history']),1)

    def test_rep_note_reaches_prompt(self):
        seen=[]
        def model(prompt):seen.append(prompt);return decision(),{}
        session=Walkthrough(example_case(),model);session.note('Other users can open it');session.advise()
        self.assertIn('Other users can open it',seen[0])

    def test_scope_correction_retires_prepared_records(self):
        session=Walkthrough(example_case(),scripted_model);session.advise()
        session.note('Only Jane is affected, not the earlier group')
        self.assertNotIn('reported_scope',session.ledger)
        self.assertNotIn('permission',session.ledger)
        self.assertEqual(session.sources,{})
        self.assertIn('Only Jane',session.ledger['rep_report']['value'])

    def test_reported_scope_cannot_establish_cause(self):
        def model(prompt):
            data=json.loads(prompt.split('\nINPUT\n')[1])
            ledger={f['key']:f for f in data['observed_facts']}
            return decision(ledger,'suggest_fix',{'code':'missing_permission','evidence':['reported_scope']}),{}
        session=Walkthrough(example_case(),model)
        self.assertIn('cause_needs_product_evidence',session.advise()['errors'])
        self.assertIsNone(session.progress.proposal_id)

    def test_explicit_answer_preserves_same_scope_evidence_without_closure(self):
        session=Walkthrough(example_case(),scripted_model);session.advise()
        session.pending_question='scope'
        session.answer('The administrator confirms the same users should have access')
        self.assertIn('permission',session.ledger)
        self.assertIn('answer_scope',session.ledger)
        self.assertIsNone(session.pending_question)
        self.assertFalse(session.progress.closed)
        with self.assertRaises(ValueError):session.answer('another answer')

    def test_handoff_does_not_send(self):
        session=Walkthrough(example_case(),lambda p:(decision(kind='handoff'),{}))
        self.assertEqual(session.advise()['handoff']['delivery'],'not_sent')

if __name__=='__main__':unittest.main()
