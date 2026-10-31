"""Corrupted shared transcripts must not become plausible usage totals."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import token_ledger


class DuplicateDispatchUsageTests(unittest.TestCase):
    def events(self, rows):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'controller.events.jsonl'
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
        return path

    def test_same_run_started_twice_rejects_accounting(self):
        path = self.events([
            dict(event_type='controller_started', run_id='run-1'),
            dict(event_type='provider_started', run_id='run-1'),
            dict(event_type='controller_started', run_id='run-1'),
        ])
        with self.assertRaisesRegex(token_ledger.LedgerError, 'duplicate controller dispatch'):
            token_ledger._provider_start_events(path)

    def test_retry_and_separate_resume_starts_are_preserved(self):
        rows = [dict(event_type='controller_started', run_id='run-1'),
                dict(event_type='provider_started', run_id='run-1'),
                dict(event_type='provider_started', run_id='run-1'),
                dict(event_type='controller_started', run_id='run-2'),
                dict(event_type='provider_started', run_id='run-2')]
        self.assertEqual([rows[1], rows[2], rows[4]], token_ledger._provider_start_events(self.events(rows)))

    def test_malformed_complete_event_still_fails(self):
        path = self.events([])
        path.write_text('{broken}\n', encoding='utf-8')
        with self.assertRaises(token_ledger.LedgerError):
            token_ledger._provider_start_events(path)


if __name__ == '__main__':
    unittest.main()
