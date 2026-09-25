import json
import unittest
from rep_walkthrough import Walkthrough
from web_walkthrough import BrowserSession
from test_investigation import example_case, decision, scripted_model

class CompletionTests(unittest.TestCase):
    def test_diagnostic_result_preserves_records_and_prevents_repeat_read(self):
        w=Walkthrough(example_case(),scripted_model);w.advise()
        old=dict(w.ledger);w.finding('A fresh browser session has the same failure')
        self.assertTrue(all(w.ledger[k]==v for k,v in old.items()))
        self.assertIsNone(w.progress.proposal_id)
        seen=[]
        def model(p):seen.append(json.loads(p.split('\nINPUT\n')[1]));return decision(kind='handoff'),{}
        w.model=model;w.advise()
        self.assertEqual(seen[0]['sources'],[])
        self.assertIn('fresh browser',str(seen[0]['observed_facts']))
        self.assertFalse(w.progress.closed)

    def test_successive_findings_are_not_overwritten(self):
        w=Walkthrough(example_case(),scripted_model)
        w.finding('Diagnostic A failed');w.finding('Diagnostic B failed')
        self.assertIn('Diagnostic A failed',str(w.ledger));self.assertIn('Diagnostic B failed',str(w.ledger))

    def test_correction_still_retires_evidence(self):
        w=Walkthrough(example_case(),scripted_model);w.advise();w.finding('Same issue elsewhere')
        w.note('Correction: different users and activity')
        self.assertEqual(set(w.ledger),{'rep_report'});self.assertFalse(w.sources)

    def test_accepted_handoff_stops_calls_but_is_not_delivery_or_recovery(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='handoff'),{}));w.advise()
        accepted=w.accept_handoff();n=len(w.calls)
        self.assertFalse(accepted['handoff']['rep_review_required'])
        self.assertEqual(w.advise()['handoff']['delivery'],'not_sent')
        self.assertEqual(len(w.calls),n);self.assertFalse(w.progress.closed)
        w.finding('New diagnostic supplied')
        with self.assertRaises(ValueError):w.accept_handoff()

    def test_repeat_question_cannot_continue_interrogation(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='ask',target='clarify'),{}))
        w.advise();w.answer('The monthly report fails')
        r=w.advise();self.assertFalse(r['recommendation_available']);self.assertIsNone(w.pending_question)

    def test_http_action_preserves_evidence_for_finding(self):
        s=BrowserSession(lambda p:(decision(),{}));s.walk=Walkthrough(example_case(),scripted_model)
        s.apply({'version':0,'action':'advice'})
        s.apply({'version':1,'action':'finding','text':'The same failure occurred on retry'})
        self.assertIn('permission',s.walk.ledger)
        self.assertNotEqual(s.walk.progress.outcome,'worked')

    def test_http_handoff_acceptance_requires_current_version(self):
        s=BrowserSession(lambda p:(decision(kind='handoff'),{}));s.apply({'version':0,'action':'advice'})
        with self.assertRaises(ValueError):s.apply({'version':0,'action':'accept_handoff'})
        s.apply({'version':1,'action':'accept_handoff'})
        self.assertTrue(s.result['handoff']['accepted_by_rep'])

if __name__=='__main__':unittest.main()
