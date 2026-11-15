"""Real bounded E04 model choices on isolated, captured Contractor A02 windows.

Replays original authorized projections through existing business processors.
No original database/state is modified and no macro submission is claimed.
"""
from __future__ import annotations
import argparse
from contextlib import nullcontext
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from types import SimpleNamespace
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from integration.contractor_bid_actions import ContractorBidActionAssembler
from integration.contractor_tender_model_options import build_model_host
from src.actions.contracts.common import ActionContext
from src.actions.processors import register_representative_processors
from src.actions.registry import ActionRegistry
from src.coordination.tasks import TaskStore,task_digest
from src.organization.models import Organization,Authorization
from src.organization.registry import OrganizationRegistry

OUT=ROOT/'output/integration/capstone_validation_20261105/model_pilot'
SOURCE=ROOT/'output/integration/linked_case0014_20261102'
MAX_CALLS=24
MODES=('single_agent','organization_discussion')
CORE=('integration/contractor_bid_actions.py','integration/contractor_tender_model_options.py',
      'integration/action_model_host.py','src/actions/model_strategy.py','src/actions/organization_strategy.py',
      'src/actions/runner.py','src/actions/processors.py','src/llm_client.py')

def now():return datetime.now(timezone.utc).isoformat()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def append(path,value):
    with path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def rebase(value,old,new):
    if isinstance(value,dict):return {k:rebase(v,old,new) for k,v in value.items()}
    if isinstance(value,list):return [rebase(v,old,new) for v in value]
    return new if value==old else value

class NoCalls:
    def request_policy(self):
        return {'schema_version':'model-request-policy.v1','max_requests_per_call':1,'internal_retries':0,
                'provider':'preflight-no-requests','model':'preflight-no-requests'}
    def chat_with_metadata(self,*args,**kwargs):raise AssertionError('Preflight must never request a model')

class CappedTransport:
    def __init__(self,client,arm_path):self.client=client;self.arm_path=arm_path
    def request_policy(self):
        return {**self.client.request_policy(),'capstone_pilot_version':'1','global_request_cap':MAX_CALLS,
                'experiment_wrapper_sha256':sha(Path(__file__))}
    def chat_with_metadata(self,messages,*,temperature):
        ledger=OUT/'api_attempts.jsonl'
        previous=[] if not ledger.exists() else [json.loads(x) for x in ledger.read_text(encoding='utf-8').splitlines()]
        if any(x['event']=='failed' for x in previous):raise RuntimeError('Pilot stopped after prior failed request')
        count=sum(x['event']=='started' for x in previous)
        if count>=MAX_CALLS:raise RuntimeError('Pilot request cap reached')
        call_id=f'CALL-{count+1:03d}';request_hash=task_digest(messages)
        record={'call_id':call_id,'arm':str(self.arm_path.relative_to(OUT)),
                'request_sha256':request_hash,'marker':messages[-1]['content'].splitlines()[0]}
        save(self.arm_path/(call_id+'-request.json'),{'messages':messages,'temperature':temperature,
             'transport_policy':self.request_policy()})
        append(ledger,{**record,'event':'started','at':now()});started=time.perf_counter()
        try:
            response=self.client.chat_with_metadata(messages,temperature=temperature)
            save(self.arm_path/(call_id+'-response.json'),{'content':response.content,'metadata':response.metadata})
            append(ledger,{**record,'event':'succeeded','at':now(),'seconds':time.perf_counter()-started,
                          'usage':response.metadata.get('usage_metadata',{})})
            return response
        except Exception as exc:
            append(ledger,{**record,'event':'failed','at':now(),'seconds':time.perf_counter()-started,
                          'error_type':type(exc).__name__})
            raise

