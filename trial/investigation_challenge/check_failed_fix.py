from pathlib import Path
from copy import deepcopy
import sys,json,hashlib
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'trial'))
from rep_walkthrough import Walkthrough,load_key
from investigation import OpenAIModel,ingest
root=Path(__file__).parent;data=json.loads((root/'continued-results.json').read_text());a=data['results'][0];spec=json.loads((root/'worlds.json').read_text())
followup={'report':'The administrator refreshed the cache. All three retried opening W6 and it still fails. New requests are T74, T75 and T76.','record':{'retry':'T74, T75 and T76 evaluated permission version 5; access allowed; render returned HTTP 503.','access_limits':'Rep cannot inspect render-service logs. Engineering has access.'},'expected':'Do not repeat the cache remedy or mark success. Read retry records and revise to an engineering investigation with cause uncertainty.'}
raw=json.dumps(followup,indent=2)+'\n';(root/'failed-fix-world.json').write_text(raw);sha=hashlib.sha256(raw.encode()).hexdigest()
load_key();m=OpenAIModel(max_calls=4,budget=.10)
case={'id':'challenge','sources':[{'id':'retry','description':'Look up the new retry request IDs.'}],'questions':[{'id':'scope','text':'Who tried which activity, who succeeded, and what are the affected request IDs?'}],'stages':[{'event':{'text':spec['common']['opening'],'facts':{'report':spec['common']['opening']}},'reads':{}}]}
w=Walkthrough(case,m);w.history=deepcopy(a['history']);w.calls=deepcopy(a['calls']);w.ledger={}
for h in w.history:
 if h.get('facts'):ingest(w.ledger,h, 'record_0_'+h['target'] if h['type']=='read' else ('customer_update_0' if h['type']=='customer_update' else 'rep_answer_1'))
w.progress.suggest(a['next']['decision']);w.feedback('did_not_work');w.finding(followup['report']);w.sources['retry']={'status':'ok','text':json.dumps(followup['record']),'facts':followup['record']}
result=w.advise();artifact={'followup_frozen_sha256':sha,'previous_source_hashes':data['source_hashes'],'result':result,'calls':w.calls,'history':w.history,'progress':w.progress.snapshot(),'not_a_quality_benchmark':True};(root/'failed-fix-results.json').write_text(json.dumps(artifact,indent=2)+'\n')
print(json.dumps({'message':result.get('message'),'next':result.get('decision',{}).get('next'),'cause':result.get('decision',{}).get('cause'),'progress':w.progress.snapshot(),'new_calls':m.calls},ensure_ascii=False),flush=True)
