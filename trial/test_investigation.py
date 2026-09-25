import json
import unittest
from copy import deepcopy
from investigation import (UpdateGate, public_payload, make_prompt, validate_decision,
                           score, run_case, ingest)


def example_case():
    return {"id": "C00", "title": "PRIVATE FUTURE ANSWER", "split": "development", "family": "access",
            "sources": [{"id": "record", "description": "Read the access record", "oracle": "PRIVATE"}],
            "questions": [{"id": "scope", "text": "Which users?", "oracle": "PRIVATE"}],
            "stages": [{"event": {"text": "Cannot open the workspace", "facts": {"reported_scope": "one"}},
                        "reads": {"record": {"status": "ok", "text": "Access was denied: permission missing",
                                             "facts": {"permission": "missing", "error": "permission denied"}}},
                        "answers": {}, "expected": {"kinds": ["suggest_fix"], "cause": "missing_permission",
                            "evidence": {"permission": "missing", "error": "permission denied"},
                            "required_facts": ["reported_scope", "permission"], "avoid_questions": ["scope"],
                            "useful_reads": ["record"]}}]}


def decision(ledger=None, kind="wait", cause=None, target=""):
    return {"facts": list((ledger or {}).values()), "hypotheses": [], "open_questions": [],
            "next": {"kind": kind, "target": target, "reason": "Inspect the missing evidence"},
            "cause": cause, "rep_message": "Wait for the pending record."}


def scripted_model(prompt):
    payload = json.loads(prompt.split("\nINPUT\n", 1)[1])
    ledger = {x["key"]: x for x in payload["observed_facts"]}
    if "permission" not in ledger:
        out = decision(ledger, "read", target="record")
    else:
        out = decision(ledger, "suggest_fix", {"code": "missing_permission", "evidence": ["permission", "error"]})
    return out, {"duration_ms": 1, "usage": {}, "estimated_cost_usd": 0, "mock": True}


