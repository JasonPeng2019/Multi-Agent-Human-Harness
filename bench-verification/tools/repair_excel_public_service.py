"""One diagnosed deterministic service repair; never launches a model or resets time."""
import hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone

base=Path(__file__).resolve().parents[2]
harness=base/'bench-verification/hx'
root=base/'bench-verification/root_runs/e1/w'
evidence=base/'bench-verification/excel/operator-only/public-lf-repair'
sys.path.insert(0,str(harness))
from orchestrator_harness import public_checks
from orchestrator_harness.records import atomic_write_json

assert not list((root/'.harness-runtime/epochs').glob('*/lanes/*/lane.json')), 'Repair must precede worker admission'
service=public_checks.validate_service(root,harness)
old=public_checks.home(root)
config=public_checks.read(old/'config.json')
assert config['fixed_inputs']=={}
receipt=root/'.agent-workspace/ROOT_PRELAUNCH_SETUP.json'
receipt_digest=hashlib.sha256(receipt.read_bytes()).hexdigest()
public_checks.stop_service(root)
assert public_checks.read(old/'service.json')['cleanup_proven'] is True
archive=(evidence/'service-before').resolve()
assert old.resolve().is_relative_to(root.resolve()) and archive.is_relative_to(evidence.resolve()) and not archive.exists()
shutil.move(str(old),str(archive))
shutil.copyfile(evidence/'public_check_adapter.corrected.py',base/'bench-verification/excel/support/public_check_adapter.py')
shutil.copyfile(evidence/'policy.corrected.json',harness/'local-config/public-check-policy.json')
new=public_checks.start_service(harness,root)
actual=public_checks.validate_service(root,harness)
assert new==actual
record={'schema':'operator-public-service-repair/v1','status':'PASS','reason':'Restore exact official LF bytes after CRLF public shell failure. No workers existed at repair.','at_utc':datetime.now(timezone.utc).isoformat(),'root':str(root),'harness':str(harness),'previous_prelaunch':{'path':str(receipt),'sha256':receipt_digest},'previous_service':service,'previous_service_archive':str(archive),'new_service':new,'model_relaunched':False,'original_clock_unchanged':True,'hidden_feedback_supplied':False}
assert hashlib.sha256(receipt.read_bytes()).hexdigest()==receipt_digest
atomic_write_json(root/'.agent-workspace/OPERATOR_PUBLIC_SERVICE_REPAIR.json',record)
atomic_write_json(evidence/'SERVICE_REPAIR.json',record)
print(json.dumps(record))
