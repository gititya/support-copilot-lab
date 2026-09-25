"""Rep-owned outcome record. Model output cannot confirm success or close a case."""
from copy import deepcopy
import hashlib
import json


class CaseProgress:
    def __init__(self):
        self.proposal_id = None
        self.proposal = None
        self.outcome = "not_tried"
        self.closed = False
        self.history = []
        self.sequence = 0

    def snapshot(self):
        return {"proposal_id": self.proposal_id, "proposal": deepcopy(self.proposal),
                "outcome": self.outcome, "closed": self.closed,
                "status": "closed" if self.closed else "verified_open" if self.outcome == "worked"
                else "investigating" if self.outcome == "did_not_work" or not self.proposal_id
                else "awaiting_rep_verification"}

    def suggest(self, decision):
        if decision.get("next", {}).get("kind") not in {"suggest_fix", "suggest_check"}:
            return
        proposal = {"next": deepcopy(decision["next"]), "cause": deepcopy(decision.get("cause")),
                    "rep_message": decision["rep_message"]}
        if proposal == self.proposal:
            return
        self.sequence += 1
        self.proposal_id = "fix-" + str(self.sequence) + "-" + hashlib.sha256(
            json.dumps(proposal, sort_keys=True).encode()).hexdigest()[:10]
        self.proposal = proposal
        self.outcome, self.closed = "not_tried", False
        self.history.append({"type": "suggested", **self.snapshot()})

    def feedback(self, control):
        # Only the host's rep-control channel calls this; never parse transcript or model claims as control.
        if not isinstance(control, dict) or set(control) - {"proposal_id", "outcome", "close"}:
            raise ValueError("invalid_rep_control")
        if not self.proposal_id or control.get("proposal_id") != self.proposal_id:
            raise ValueError("stale_or_missing_proposal")
        outcome = control.get("outcome", self.outcome)
        if not isinstance(outcome, str) or outcome not in {"worked", "did_not_work", "not_tried", "unclear"}:
            raise ValueError("invalid_rep_outcome")
        close = control.get("close", False)
        if not isinstance(close, bool):
            raise ValueError("invalid_rep_close")
        if close and outcome != "worked":
            raise ValueError("closure_requires_rep_verified_success")
        self.outcome, self.closed = outcome, close
        self.history.append({"type": "rep_feedback", **self.snapshot()})

    def new_evidence(self):
        # A new problem update invalidates the old confirmation target, not the audit trail.
        if self.proposal_id:
            self.history.append({"type": "superseded_by_evidence", **self.snapshot()})
        self.proposal_id, self.proposal = None, None
        self.outcome, self.closed = "unclear", False
