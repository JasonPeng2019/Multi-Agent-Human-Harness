from pathlib import Path
import json,subprocess,sys
from datetime import datetime,timezone
w=Path(__file__).resolve().parents[1]
if sys.argv[1:]==['--time']:
 p=next((w.parent/'out').glob('*/launch.json'));r=json.loads(p.read_text());deadline=datetime.fromisoformat(r['watchdog_deadline_utc'].replace('Z','+00:00'));print(json.dumps({'deadline_utc':deadline.isoformat(),'remaining_minutes':max(0,(deadline-datetime.now(timezone.utc)).total_seconds()/60)}));raise SystemExit(0)
raise SystemExit(subprocess.call([sys.executable,'C:\\Users\\Jason\\Documents\\Jason\\Orchestrator-Harness-Hackathon-Benchmark\\bench-verification\\biofabric\\support\\public_check_adapter.py','--worktree',str(w),*sys.argv[1:]]))
