import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'harness-single-run-version'))
from public_service_repair import validate_repair

class ServiceRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.root=self.base/'workspace';self.h=self.base/'harness';self.root.mkdir();self.h.mkdir();self.archive=self.base/'operator/service-before';self.archive.mkdir(parents=True)
        self.path=self.root/'.agent-workspace/ROOT_PRELAUNCH_SETUP.json';self.path.parent.mkdir()
        self.old={'schema':'worker-public-check-service/v1','pid':123,'creation_time':'old','status':'READY','policy_sha256':'old-policy','root':str(self.root),'harness':str(self.h)}
        self.new={**self.old,'pid':456,'creation_time':'new','policy_sha256':'new-policy'}
        self.receipt={'public_check_service':self.old};self.write(self.path,self.receipt)
        self.stopped={**self.old,'status':'STOPPED','cleanup_proven':True};self.write(self.archive/'service.json',self.stopped)
        self.repair={'schema':'operator-public-service-repair/v1','status':'PASS','root':str(self.root),'harness':str(self.h),'model_relaunched':False,'original_clock_unchanged':True,'previous_prelaunch':{'path':str(self.path),'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()},'previous_service':self.old,'previous_service_archive':str(self.archive),'new_service':self.new}
        self.save()
        self.patch=mock.patch.multiple('orchestrator_harness.processes',identity_matches=mock.Mock(return_value=False),process_alive=mock.Mock(return_value=False));self.patch.start();self.addCleanup(self.patch.stop)
    def write(self,p,v):p.write_text(json.dumps(v))
    def save(self):
        self.write(self.root/'.agent-workspace/OPERATOR_PUBLIC_SERVICE_REPAIR.json',self.repair);self.write(self.archive.parent/'SERVICE_REPAIR.json',self.repair)
    def validate(self,actual=None,**kw):return validate_repair(self.root,self.h,self.path,self.receipt,actual or self.new,**kw)
    def test_truthful_repair_links_old_and_new_service(self):self.assertIn('sha256',self.validate())
    def test_closed_native_service_retains_repair_chain(self):self.validate({**self.new,'status':'STOPPED'},closed=True)
    def test_original_receipt_mutation_rejected(self):
        self.write(self.path,{'changed':True})
        with self.assertRaisesRegex(ValueError,'original prelaunch'):self.validate()
    def test_unproven_old_cleanup_rejected(self):
        self.stopped['cleanup_proven']=False;self.write(self.archive/'service.json',self.stopped)
        with self.assertRaisesRegex(ValueError,'cleanup'):self.validate()
    def test_replacement_new_process_rejected(self):
        with self.assertRaisesRegex(ValueError,'identity changed'):self.validate({**self.new,'pid':999})
    def test_operator_evidence_must_match(self):
        self.write(self.archive.parent/'SERVICE_REPAIR.json',{})
        with self.assertRaisesRegex(ValueError,'operator evidence'):self.validate()
    def test_old_service_still_live_rejected(self):
        with mock.patch('orchestrator_harness.processes.identity_matches',return_value=True):
            with self.assertRaisesRegex(ValueError,'live'):self.validate()

if __name__=='__main__':unittest.main()
