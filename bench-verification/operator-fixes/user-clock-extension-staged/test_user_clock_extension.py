import importlib.util
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('staged_clock', HERE/'orchestrator_harness/quota_clock.py')
clock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clock)

class ClockExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        self.now = datetime.now(timezone.utc)
        self.first = self.now-timedelta(hours=1)
        self.old = self.now+timedelta(minutes=10)
        self.launch = dict(run_id='run', started_at_utc=self.first.isoformat(),
                           watchdog_deadline_utc=self.old.isoformat(), workspace=str(self.run))
        self.save(self.run/'launch.json', self.launch)
        (self.run/'claude-events.jsonl').write_text(json.dumps(dict(type='system',subtype='init',session_id='sid'))+'\n')
        self.save(self.run/'auth.json', dict(schema='operator-user-clock-authorization/v1',extensions={'run':900}))
        self.row = dict(schema='operator-user-clock-extension/v1',run_id='run',root_session_id='sid',seconds=900,
            issued_at_utc=(self.now-timedelta(seconds=5)).isoformat(),
            prior_effective_deadline_utc=self.old.isoformat(),
            effective_deadline_utc=(self.old+timedelta(seconds=900)).isoformat(),
            original_launch=self.ref(self.run/'launch.json'),authorization=self.ref(self.run/'auth.json'))
        self.receipt = self.run/'clock-extensions/0001.json'
        self.save(self.receipt,self.row)
    def save(self,path,row):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(row))
    def ref(self,path):
        return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    def test_addition_and_original_bytes(self):
        original=(self.run/'launch.json').read_bytes()
        result=clock.effective_deadline(self.run,now=self.now)
        self.assertEqual(900,result['user_extension_seconds'])
        self.assertEqual(self.old+timedelta(seconds=900),clock.instant(result['effective_deadline_utc']))
        self.assertEqual(original,(self.run/'launch.json').read_bytes())
    def test_history_is_not_rewritten(self):
        segment=self.run/'segments/0002';segment.mkdir(parents=True)
        baseline=clock.effective_deadline(self.run,now=self.now,as_of=self.first)
        launch={**self.launch,'started_at_utc':(self.now-timedelta(minutes=1)).isoformat(),
                'quota_clock':baseline,'resume_session_id':'sid'}
        self.save(segment/'launch.json',launch)
        self.assertEqual(baseline,clock.validate_launch_clock(segment/'launch.json',launch))
        self.assertNotIn('user_extension_seconds',baseline)
    def test_forged_or_late_receipts_rejected(self):
        for key,value in [('seconds',901),('run_id','other'),('root_session_id','other'),
                          ('issued_at_utc',(self.old+timedelta(seconds=1)).isoformat()),
                          ('effective_deadline_utc',self.old.isoformat())]:
            with self.subTest(key=key):
                self.save(self.receipt,{**self.row,key:value})
                with self.assertRaises(ValueError):clock.effective_deadline(self.run,now=self.now)
        self.save(self.receipt,self.row)
        self.save(self.run/'auth.json',dict(schema='operator-user-clock-authorization/v1',extensions={'run':1800}))
        with self.assertRaises(ValueError):clock.effective_deadline(self.run,now=self.now)
    def test_old_cutoff_only_not_new_cutoff(self):
        segment=self.run/'segments/0003';segment.mkdir(parents=True)
        self.save(segment/'launch.json',self.launch)
        final=dict(watchdog_expired=True,launch_error=None,watchdog_stop_errors=[])
        self.save(segment/'manifest.json',final)
        current=clock.effective_deadline(self.run,now=self.now)
        self.assertTrue(clock.extension_covers_expired_segment(segment,current))
        self.save(segment/'launch.json',{**self.launch,'watchdog_deadline_utc':current['effective_deadline_utc'],'quota_clock':current})
        self.assertFalse(clock.extension_covers_expired_segment(segment,current))
    def test_stop_errors_do_not_bypass_admission(self):
        segment=self.run/'segments/0003';segment.mkdir(parents=True)
        self.save(segment/'launch.json',self.launch)
        self.save(segment/'manifest.json',dict(watchdog_expired=True,watchdog_stop_errors=['failed']))
        self.assertFalse(clock.extension_covers_expired_segment(segment,clock.effective_deadline(self.run,now=self.now)))

if __name__=='__main__':unittest.main()
