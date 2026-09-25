"""Two owner journeys over a shared fictional product; no case outcome in model input."""
from pathlib import Path
from copy import deepcopy
import json
from rep_walkthrough import Walkthrough
WORLD=json.loads(Path(__file__).with_name('journey_world.json').read_text())
class JourneyWalkthrough(Walkthrough):
    def __init__(self,model):
        super().__init__(WORLD['case'],model)
    def advise(self):
        # Query identifiers must come from rep input, never the private world or model guesses.
        last_reset=max((i for i,h in enumerate(self.history) if h.get('type')=='query_scope_reset'),default=-1)
        reports=' '.join(h.get('text','') for h in self.history[last_reset+1:] if h.get('type') in {'rep_answer','rep_report'}).lower()
        for name,entry in WORLD['records'].items():
            if any(key in reports.split() or key in reports.replace(',',' ').replace('.',' ').split() for key in entry['required_ids']):
                self.sources[name]=deepcopy(entry['record'])
        return super().advise()
    def note(self,text):
        result=super().note(text)
        # Scope corrections must also retire identifiers used for past queries.
        self.history.insert(len(self.history)-1,{'type':'query_scope_reset'})
        return result
