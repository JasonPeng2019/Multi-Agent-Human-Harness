import json
import tempfile
import unittest
from pathlib import Path

from orchestrator_harness import view_state, view_artifacts
from orchestrator_harness.core import content_hash
from orchestrator_harness.tests.test_view import ViewFixture, EPOCH


class RootReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = ViewFixture(Path(self.tmp.name))
        self.lane = self.fixture.lanes[2]
        self.folder = self.fixture.rt / 'epochs' / EPOCH / 'lanes' / self.lane['lane_id']
        self.path = self.folder / 'COMPLETION_REVIEW.json'
        self.record = {'schema': 'completion-review/v1', 'lane_id': self.lane['lane_id'], 'run_id': self.lane['run_id'],
                       'review_outcome': 'PASS', 'review_summary': 'Root checked committed changes and reran tests.',
                       'reviewed_at': '2026-10-31T00:00:00Z', 'commit': 'a' * 40, 'evidence': ['unittest: 15 passed']}
        self.record['content_hash'] = content_hash(self.record)
        self.path.write_text(json.dumps(self.record))

    def test_review_content_reaches_result_view(self):
        review = view_state._root_review(self.fixture.rt, EPOCH, self.lane, {'accepted_by': 'ROOT', 'approval': 'ACCEPTED'})
        text = view_artifacts.panel_text({**self.lane, 'root_review': review}, 'result')
        self.assertTrue(text.startswith('### Root review'))
        for value in ('Verdict: PASS', 'Decision: ACCEPTED', 'Reviewer: ROOT', 'Root checked committed changes', 'unittest: 15 passed'):
            self.assertIn(value, text)

    def test_other_run_or_tampered_review_is_not_shown(self):
        for field, value in [('run_id', 'other-run'), ('review_summary', 'tampered')]:
            record = dict(self.record, **{field: value})
            self.path.write_text(json.dumps(record))
            self.assertIsNone(view_state._root_review(self.fixture.rt, EPOCH, self.lane, None))

    def test_archived_review_remains_readable(self):
        archive = self.folder / 'retirement-archive'
        archive.mkdir()
        self.path.rename(archive / self.path.name)
        review = view_state._root_review(self.fixture.rt, EPOCH, self.lane, None)
        self.assertEqual('PASS', review['verdict'])
        self.assertEqual('Pending', review['approval'])

    def test_saved_test_report_is_expanded_but_external_path_is_not(self):
        report = self.fixture.rt.parent / 'checks.txt'
        report.write_text('test_average ... ok\nRan 4 tests\nOK')
        outside = Path(self.tmp.name).parent / 'not-owned-review.txt'
        review = {'verdict': 'PASS', 'approval': 'ACCEPTED', 'reviewer': 'ROOT', 'summary': 'Checks passed',
                  'workspace': str(self.fixture.rt.parent), 'evidence': [str(report), str(outside)]}
        text = view_artifacts.root_review_text({'root_review': review})
        self.assertIn('test_average ... ok', text)
        self.assertIn('Test report: checks.txt', text)

    def test_pending_review_is_explicit(self):
        self.assertIn('No verified root review', view_artifacts.root_review_text({}))
