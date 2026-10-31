"""Display one saved hidden partial score, identifying any local scoring variant."""
import argparse,json,math
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run_folder',type=Path);p.add_argument('--json',action='store_true');a=p.parse_args()
    file=a.run_folder/'hidden-evaluation/grading.json'
    if not file.is_file():p.exit(2,'No hidden score saved for this run yet.\n')
    r=json.loads(file.read_text(encoding='utf-8-sig'));s=r.get('partial_score')
    if r.get('status')!='GRADED' or r.get('cleanup_proven') is not True or type(s) not in (int,float) or not math.isfinite(s) or not 0<=s<=1:p.exit(2,'No completed, verified hidden score is available.\n')
    if a.json:print(json.dumps(r,indent=2));return
    print(f"Run: {r['run_id']}\nTask: {r['task']}\nHidden evaluation partial score: {100*s:.3f}%\nBinary reward: {r['binary_reward']}")
    if r.get('official_comparable') is False:
        print('Scoring: '+r.get('scoring_note','local oracle-based timing / Claude CLI visual-grader variant (not official benchmark parity)'))
    m=r.get('metrics',{})
    if r['task']=='biofabric-rust-rewrite':print(f"Tests: {m['passed']} passed / {m['passed']+m['failed']} total")
    if r['task']=='excel-clone':print(f"Correctness: {m['correctness_reward']:.3f} | UX: {m['cua_rubric_score']:.3f}")
    if r.get('candidate_revision'):print(f"Candidate: {r['candidate_revision']}")

if __name__=='__main__':main()
