"""Clock recovery must preserve identity, charge work, and reject unsupported pauses."""
import copy,hashlib,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from quota_clock import effective_deadline

class QuotaClockTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.run=self.root/'out/trial';self.run.mkdir(parents=True)
        self.now=datetime(2026,10,31,10,41,tzinfo=timezone.utc)
        self.launch={'run_id':'trial','started_at_utc':'2026-10-31T08:00:00+00:00','watchdog_deadline_utc':'2026-10-31T11:45:00+00:00'}
        self.write(self.run/'launch.json',self.launch)
        self.write(self.run/'manifest.json',{'run_id':'trial','ended_at_utc':'2026-10-31T09:00:00+00:00','watchdog_expired':False})
        self.events=self.run/'claude-events.jsonl'
        self.events.write_text(json.dumps({'type':'system','subtype':'init','session_id':'same-session'})+'\n'+json.dumps({'type':'rate_limit_event','session_id':'same-session','rate_limit_info':{'status':'rejected','resetsAt':1793443200}})+'\n')
        self.stop={'schema':'operator-quota-stop/v1','run_id':'trial','root_session_id':'same-session','all_owned_provider_processes_absent':True,'collector_sealed':True,'stopped_at_utc':'2026-10-31T09:01:00+00:00','segment_launch':self.ref(self.run/'launch.json'),'segment_manifest':self.ref(self.run/'manifest.json'),'transcript':self.ref(self.events)}
        self.write(self.root/'QUOTA_STOP.json',self.stop)
        self.pause={'schema':'operator-quota-pause/v1','run_id':'trial','root_session_id':'same-session','original_deadline_utc':self.launch['watchdog_deadline_utc'],'stop_audit':self.ref(self.root/'QUOTA_STOP.json'),'paused_at_utc':'2026-10-31T09:01:00+00:00','clock_resumed_at_utc':'2026-10-31T10:40:00+00:00'}
    def write(self,p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
    def ref(self,p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def install(self):self.write(self.run/'quota-pauses/0001.json',self.pause)
    def check(self):return effective_deadline(self.run,now=self.now)
    def test_no_pause_keeps_original_wall_clock(self):
        r=self.check();self.assertEqual(self.launch['watchdog_deadline_utc'],r['effective_deadline_utc']);self.assertEqual(0,r['paused_seconds'])
    def test_only_quiescent_quota_gap_is_added(self):
        self.install();r=self.check();self.assertEqual('2026-10-31T13:24:00+00:00',r['effective_deadline_utc']);self.assertEqual(5940,r['paused_seconds']);self.assertEqual(self.launch,json.loads((self.run/'launch.json').read_text()))
    def test_active_work_cannot_be_paused(self):
        self.pause['paused_at_utc']='2026-10-31T09:00:00+00:00';self.install()
        with self.assertRaisesRegex(ValueError,'active work'):self.check()
    def test_foreign_session_rejected(self):
        self.pause['root_session_id']='replacement';self.install()
        with self.assertRaisesRegex(ValueError,'session'):self.check()
    def test_early_reset_recovery_rejected(self):
        self.pause['clock_resumed_at_utc']='2026-10-31T10:39:00+00:00';self.install()
        with self.assertRaisesRegex(ValueError,'reset'):self.check()
    def test_changed_evidence_rejected(self):
        self.install();self.events.write_text('{}\n')
        with self.assertRaisesRegex(ValueError,'evidence changed'):self.check()
    def test_operator_delay_after_reset_cannot_extend_allowance(self):
        self.pause['clock_resumed_at_utc']='2026-10-31T10:40:30+00:00';self.install()
        with self.assertRaisesRegex(ValueError,'operator delay'):self.check()
    def test_future_pause_rejected(self):
        self.pause['clock_resumed_at_utc']='2026-10-31T10:42:00+00:00';self.install()
        with self.assertRaisesRegex(ValueError,'future'):self.check()
    def test_unsealed_or_expired_allowance_rejected(self):
        self.write(self.run/'manifest.json',{'run_id':'trial','ended_at_utc':'2026-10-31T09:00:00+00:00','watchdog_expired':True});self.stop['segment_manifest']=self.ref(self.run/'manifest.json');self.write(self.root/'QUOTA_STOP.json',self.stop);self.pause['stop_audit']=self.ref(self.root/'QUOTA_STOP.json');self.install()
        with self.assertRaisesRegex(ValueError,'expired'):self.check()
    def test_normal_finish_is_not_quota_evidence(self):
        self.events.write_text(json.dumps({'type':'result','session_id':'same-session','subtype':'success'})+'\n');self.stop['transcript']=self.ref(self.events);self.write(self.root/'QUOTA_STOP.json',self.stop);self.pause['stop_audit']=self.ref(self.root/'QUOTA_STOP.json');self.install()
        with self.assertRaisesRegex(ValueError,'rejected usage'):self.check()

if __name__=='__main__':unittest.main()