def capture_windows():
    db=SOURCE/'attempt-001/runtime/tasks.sqlite'
    c=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
    captured={}
    for key,raw in c.execute("select key,value from metadata where key like 'action_option_snapshot:%'"):
        record=json.loads(raw)
        if record['selection']['action_id']=='CONTRACTOR-A02':
            assert task_digest({k:v for k,v in record.items() if k!='record_sha256'})==record['record_sha256']
            captured[record['selection']['organization_id']]={'metadata_key':key,'record':record}
    histories={}
    for key,raw in c.execute("select key,value from metadata where key like 'contractor_bid_source_history:%'"):
        record=json.loads(raw)
        assert task_digest({k:v for k,v in record.items() if k!='record_sha256'})==record['record_sha256']
        histories[record['identity']['organization_id']]={'key':key,'record':record}
    c.close()
    active=read(SOURCE/'input/macro-request.json')
    ids=[a['agent_id'] for a in active['agents'] if a['role']=='Contractor'][::2]
    assert len(ids)==4 and all(cid in captured for cid in ids)
    assembly=read(SOURCE/'input/assembly-host.json')
    orgs=assembly['settings']['bank']['authority']['organization_snapshot']['organizations']
    result=[]
    for i,cid in enumerate(ids,1):
        data=captured[cid];snapshot=deepcopy(data['record']['snapshot'])
        history=histories[cid]
        assert history['record']['identity']['context_sha256']==task_digest(snapshot['context'])
        by_ref={task_digest(r['ref']):r for r in snapshot['source_reading']}
        for row in history['record']['source_reading']:
            key=task_digest(row['ref'])
            if key in by_ref:assert by_ref[key]==row
            else:by_ref[key]=row
        snapshot['source_reading']=list(by_ref.values())
        assert len(snapshot['options'])==2
        result.append({'window_id':f'WINDOW-{i:02d}','company_id':cid,'project_id':'CASE-0014',
            'source_db_sha256':sha(db),'source_metadata_key':data['metadata_key'],
            'original_record_sha256':data['record']['record_sha256'],'snapshot':snapshot,
            'original_executed_source_history':{'key':history['key'],'sha256':history['record']['record_sha256']},
            'organizations':orgs,'source_run':snapshot['context']['run_id'],
            'boundary':'captured scenario replay; original business profiles retained; not a new real-world project'})
    return result

def build(window,mode,path,transport):
    run_id='capstone-20261105-'+window['window_id'].lower()+'-'+mode
    snap=rebase(deepcopy(window['snapshot']),window['source_run'],run_id)
    context=ActionContext.model_validate(snap['context'])
    organizations=OrganizationRegistry(run_id)
    for row in window['organizations']:organizations.register(Organization.model_validate(row))
    for row in snap['source_reading']:
        if row['ref']['kind']=='Authorization':organizations.authorize(Authorization.model_validate(row['projection']))
    registry=register_representative_processors(ActionRegistry())
    path.mkdir(parents=True,exist_ok=True)
    store=TaskStore(run_id=run_id,organization_ids=[window['company_id']],path=path/'tasks.sqlite')
    model_version='tender-model:'+task_digest(transport.request_policy())
    assembly=SimpleNamespace(client=SimpleNamespace(tasks=store,tender_model_client=transport,
        versions={'model':model_version},organization_roles={window['company_id']:'Contractor'}))
    try:
        host=build_model_host(assembly=assembly,registry=registry,organizations=organizations,store=store,
            read_guard=nullcontext,request=None,output_directory=path,
            settings={'namespace':'capstone-captured-options','strategy':mode,
                'host':{'host_id':'host','budget_id':'arm-budget','max_calls':6,
                    'action_ids':['CONTRACTOR-A01','CONTRACTOR-A02'],'max_options':2,
                    'max_prompt_chars':300000,'max_response_chars':4096,'max_members':4}})
        projection={'run_id':run_id,'macro_version':'captured-authorized-source.v1','state_version':'frozen-window-v1',
            'read_token':context.read_token,'business_time':context.business_time.model_dump(mode='json'),
            'organization_id':window['company_id'],
            'objects':[{'ref':r['ref'],'value':r['projection']} for r in snap['source_reading']]}
        class FrozenProvider:
            def project(self,**kwargs):return deepcopy(projection)
        assembler=ContractorBidActionAssembler(registry=registry,organizations=organizations,
            provider=FrozenProvider(),macro_version=projection['macro_version'],source_mode='formal',
            policy_version='captured-scenario-replay.v1',model_host=host)
        action=snap['action_input']
        prepared=assembler.build(context,**{k:action[k] for k in
            ['pricing_profile_ref','capacity_ref','cost_refs','allowed_method_refs']})
        prepared.runner.prepare_decision(context=context,action_input=prepared.action_input,reading=prepared.reading)
        registration=registry.get('CONTRACTOR-A02');component=host.components[0]
        options,error=component._options(context,prepared.action_input,registration,prepared.reading,registration.processor)
        assert error is None and len(options)==2
        assert [o['option_id'] for o in options]==[o['option_id'] for o in snap['options']]
        assert prepared.action_input.model_dump(mode='json')==snap['action_input']
        return store,host,prepared,options,len(registry.role_configurations['Contractor'].members)
    except Exception:
        store.close();raise

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'protocol.json').exists():
        protocol=read(OUT/'protocol.json');assert protocol['runner_sha256']==sha(Path(__file__))
        print('Existing verified pilot protocol retained; no call.',flush=True);return
    windows=capture_windows()
    save(OUT/'captured_windows.json',windows)
    attempt=1+len(list(OUT.glob('preflight-*')))
    folder=OUT/f'preflight-{attempt:02d}'
    results=[]
    for window in windows:
        for mode in MODES:
            store,host,prepared,options,members=build(window,mode,folder/window['window_id']/mode,NoCalls())
            try:
                baseline=prepared.execute(execution_path='deterministic')
                assert baseline.kind=='completed'
                results.append({'window_id':window['window_id'],'company_id':window['company_id'],'mode':mode,
                    'options_sha256':task_digest(options),'option_ids':[o['option_id'] for o in options],
                    'original_input_sha256':task_digest(window['snapshot']['action_input']),
                    'members':members,'expected_paid_requests':1 if mode=='single_agent' else members+1,
                    'rule_result':baseline.model_dump(mode='json')})
            finally:store.close()
    for w in windows:
        pair=[r for r in results if r['window_id']==w['window_id']]
        assert pair[0]['options_sha256']==pair[1]['options_sha256']
    assert sum(r['expected_paid_requests'] for r in results)<=MAX_CALLS
    save(folder/'checks.json',results)
    protocol={'prepared_at':now(),'runner_sha256':sha(Path(__file__)),
        'window_file_sha256':sha(OUT/'captured_windows.json'),'core_sha256':{p:sha(ROOT/p) for p in CORE},
        'provider':'deepseek','model':'deepseek-v4-flash','temperature':0,'modes':MODES,
        'selected_windows':[r['window_id'] for r in windows],
        'selection_rule':'every other contractor in the frozen initial source order; no label-based selection',
        'total_request_cap':MAX_CALLS,'expected_requests':sum(r['expected_paid_requests'] for r in results),
        'preflight_checks':str((folder/'checks.json').relative_to(OUT)),
        'scope':'one project, four captured quotation decision windows, one replicate per mode; no macro submission',
        'independence':'separate arm journals, fresh calls, no cached response reuse; not an independent new-project test',
        'quality_oracle':'formal business checks; expert judgment pending; no claim that cheaper bids are better'}
    save(OUT/'protocol.json',protocol);save(OUT/'state.json',{'status':'prepared','paid_calls':0})
    print(json.dumps(protocol,ensure_ascii=False),flush=True)

