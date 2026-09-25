"""Render saved controlled trial evidence; never makes model calls."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |',
                      *['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in rows]])


def median(values):
    return f'{statistics.median(values) / 1000:.2f}s' if values else 'not measured'


def render(root):
    evidence = root / 'outputs/cop1'
    trials = [json.loads((evidence / name).read_text()) for name in ['heldout-access-v3.json', 'heldout-integration-v3.json']]
    timing = json.loads((evidence / 'timing-v3.json').read_text())
    for trial in [*trials, timing]:
        if len(trial['results']) != 2 * len(trial['selected_cases']):
            raise ValueError('Run is incomplete; do not render a final report')
    results = [r for trial in trials for r in trial['results']]
    lanes = defaultdict(list)
    for r in results:
        lanes[r['lane']].append(r)
    rows = []
    for lane in ['investigation', 'baseline']:
        selected = lanes[lane]
        stages = [s for r in selected for s in r['stages']]
        calls = [c for r in selected for c in r['calls']]
        waits = [sum(c.get('duration_ms', 0) for c in r['calls'] if c['stage'] == s['index']) for r in selected for s in r['stages']]
        rows.append([lane, len(selected), f"{sum(s['grade']['passed'] for s in stages)}/{len(stages)}",
            f"{sum(s['grade']['checks']['expected_outcome'] and s['grade']['checks']['cause_supported_now'] for s in stages)}/{len(stages)}",
            len(calls), sum(c.get('failed', False) for c in calls),
            sum(s['grade']['question_requests'] for s in stages),
            sum(len(s['grade'].get('observation_warnings', [])) for s in stages),
            median(waits), f"${sum(c.get('estimated_cost_usd', 0) for c in calls):.6f}"])
    lines = ['# Copilot investigation and timing trial — 10 September 2026', '',
        'This report reads frozen synthetic trial artifacts. It is not a rep outcome study or a live helpdesk integration.', '',
        '## Investigation comparison', '',
        'The investigation version carries compact previous state, current observed facts and the latest observation. The baseline sees the full observed history and current facts. Both use the same model, source/question menus and basic support rules. Product data arrives only after a requested read; host-supplied source revisions invalidate older records.', '',
        table(['Approach', 'Cases', 'All checks pass (stages)', 'Supported expected outcome (stages)', 'Model calls', 'Provider errors', 'Questions requested', 'Answers adding no fact', 'Median model wait per update', 'Usage cost estimate'], rows), '',
        'An all-check pass requires supported structured facts, an evidence-backed cause, the authored outcome, retained required facts and no recorded request errors. Supported expected outcome is narrower: it does not imply good wording, efficient investigation or customer recovery. A simulated answer adding no fact is a warning, not proof that the question was unreasonable.', '',
        'The model is `gpt-5.6-luna`, low reasoning, direct OpenAI. Provider wait includes multiple calls within an update and failed-request wait where recorded. Sources are in-memory fixtures; these are not customer response-time benchmarks. Runs for the two families and timing experiment overlapped, so provider contention may affect latency. Costs are estimates from returned token usage and recorded prices, not invoices.', '',
        '## Case-level results', '',
        table(['Case', 'Family', 'Approach', 'Passed stages', 'Final investigation action', 'Cause', 'Recorded errors'], [
            [r['case_id'], r['family'], r['lane'], f"{sum(s['grade']['passed'] for s in r['stages'])}/{len(r['stages'])}",
             r['stages'][-1]['decision'].get('next', {}).get('kind'), r['stages'][-1]['decision'].get('cause'),
             ', '.join(sorted({e for s in r['stages'] for e in s['grade']['errors']})) or 'none'] for r in results]), '',
        '## Timing: redundant request overhead', '',
        'Two development cases were replayed with one unfinished fragment before each committed update and one exact repeat afterwards. The eager version called the model on these extras; the gated version held fragments and suppressed repeats. Extra calls were advice-only: their proposed reads were not executed, so this is not a comparison of complete interactive sessions.', '',
        table(['Case', 'Mode', 'Committed stages passed', 'Total calls', 'Partial calls', 'Duplicate calls', 'Duplicate grades failed', 'All provider calls succeeded', 'Total provider wait'], [
            [r['case_id'], r['timing'], f"{sum(s['grade']['passed'] for s in r['stages'])}/{len(r['stages'])}",len(r['calls']),
             sum(c.get('partial',False) for c in r['calls']),sum(c.get('duplicate',False) for c in r['calls']),
             sum(c.get('duplicate',False) and not c.get('grade',{}).get('passed',False) for c in r['calls']),r['all_calls_succeeded'],
             f"{sum(c.get('duration_ms',0) for c in r['calls'])/1000:.2f}s"] for r in timing['results']]), '',
    ]
    extras = [c for r in timing['results'] if r['timing'] == 'every_update' for c in r['calls'] if c.get('partial') or c.get('duplicate')]
    lines += [f"The eager runs made {len(extras)} extra fragment/repeat requests, taking {sum(c.get('duration_ms',0) for c in extras)/1000:.2f}s of accumulated provider wait and an estimated ${sum(c.get('estimated_cost_usd',0) for c in extras):.6f}. These are directly observed overhead calls, not a promise of that saving on normal customer traffic.", '',
        'Every committed update still runs. Changed record facts and query scope are not treated as duplicates. The gate withdraws prior advice when a partial correction or new committed update begins. There is no learned semantic trigger, live audio or live streaming UI.', '',
        '## Limits and provenance', '',
        '- Six evaluation cases are separate from two development cases. They are author-designed synthetic cases, not independently collected customer cases. The final runner and case hashes were frozen before evaluation; no post-result tuning is included.',
        '- Raw prompts exclude future stages, scenario explanations, descriptive case titles, split and expected answers. The menu still limits the problem to four cause categories and listed questions/records; this does not prove open-ended investigation.',
        '- The evaluator checks structured assertions against observed source values and authored causal evidence. Free-text advice and hypotheses require human review. A valid source citation alone does not guarantee that the prose follows from it.',
        '- A terminal resolve action identifies a diagnosis for the rep. It does not change the product, confirm customer recovery or prove a receiving person read a handoff.',
        '- The two earlier development runs and their inputs are preserved. Their scores use earlier prompts/expectations and must not be pooled with the frozen evaluation.', '',
        'Sources: [access results](../outputs/cop1/heldout-access-v3.json), [integration results](../outputs/cop1/heldout-integration-v3.json), [timing results](../outputs/cop1/timing-v3.json), [frozen inputs](../outputs/cop1/frozen-inputs-v3.json).', '',
        '## Saved rep advice for review', '']
    for r in results:
        lines += [f"### {r['case_id']} — {r['family']} — {r['lane']}", '']
        for s in r['stages']:
            decision = s['decision']
            misses = [k for k,v in s['grade']['checks'].items() if not v]
            lines += [f"**Update {s['index']+1}:** {decision.get('rep_message','No usable response.')}", '',
                      f"Requested records: {', '.join(s['reads']) or 'none'}. Questions: {', '.join(s['questions']) or 'none'}. Missed checks: {', '.join(misses) or 'none'}. Errors: {', '.join(s['grade']['errors']) or 'none'}.", '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent.parent
    args.output.write_text(render(root))
