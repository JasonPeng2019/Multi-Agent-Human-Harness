"""Reconcile only containers named by this cancelled trial's native receipts."""
import hashlib,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
p=BASE/'root_runs/e1';rt=p/'w/.harness-runtime';home=rt/'operator-only/public-check-service'
evidence=BASE/'operator-fixes/cancelled-excel-service';evidence.mkdir(exist_ok=False)
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def save(q,d):q.write_text(json.dumps(d,indent=2),encoding='utf-8')
def docker(*args):return subprocess.run(['docker',*args],capture_output=True,text=True,timeout=60)
h=Path(read(p/'run.json')['harness_dir']);sys.path.insert(0,str(h))
from orchestrator_harness import processes
from orchestrator_harness.records import RecordLock,atomic_write_json
service=read(home/'service.json');config=read(home/'config.json')
assert processes.exact_process_is_gone(service['pid'],service['creation_time'])
save(evidence/'SERVICE_BEFORE.json',service)
proofs={};ids=set();names=set();unfinished=[]
for folder in (home/'jobs').glob('*/*'):
    if not folder.is_dir():continue
    result=folder/'result.json'
    assert result.exists(),folder
    d=read(result);assert d.get('completed_at'),result
    proofs[str(result.resolve())]=sha(result)
    if d.get('backend',{}).get('container'):ids.add(d['backend']['container'])
    names.update(re.findall(r'excel-public-[a-f0-9]{16}',d.get('error','')))
inventory=docker('ps','-a','--no-trunc','--format','{{json .}}');assert inventory.returncode==0,inventory.stderr
rows=[json.loads(line) for line in inventory.stdout.splitlines() if line.strip()]
owned=[row for row in rows if row['ID'] in ids or row['Names'] in names]
audit={'at_utc':datetime.now(timezone.utc).isoformat(),'service_process_absent':True,
       'result_hashes':proofs,'recorded_container_ids':sorted(ids),'recorded_timeout_names':sorted(names),
       'matched_inventory':owned,'cleanup_actions':[],'all_recorded_containers_absent':False}
save(evidence/'PROOF.json',audit)
for row in owned:
    inspected=docker('inspect',row['ID']);assert inspected.returncode==0
    obj=json.loads(inspected.stdout)[0]
    assert obj['Id']==row['ID'] and obj['Image']==config['backend']['image_id'],row
    assert obj['Name'].lstrip('/')==row['Names'] and row['Names'].startswith('excel-public-'),row
    save(evidence/(row['ID']+'.inspect.json'),obj)
    removed=docker('rm','-f',row['ID'])
    audit['cleanup_actions'].append({'id':row['ID'],'name':row['Names'],'exit_code':removed.returncode,
                                     'stdout':removed.stdout,'stderr':removed.stderr})
    save(evidence/'PROOF.json',audit)
    assert removed.returncode==0
after=docker('ps','-a','--no-trunc','--format','{{json .}}');assert after.returncode==0
remaining=[json.loads(line) for line in after.stdout.splitlines() if line.strip()]
assert not any(row['ID'] in ids or row['Names'] in names for row in remaining)
audit['all_recorded_containers_absent']=True
audit['reconciled_at_utc']=datetime.now(timezone.utc).isoformat()
audit['historical_errors_preserved']=True
save(evidence/'PROOF.json',audit)
with RecordLock(home/'service.json'):
    current=read(home/'service.json');assert current==service
    current.update(status='STOPPED',cleanup_proven=True,
                   operator_cleanup_proof={'path':str((evidence/'PROOF.json').resolve()),'sha256':sha(evidence/'PROOF.json')},
                   operator_cleanup_reconciled_at=audit['reconciled_at_utc'])
    atomic_write_json(home/'service.json',current)
save(evidence/'SERVICE_AFTER.json',current)
print('Verified',len(proofs),'terminal public jobs; removed',len(owned),'exact owned containers; historical failure results preserved.')