def run():
    protocol=read(OUT/'protocol.json');state=read(OUT/'state.json')
    assert state['status']=='prepared' and not (OUT/'api_attempts.jsonl').exists()
    assert protocol['runner_sha256']==sha(Path(__file__))
    assert sha(OUT/'captured_windows.json')==protocol['window_file_sha256']
    assert all(sha(ROOT/p)==h for p,h in protocol['core_sha256'].items())
    from src.llm_client import OpenAICompatibleClient
    from integration.model_tender_native import _close_transport
    raw=OpenAICompatibleClient.from_env(model=protocol['model'])
    try:
        assert raw.request_policy()['provider']==protocol['provider']
        save(OUT/'state.json',{'status':'running','started_at':now(),'total_request_cap':MAX_CALLS})
        results=[]
        for i,window in enumerate(read(OUT/'captured_windows.json')):
            modes=MODES if i%2==0 else tuple(reversed(MODES))
            for mode in modes:
                arm=OUT/'arms'/window['window_id']/mode
                if (arm/'intent.json').exists():raise RuntimeError('Prior unresolved arm intent; no replay')
                store,host,prepared,options,members=build(window,mode,arm,CappedTransport(raw,arm))
                try:
                    save(arm/'intent.json',{'started_at':now(),'input_sha256':task_digest(window['snapshot']['action_input']),
                        'options_sha256':task_digest(options),'protocol_sha256':sha(OUT/'protocol.json')})
                    started=time.perf_counter();result=prepared.execute()
                    audit=prepared.runner.audit_records[-1].model_dump(mode='json')
                    record={'window_id':window['window_id'],'company_id':window['company_id'],'mode':mode,
                        'result':result.model_dump(mode='json'),'audit':audit,'seconds':time.perf_counter()-started,
                        'host_evidence':host.evidence()}
                    save(arm/'outcome.json',record);results.append(record)
                    print(json.dumps({'window':window['window_id'],'mode':mode,'kind':result.kind},ensure_ascii=False),flush=True)
                    if result.kind!='completed':raise RuntimeError('Retained non-completed action; no retry or fallback')
                finally:store.close()
        ledger=[json.loads(x) for x in (OUT/'api_attempts.jsonl').read_text(encoding='utf-8').splitlines()]
        assert sum(r['event']=='started' for r in ledger)<=MAX_CALLS
        save(OUT/'results.json',results)
        save(OUT/'state.json',{'status':'completed','finished_at':now(),'decision_windows':4,
            'model_decisions':len(results),'paid_attempts':sum(r['event']=='started' for r in ledger),
            'successful_requests':sum(r['event']=='succeeded' for r in ledger)})
    except Exception as exc:
        save(OUT/'state.json',{'status':'stopped_error','at':now(),'error_type':type(exc).__name__,
                             'automatic_retries':0})
        raise
    finally:_close_transport(raw)

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=p.parse_args()
    prepare() if a.prepare else run()
