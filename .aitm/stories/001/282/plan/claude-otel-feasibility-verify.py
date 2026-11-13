from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import sys

root=Path(sys.argv[1]).resolve()
session=(root/'session-id.txt').read_text().strip()
native=Path.home()/'.claude/projects'/re.sub(r'[^A-Za-z0-9]','-',str(root/'project'))
parent=native/(session+'.jsonl')
child,=(native/session/'subagents').glob('agent-*.jsonl')
raw=root/'telemetry.json'
events=[
    {a['key']: next(iter(a['value'].values())) for a in record['attributes']}
    for batch in json.loads(raw.read_bytes())
    for resource in batch['resourceLogs']
    for scope in resource['scopeLogs']
    for record in scope['logRecords']
]
def rows(path):
    return list(map(json.loads,path.read_bytes().splitlines()))
parent_rows, child_rows = rows(parent), rows(child)
child_agent=child_rows[0]['agentId']
requests=[e for e in events if e.get('event.name')=='api_request']
assert len({e['request_id'] for e in requests})==len(requests)==5
assert len({e['client_request_id'] for e in requests})==5
assert {e['session.id'] for e in requests}=={session}
child_requests=[e for e in requests if e.get('agent_id')==child_agent]
assert len(child_requests)==2
one_prompt,={e['prompt.id'] for e in child_requests}
main_requests=[e for e in requests if e.get('prompt.id')==one_prompt and 'agent_id' not in e]
assert len(main_requests)==2
native_counts={'input_tokens':'input_tokens','output_tokens':'output_tokens',
               'cache_read_tokens':'cache_read_input_tokens','cache_creation_tokens':'cache_creation_input_tokens'}
for event in requests:
    side=child_rows if 'agent_id' in event else parent_rows
    matches=[r for r in side if r['type']=='assistant' and r.get('requestId')==event['request_id']]
    assert matches
    assert len({r['message']['id'] for r in matches})==1
    for r in matches:
        assert all(int(event[k])==r['message']['usage'][v] for k,v in native_counts.items())
result,=[r for r in parent_rows if 'toolUseResult' in r]
assert result['toolUseResult']['agentId']==child_agent
assert result['promptId']==one_prompt
assert result['toolUseResult']['usage']==child_rows[-1]['message']['usage']
assert child_requests[-1]['request_id']==child_rows[-1]['requestId']
assert any(e.get('event.name')=='subagent_completed' and e.get('agent_id')==child_agent for e in events)
for e in events:
    assert not (e.get('prompt') and e['prompt'].lower()!='<redacted>')
scope=main_requests+child_requests
child_cost=sum(int(e['cost_usd_micros']) for e in child_requests)
scope_cost=sum(int(e['cost_usd_micros']) for e in scope)
totals=lambda group:{k:sum(int(e[k]) for e in group) for k in native_counts}
out={'schema':'aitm.claude-coverage-otel-feasibility/v1','surface':'macOS Claude Code 2.1.318',
     'scope':'one synthetic foreground Agent prompt and one tool-free control prompt',
     'telemetry_api_requests':len(requests),'all_joined_to_unique_native_request_identity':True,
     'agent_prompt_total_requests':len(scope),'agent_prompt_child_requests':len(child_requests),
     'agent_prompt_child_tokens':totals(child_requests),'agent_prompt_all_tokens':totals(scope),
     'agent_prompt_child_estimated_cost_usd_micros':child_cost,
     'agent_prompt_all_estimated_cost_usd_micros':scope_cost,
     'agent_prompt_child_estimated_cost_share':round(child_cost/scope_cost,6),
     'earlier_child_request_estimated_cost_usd_micros':int(child_requests[0]['cost_usd_micros']),
     'parent_result_covers_final_child_request_only':True,
     'original_ownership_or_gate_change':False,'production_prevalence_measured':False,
     'artifact_sha256':{k:sha256(v.read_bytes()).hexdigest() for k,v in [('telemetry',raw),('parent',parent),('child',child),('wire',root/'wire.jsonl')]}}
(root/'feasibility.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
