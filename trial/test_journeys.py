import json,unittest
from journeys import JourneyWalkthrough,WORLD
from test_investigation import decision
class JourneyTests(unittest.TestCase):
 def test_opening_has_only_report_and_account(self):
  seen=[]
  def model(p):seen.append(p);return decision(kind='ask',target='clarify'),{}
  w=JourneyWalkthrough(model);w.advise();p=json.loads(seen[0].split('\nINPUT\n')[1])
  self.assertEqual({f['key'] for f in p['observed_facts']},{'customer_report','account'})
  for entry in WORLD['records'].values():self.assertNotIn(entry['record']['text'],seen[0])
  self.assertEqual([s['id'] for s in p['sources']],['policy'])
 def test_unrelated_update_does_not_unlock_requests(self):
  w=JourneyWalkthrough(lambda p:(decision(),{}));w.finding('I have no request IDs');w.advise();self.assertNotIn('requests',w.sources)
 def test_matching_id_unlocks_only_matching_lookup(self):
  seen=[]
  def model(p):seen.append(p);return decision(),{}
  w=JourneyWalkthrough(model);w.finding('Failed request T71.');w.advise()
  self.assertIn('requests',w.sources);self.assertNotIn('retry',w.sources)
  self.assertNotIn(WORLD['records']['requests']['record']['text'],seen[0])
 def test_correction_retires_previous_identifiers(self):
  w=JourneyWalkthrough(lambda p:(decision(),{}));w.finding('T71');w.advise();w.note('Correction: another account entirely');w.advise();self.assertNotIn('requests',w.sources)
 def test_case_selection_does_not_supply_ending_to_model(self):
  from web_walkthrough import BrowserSession
  prompts=[]
  def model(p):prompts.append(p);return decision(kind='ask',target='clarify'),{}
  for family in ['resolve_journey','escalate_journey']:
   s=BrowserSession(model);s.start(family);s.apply({'version':0,'action':'advice'})
  self.assertEqual(prompts[0],prompts[1])
if __name__=='__main__':unittest.main()
