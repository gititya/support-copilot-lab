from pathlib import Path
from copy import deepcopy
import json,sys,hashlib
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'trial'))
from rep_walkthrough import Walkthrough,load_key
from investigation import OpenAIModel
root=Path(__file__).parent;spec=json.loads((root/'worlds.json').read_text());previous=json.loads((root/'results.json').read_text());common=spec['common']
load_key();m=OpenAIModel(max_calls=14,budget=.30);out=[]
for row,world in zip(previous['results'],spec['worlds']):
 # Human reviewer inspected all three actual questions. They request the failed activity and symptoms.
 # Supply only the already-frozen scope answer, including known lookup identifiers; no diagnosis.
 case={'id':'challenge','sources':[{'id':'policy','description':'Read permitted support actions and access limits.'},{'id':'requests','description':'Look up requests once member, workspace and request IDs are known.'}],'questions':[{'id':'scope','text':'Who tried which activity, who succeeded, and what are the affected request IDs?'}],'stages':[{'event':{'text':common['opening'],'facts':{'report':common['opening']}},'reads':{'policy':{'status':'ok','text':common['policy'],'facts':{'support_policy':common['policy']}}}}]}
 w=Walkthrough(case,m);w.history=deepcopy(row['history']);w.calls=deepcopy(row['calls']);w.pending_question='clarify'
 w.answer(common['answer']);w.sources['requests']={'status':'ok','text':json.dumps(world['record']),'facts':deepcopy(world['record'])}
 result=w.advise();item={'world':world['id'],'first':row['initial'],'answer':common['answer'],'next':result,'history':w.history,'calls':w.calls,'progress':w.progress.snapshot()};out.append(item)
 checks=[]
 for c in w.calls:
  p=json.loads(c['prompt'].split('\nINPUT\n')[1]);read=any(h.get('type')=='read' and h.get('target')=='requests' for h in p['observed_history'])
  if not read and any(v in c['prompt'] for v in world['record'].values()):checks.append('early_record_leak')
  if world['expected'] in c['prompt']:checks.append('outcome_leak')
 item['leak_errors']=checks
 (root/'continued-results.json').write_text(json.dumps({'spec_sha256':previous['frozen_spec_sha256'],'source_hashes':previous['source_hashes'],'first_prompts_identical':previous['first_prompts_identical'],'method':'Human reviewer matched actual clarification questions to a frozen answer; no new case facts or expected outcomes supplied. Assistant instructions unchanged.','results':out,'new_model_calls':m.calls},indent=2)+'\n')
 print(json.dumps({'world':world['id'],'result':result.get('message'),'next':result.get('decision',{}).get('next'),'cause':result.get('decision',{}).get('cause'),'errors':result.get('errors'),'leaks':checks,'calls':len(w.calls)},ensure_ascii=False),flush=True)
