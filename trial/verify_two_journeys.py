from pathlib import Path
import sys,json,datetime
r=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(r/'trial'))
from web_walkthrough import BrowserSession
from investigation import OpenAIModel
m=OpenAIModel(max_calls=20,budget=.40);results=[]
p=r/'outputs/cop1'/('two-journeys-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
for family in ['resolve_journey','escalate_journey']:
 s=BrowserSession(m);s.start(family);row={'journey':family,'steps':[]};results.append(row)
 def action(name,**kw):
  s.apply({'version':s.version,'action':name,'proposal_id':s.walk.progress.proposal_id,**kw});row['steps'].append({'action':name,'advice':s.result,'progress':s.walk.progress.snapshot()})
 try:
  action('advice');assert s.walk.pending_question,'Did not ask for missing details'
  action('answer',text='Three members cannot open W6. Five others opened it today. All three could open it yesterday. They see access denied. Request IDs T71, T72, T73.')
  assert s.result.get('decision',{}).get('next',{}).get('kind')=='suggest_fix','No supported fix proposed'
  assert not s.walk.progress.closed
  if family=='resolve_journey':
   action('worked');assert not s.walk.progress.closed;action('close');assert s.walk.progress.closed
  else:
   action('failed');action('finding',text='The administrator refreshed the cache. All three retried and now see a blank workspace page. Retry request IDs T74, T75, T76.')
   assert 'handoff' in s.result,'No handoff after failed fix and server error'
   assert s.result['decision']['cause'] is None
   action('accept_handoff');assert s.result['handoff']['delivery']=='not_sent';assert not s.walk.progress.closed
  row['passed']=True
 except Exception as e:row['passed']=False;row['error']=str(e)
 finally:
  row['calls']=s.walk.calls;row['history']=s.walk.history;s.walk.save(s.log)
  p.write_text(json.dumps({'results':results,'calls':m.calls,'not_a_quality_benchmark':True},indent=2)+'\n')
 print(family,row['passed'],row.get('error',''),flush=True)
 for st in row['steps']:print(st['action'],(st['advice'] or {}).get('message',''),flush=True)
print('EVIDENCE',p,flush=True)
