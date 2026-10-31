"""Validate a recorded deterministic service repair while retaining launch receipts.

Staged native prelaunch helper; no model/service launch or automatic repair.
"""
import hashlib,json
from pathlib import Path

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def validate_repair(root:Path,harness:Path,receipt_path:Path,receipt:dict,actual:dict,*,closed=False):
    from orchestrator_harness import processes
    path=root/'.agent-workspace/OPERATOR_PUBLIC_SERVICE_REPAIR.json'
    repair=read(path)
    if (repair.get('schema')!='operator-public-service-repair/v1' or repair.get('status')!='PASS'
            or Path(repair['root']).resolve()!=root.resolve()
            or Path(repair['harness']).resolve()!=harness.resolve()
            or repair.get('model_relaunched') is not False
            or repair.get('original_clock_unchanged') is not True):
        raise ValueError('Public service repair identity or clock is invalid')
    prior=repair['previous_prelaunch']
    if Path(prior['path']).resolve()!=receipt_path.resolve() or prior['sha256']!=digest(receipt_path):
        raise ValueError('Public service repair changed the original prelaunch receipt')
    if repair['previous_service']!=receipt['public_check_service']:
        raise ValueError('Public service repair does not link to the previous service')
    archive=Path(repair['previous_service_archive']).resolve(strict=True)
    if archive.is_relative_to(root.resolve()):raise ValueError('Service repair evidence must be outside the editable ROOT')
    operator=archive.parent/'SERVICE_REPAIR.json'
    if digest(operator)!=digest(path):raise ValueError('Public service repair operator evidence differs')
    stopped=read(archive/'service.json');old=repair['previous_service']
    if stopped.get('status')!='STOPPED' or stopped.get('cleanup_proven') is not True:
        raise ValueError('Prior public service cleanup is not proven')
    for key,value in old.items():
        if key!='status' and stopped.get(key)!=value:raise ValueError('Prior public service process identity changed')
    if (processes.identity_matches(old['pid'],old['creation_time'])
            or (processes.process_alive(old['pid']) and processes.process_identity(old['pid']) is None)):
        raise ValueError('Prior public service is live or its process identity is unknown')
    expected=repair['new_service']
    if closed:expected={**expected,'status':'STOPPED'}
    if actual!=expected:raise ValueError('Repaired public service identity changed')
    return {'path':str(path.resolve()),'sha256':digest(path),'operator_path':str(operator)}
