import json
import unittest
from rep_walkthrough import Walkthrough
from test_investigation import example_case,decision,scripted_model


class FocusTests(unittest.TestCase):
    def test_same_input_reuses_advice_and_keeps_question(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='ask',target='scope'),{}))
        first=w.advise();second=w.advise()
        self.assertEqual(first['message'],second['message'])
        self.assertTrue(second['reused_advice']);self.assertEqual(len(w.calls),1)
        self.assertEqual(w.pending_question,'scope')

    def test_real_update_invalidates_cache(self):
        w=Walkthrough(example_case(),lambda p:(decision(),{}))
        w.advise();w.note('A new finding');w.advise()
        self.assertEqual(len(w.calls),2)

    def test_custom_scope_never_offers_retired_records(self):
        seen=[]
        def model(p):seen.append(json.loads(p.split('\nINPUT\n')[1]));return decision(),{}
        w=Walkthrough(example_case(),model);w.note('A function fails rather than login');w.advise()
        self.assertEqual(seen[0]['sources'],[])
        self.assertIn('record',seen[0]['unavailable_sources'])

    def test_partial_answer_allows_narrow_followup_not_same_broad_question(self):
        seen=[]
        def model(p):
            payload=json.loads(p.split('\nINPUT\n')[1]);seen.append(payload)
            if len(seen)==1:return decision(kind='ask',target='scope'),{}
            if len(seen)==2:return decision(kind='ask',target='scope'),{}
            d=decision(kind='ask',target='clarify');d['rep_message']='Which of those people tried the same activity successfully?';return d,{}
        w=Walkthrough(example_case(),model);w.advise();w.answer('Three people reported it');result=w.advise()
        self.assertNotIn('scope',[q['id'] for q in seen[1]['questions']])
        self.assertIn('clarify',[q['id'] for q in seen[1]['questions']])
        self.assertIn('focus_rejection',w.calls[1]);self.assertEqual(w.pending_question,'clarify')
        self.assertIn('successfully',result['suggested_question'])

    def test_new_scope_does_not_reuse_old_completed_question(self):
        seen=[]
        def model(p):seen.append(json.loads(p.split('\nINPUT\n')[1]));return decision(kind='ask',target='scope'),{}
        w=Walkthrough(example_case(),model);w.advise();w.answer('Three people');w.note('Correction: a different group');w.advise()
        self.assertIn('scope',[q['id'] for q in seen[-1]['questions']])

    def test_unproven_fix_must_be_labelled_diagnostic(self):
        calls=[]
        def model(p):
            calls.append(p)
            d=decision(kind='suggest_fix' if len(calls)==1 else 'suggest_check')
            d['rep_message']='With rep approval, compare this page in a private window to test whether saved browser state is involved.'
            return d,{}
        w=Walkthrough(example_case(),model);result=w.advise()
        self.assertEqual(result['decision']['next']['kind'],'suggest_check')
        self.assertIn('focus_rejection',w.calls[0]);self.assertFalse(w.progress.closed)
        self.assertEqual(w.progress.outcome,'not_tried')

    def test_persistent_unproven_fix_cannot_create_proposal(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='suggest_fix'),{}))
        self.assertFalse(w.advise()['recommendation_available'])
        self.assertIsNone(w.progress.proposal_id)

    def test_distinct_clarifications_preserve_both_answers(self):
        def model(p):
            d=decision(kind='ask',target='clarify')
            d['rep_message']='Which browsers failed?' if 'answer_clarify_' in p else 'Which feature failed?'
            return d,{}
        w=Walkthrough(example_case(),model)
        w.advise();w.answer('The monthly report chart')
        w.advise();w.answer('It happens in two browsers')
        values=[v['value'] for k,v in w.ledger.items() if k.startswith('answer_clarify_')]
        self.assertEqual(values,['The monthly report chart','It happens in two browsers'])

    def test_diagnostic_finding_does_not_verify_recovery(self):
        w=Walkthrough(example_case(),lambda p:(decision(kind='suggest_check'),{}));w.advise()
        w.note('The diagnostic check reproduced the failure')
        self.assertNotEqual(w.progress.outcome,'worked');self.assertFalse(w.progress.closed)
        w.advise()
        w.feedback('worked');self.assertFalse(w.progress.closed)
        w.feedback(close=True);self.assertTrue(w.progress.closed)

if __name__=='__main__':unittest.main()
