from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'trial'))
from rep_walkthrough import Walkthrough,load_key
from investigation import OpenAIModel
root=Path(__file__).parent;raw=(root/'worlds.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==(root/'FROZEN.sha256').read_text().strip()
spec=json.loads(raw);common=spec['common'];load_key();model=OpenAIModel(max_calls=20,budget=.40)
results=[];first_prompts=[]
for world in spec['worlds']:
 case={'id':'challenge','sources':[{'id':'policy','description':'Read permitted support actions and access limits.'},{'id':'requests','description':'Look up requests once member, workspace and request IDs are known.'}], 'questions':[{'id':'scope','text':'Who tried which activity, who succeeded, and what are the affected request IDs?'}], 'stages':[{'event':{'text':common['opening'],'facts':{'report':common['opening']}},'reads':{'policy':{'status':'ok','text':common['policy'],'facts':{'support_policy':common['policy']}}}}]}
 w=Walkthrough(case,model);first=w.advise();first_prompts.append(w.calls[0]['prompt'])
 row={'world':world['id'],'initial':first,'observations':[]};results.append(row)
 # Do not use a model to fabricate answers to arbitrary questions. Only the frozen listed scope question has an automatic response.
 if w.pending_question=='scope':
  w.answer(common['answer']);row['customer_answer']=common['answer']
  w.sources['requests']={'status':'ok','text':json.dumps(world['record']),'facts':deepcopy(world['record'])}
  row['after_scope']=w.advise()
 else:row['stopped']='No listed scope question: requires human review, not an invented answer.'
 row['calls']=w.calls;row['history']=w.history;row['progress']=w.progress.snapshot()
 before_read=True;leaks=[]
 for call in w.calls:
  payload=json.loads(call['prompt'].split('\nINPUT\n')[1])
  read=any(h.get('type')=='read' and h.get('target')=='requests' for h in payload['observed_history'])
  if not read:
   for value in world['record'].values():
    if value in call['prompt']:leaks.append('record visible before read')
  if world['expected'] in call['prompt']:leaks.append('expected outcome leaked')
 row['input_leak_checks']=leaks
 artifact={'frozen_spec_sha256':hashlib.sha256(raw).hexdigest(),'source_hashes':{f:hashlib.sha256((r/'trial'/f).read_bytes()).hexdigest() for f in ['rep_walkthrough.py','investigation.py','SUPPORT_RULES.md']},'results':results,'first_prompts_identical':len(set(first_prompts))==1,'calls':model.calls,'not_a_quality_benchmark':True}
 (root/'results.json').write_text(json.dumps(artifact,indent=2)+'\n')
 print(json.dumps({'world':world['id'],'first':first.get('message'),'kind':first.get('decision',{}).get('next'), 'after':row.get('after_scope',{}).get('message'),'after_kind':row.get('after_scope',{}).get('decision',{}).get('next'),'stopped':row.get('stopped'),'leaks':leaks},ensure_ascii=False),flush=True)
print('TOTAL',model.calls,'same_initial_prompts',len(set(first_prompts))==1,flush=True)
