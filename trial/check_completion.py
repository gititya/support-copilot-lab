import json,sys
from pathlib import Path
r=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(r/'trial'))
from rep_walkthrough import Walkthrough,load_key
from investigation import OpenAIModel
from datetime import datetime
run_stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
load_key();m=OpenAIModel(max_calls=16,budget=.35)
cases=json.loads((r/'trial/completion_cases.json').read_text());out=[]
for case in cases:
 w=Walkthrough(case,m);result=w.advise()
 row={'case':case['id'],'first':result}
 if case['id']=='finish' and w.progress.proposal_id:
  w.feedback('worked');w.feedback(close=True);row['end']=w.progress.snapshot()
 if case['id']=='disprove':
  w.finding('The same monthly report remains blank in a fresh browser session. The rep has no report-service logs or further permitted diagnostics. The affected request IDs are REQ-31, REQ-32 and REQ-33, at 09:10 UTC.')
  row['after_result']=w.advise()
 if w.cached_advice and 'handoff' in w.cached_advice:row['accepted']=w.accept_handoff()
 row['calls']=w.calls;row['ledger']=w.ledger
 # Deliberately simple summary comparator gets the same currently observed facts, no future answers.
 prompt='Summarize this fictional support case for the rep. Separate known facts and unknowns. Do not advise a next step or invent a cause. Return JSON with only a summary string.\n'+json.dumps({'current_facts':list(w.ledger.values())})
 row['summary_baseline'],row['summary_meta']=m(prompt)
 out.append(row)
 path=r/'outputs/cop1'/('bounded-completion-'+run_stamp+'.json');path.write_text(json.dumps({'cases':out,'not_a_quality_benchmark':True,'model':m.model,'calls':m.calls,'estimated_cost_usd':m.estimated_cost},indent=2))
 print(case['id'],json.dumps({k:v for k,v in row.items() if k in ['first','after_result','end','summary_baseline']},ensure_ascii=False),flush=True)
print('Saved',path,'calls',m.calls,flush=True)