class InvestigationTests(unittest.TestCase):
    def test_future_and_oracle_not_in_model_payload(self):
        case = example_case()
        case["stages"].append({"event": {"text": "FUTURE SECRET", "facts": {}}})
        payload = public_payload(case, case["stages"][0]["event"], {}, [], None, "investigation", [])
        prompt = make_prompt(payload, "investigation")
        for forbidden in ("PRIVATE", "FUTURE SECRET", '"expected"', '"split"', '"oracle"', '"reads"'):
            self.assertNotIn(forbidden, prompt)
        self.assertNotIn("permission denied", prompt)

    def test_choice_is_needed_to_obtain_record(self):
        r = run_case(example_case(), scripted_model)
        self.assertTrue(r["passed"])
        self.assertEqual(r["stages"][0]["reads"], ["record"])
        self.assertNotIn('"value": "missing"', r["calls"][0]["prompt"])
        self.assertIn('"value": "missing"', r["calls"][1]["prompt"])

    def test_invented_fact_fails_even_if_expected_facts_present(self):
        case = example_case(); d = decision()
        d["facts"] = [{"key": "invented", "value": "yes", "source": "R0"}]
        self.assertIn("unsupported_fact", validate_decision(d, {}, case))

    def test_unresolved_expected_does_not_pass_invented_cause(self):
        case = example_case()
        ledger = {"permission": {"key": "permission", "value": "missing", "source": "R0"}}
        d = decision(ledger, "handoff", {"code": "missing_permission", "evidence": ["permission"]})
        grade = score(d, ledger, {"kinds": ["handoff"], "cause": None}, case, [], [])
        self.assertFalse(grade["checks"]["expected_outcome"])
        self.assertFalse(grade["checks"]["cause_supported_now"])

    def test_partial_product_evidence_does_not_prove_cause(self):
        case = example_case()
        ledger = {"permission": {"key": "permission", "value": "missing", "source": "R0"}}
        d = decision(ledger, "suggest_fix", {"code": "missing_permission", "evidence": ["permission"]})
        grade = score(d, ledger, case["stages"][0]["expected"], case, [], [])
        self.assertFalse(grade["checks"]["cause_supported_now"])

    def test_correction_invalidates_old_fact_source(self):
        ledger = {}; ingest(ledger, {"facts": {"scope": "all"}}, "E0")
        old = decision(deepcopy(ledger))
        ingest(ledger, {"facts": {"scope": "one"}}, "E1")
        self.assertIn("unsupported_fact", validate_decision(old, ledger, example_case()))

    def test_explicit_null_replaces_old_cause(self):
        case = example_case()
        case["stages"].append({"event": {"text": "Correction: the permission is present", "facts": {"permission": "present"}},
                               "reads": {}, "answers": {}, "expected": {"kinds": ["handoff"], "cause": None}})
        def model(prompt):
            p = json.loads(prompt.split("\nINPUT\n")[1]); ledger = {x["key"]:x for x in p["observed_facts"]}
            if ledger.get("permission", {}).get("value") == "present":return decision(ledger,"handoff"), {}
            return scripted_model(prompt)
        r = run_case(case, model)
        self.assertTrue(r["passed"])
        self.assertIsNone(r["stages"][-1]["decision"]["cause"])

    def test_unlisted_tool_and_actuation_rejected(self):
        for kind,target in [("read","unlisted"),("delete","record"),("suggest_fix","record")]:
            self.assertTrue(validate_decision(decision(kind=kind,target=target),{},example_case()))

    def test_repeated_source_is_visible_failure(self):
        def model(prompt):return decision(kind="read",target="record"),{}
        r = run_case(example_case(), model)
        self.assertFalse(r["passed"])
        self.assertIn("repeated_request",r["stages"][0]["grade"]["errors"])

    def test_provider_error_stays_in_denominator(self):
        def model(prompt):raise RuntimeError("provider_network_or_timeout")
        r = run_case(example_case(),model)
        self.assertFalse(r["passed"])
        self.assertEqual(len(r["stages"]),1)
        self.assertTrue(r["calls"][0]["failed"])

    def test_bad_json_shapes_are_failures_not_crashes(self):
        case=example_case()
        for bad in [None,[],"bad",{"facts":None,"next":None}]:
            grade=score(bad,{},case["stages"][0]["expected"],case,[],[])
            self.assertFalse(grade["passed"])

    def test_unhashable_model_fields_are_rejected(self):
        c=example_case()
        bad=decision(); bad["facts"]=[{"key":[],"value":"x","source":"x"}]
        self.assertFalse(score(bad,{},c["stages"][0]["expected"],c,[],[])["passed"])
        bad=decision(cause={"code":"missing_permission","evidence":[{}]})
        self.assertTrue(validate_decision(bad,{},c))
        bad=decision(kind=[]); self.assertTrue(validate_decision(bad,{},c))

    def test_bad_cause_evidence_types_fail_with_otherwise_correct_cause(self):
        c=example_case(); ledger={}
        ingest(ledger,{"facts":{"permission":"missing","error":"permission denied"}},"R0")
        for value in [None,False,0,1,1.5,{},"permission"]:
            d=decision(ledger,"suggest_fix",{"code":"missing_permission","evidence":value})
            self.assertFalse(score(d,ledger,c["stages"][0]["expected"],c,[],[])["passed"])

    def test_exact_required_fields(self):
        d=decision(); d.pop("cause")
        self.assertTrue(validate_decision(d,{},example_case()))
        for value in [None,0,[],{}]:
            self.assertTrue(validate_decision(decision(target=value),{},example_case()))

    def test_early_unsupported_cause_cannot_be_hidden_by_final_success(self):
        def model(prompt):
            out,meta=scripted_model(prompt)
            if out["next"]["kind"]=="read":
                out["cause"]={"code":"missing_permission","evidence":["reported_scope"]}
            return out,meta
        r=run_case(example_case(),model)
        self.assertFalse(r["passed"])
        self.assertIn("unsupported_intermediate_cause",r["stages"][0]["grade"]["errors"])

    def test_timing_probes_score_duplicates_and_count_failed_wait(self):
        calls=0
        def model(prompt):
            nonlocal calls
            calls+=1
            if calls==3:raise RuntimeError("timeout")
            return scripted_model(prompt)
        r=run_case(example_case(),model,timing="every_update",duplicate_updates=1)
        self.assertFalse(r["all_calls_succeeded"])
        self.assertFalse(r["passed"])
        self.assertIn("duration_ms",r["calls"][-1])
        r=run_case(example_case(),scripted_model,timing="every_update",duplicate_updates=1,partial_updates=True)
        self.assertEqual(sum(x.get("partial",False) for x in r["calls"]),1)
        self.assertIn("grade",r["calls"][-1])

    def test_duplicate_gate_preserves_changes_and_partial_commit(self):
        gate=UpdateGate(); event={"text":"access fails","facts":{"scope":"all"}}
        self.assertEqual(gate.observe(event),"changed")
        gate.active_advice="old"
        self.assertEqual(gate.observe(event),"duplicate")
        changed={"text":"access fails","facts":{"scope":"one"}}
        self.assertEqual(gate.observe(changed),"changed")
        self.assertIsNone(gate.active_advice)
        self.assertEqual(gate.observe(changed,False),"partial_wait")
        self.assertEqual(gate.observe(changed),"changed")

    def test_duplicate_suppression_changes_calls_not_first_decision(self):
        dedup=run_case(example_case(),scripted_model,duplicate_updates=2)
        eager=run_case(example_case(),scripted_model,timing="every_update",duplicate_updates=2)
        self.assertEqual(len(dedup["calls"]),2)
        self.assertEqual(len(eager["calls"]),4)
        self.assertEqual(dedup["stages"],eager["stages"])

    def test_baseline_has_same_records_without_previous_model_state(self):
        c=example_case(); event=c["stages"][0]["event"]
        a=public_payload(c,event,{},[],{"cause":"old"},"investigation",[])
        b=public_payload(c,event,{},[],{"cause":"old"},"baseline",[])
        a.pop("previous_investigation")
        self.assertEqual(a,b)

    def test_investigation_uses_compact_state_baseline_uses_history(self):
        c=example_case(); event=c["stages"][0]["event"]
        history=[{"text":"old"},{"text":"new"}]
        a=public_payload(c,event,{},history,{"cause":None},"investigation",[])
        b=public_payload(c,event,{},history,None,"baseline",[])
        self.assertEqual(a["observed_history"],history[-1:])
        self.assertEqual(b["observed_history"],history)
        self.assertEqual(a["sources"],b["sources"])
        self.assertEqual(a["observed_facts"],b["observed_facts"])

    def test_record_change_announced_and_old_record_removed(self):
        c=example_case()
        second=deepcopy(c["stages"][0]); second["event"]={"text":"New update","facts":{}}
        second["reads"]["record"]["facts"]["permission"]="present"
        second["expected"]={"kinds":["wait"],"cause":None}
        c["stages"].append(second)
        inspected=[]
        def model(prompt):
            p=json.loads(prompt.split("\nINPUT\n")[1])
            if p["event"]["text"]=="New update":
                inspected.append(p)
                return decision({x["key"]:x for x in p["observed_facts"]}),{}
            return scripted_model(prompt)
        run_case(c,model)
        self.assertEqual(inspected[0]["sources"][0]["revision"],2)
        self.assertNotIn("permission",{x["key"] for x in inspected[0]["observed_facts"]})

    def test_question_with_no_answer_returns_pending_without_further_reads(self):
        c=example_case()
        c["stages"][0]["expected"]={"kinds":["ask"],"cause":None}
        def model(prompt):return decision(kind="ask",target="scope"),{}
        r=run_case(c,model)
        self.assertEqual(len(r["calls"]),1)
        self.assertTrue(r["passed"])


if __name__ == '__main__':
    unittest.main()
