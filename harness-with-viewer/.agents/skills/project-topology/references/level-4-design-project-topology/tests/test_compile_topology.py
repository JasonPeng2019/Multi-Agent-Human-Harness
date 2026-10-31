"""Synthetic schema fixtures; these declarations are never production review evidence."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import compile_topology as c


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.source, self.review = c.migrate_texts(*c.v.build_self_test_package())

    def approve_fixture(self):
        self.review['approved_source_sha256'] = c.digest(self.source)

    def two_steps(self):
        original = self.source['steps']['STEP-001']
        original = copy.deepcopy(original)
        original['layout'] = original['layout'].replace(c.v.STEP_FAST_LANE_CANONICAL_BLOCK, 'CANONICAL_BLOCK_HERE')
        text = json.dumps(original)
        # Preserve requirement/deliverable references; give every executable identity a unique owner.
        ids = set(c.v.MI_RE.findall(text)) | set(c.v.LANE_RE.findall(text)) | set(c.v.HANDOFF_RE.findall(text))
        ids |= set(c.v.PROCESS_RE.findall(text)) | set(c.v.INVOCATION_RE.findall(text))
        import re
        ids |= set(re.findall(r'CARD-[A-Z0-9][A-Z0-9_-]*', text))
        for token in sorted(ids, key=len, reverse=True):
            text = text.replace(token, token + '-TWO')
        for before, after in [('STEP-001', 'STEP-002'), ('GATE-001', 'GATE-002'), ('LOOP-001', 'LOOP-002'), ('EDGE-001', 'EDGE-002')]:
            text = text.replace(before, after)
        self.source['steps']['STEP-002'] = json.loads(text)
        self.source['steps']['STEP-002']['layout'] = self.source['steps']['STEP-002']['layout'].replace('CANONICAL_BLOCK_HERE', c.v.STEP_FAST_LANE_CANONICAL_BLOCK)
        header = c.v.REQUIRED_TABLES[c.v.HEADINGS[8]][0]
        layout, rows = c.table_extract(self.source['topology']['root_layout'], header, 'TEST_EDGES')
        rows.append(['EDGE-002', 'STEP-002.accepted result', 'terminal', 'accepted', 'serial', 'N/A', 'incomplete'])
        self.source['topology']['root_layout'] = c.put(layout, 'TEST_EDGES', c.table(header, rows))
        doc, rows = c.table_extract(self.review['validation_markdown'], c.v.AUDIT_SCOPE_TABLE, 'TEST_AUDIT')
        rows.append([cell.replace('STEP-001', 'STEP-002') for cell in rows[0]])
        self.review['validation_markdown'] = c.put(doc, 'TEST_AUDIT', c.table(c.v.AUDIT_SCOPE_TABLE, rows))
        self.approve_fixture()

    def test_migrate_render_full_validator_and_narrative(self):
        package = list(c.v.build_self_test_package())
        package[3]['STEP-001.md'] += '\nAuthored important retained narrative about operator handoff.\n'
        source, review = c.migrate_texts(*package)
        files, fresh = c.compile_source(source, review)
        self.assertTrue(fresh)
        self.assertEqual([], c.package_errors(files, source))
        self.assertIn('Authored important retained narrative', files['steps/STEP-001.md'])

    def test_two_steps_member_addition_has_one_owner(self):
        self.two_steps()
        before, _ = c.compile_source(self.source, self.review)
        self.assertEqual([], c.package_errors(before, self.source))
        instance = self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']
        member = copy.deepcopy(instance['cards'][1])
        member['id'] += '-EXTRA'
        for name in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
            member['dispatch'][name] += '-EXTRA'
        instance['cards'].append(member)
        after, fresh = c.compile_source(self.source, self.review)
        self.assertFalse(fresh)
        self.assertEqual(before['steps/STEP-002.md'], after['steps/STEP-002.md'])
        self.assertIn('LANE-NORMAL-EXTRA', after['plan-workflow.md'])
        self.assertIn('CARD-NORMAL-M-EXTRA=worker', after['modules/M05.md'])
        self.approve_fixture()
        after, _ = c.compile_source(self.source, self.review)
        self.assertEqual([], c.package_errors(after, self.source))

    def test_private_change_impact_and_public_dependency(self):
        self.two_steps()
        self.source['steps']['STEP-002']['depends_on'] = ['interface:STEP-001']
        baseline = {'units': {key: c.digest(value) for key, value in c.units(self.source).items()}}
        self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']['cards'][1]['fields']['objective'] += '; preserve private detail'
        report = c.impact(self.source, baseline)
        self.assertIn('step:STEP-001', report['review_candidates'])
        self.assertNotIn('step:STEP-002', report['review_candidates'])
        self.source['steps']['STEP-001']['public_interface'][1] += '; altered public result'
        self.assertIn('step:STEP-002', c.impact(self.source, baseline)['review_candidates'])

    def test_entry_order_derived_union(self):
        self.two_steps()
        step = self.source['steps']['STEP-001']
        item = copy.deepcopy(step['instances']['MI-NORMAL-ACCEPT'])
        new_id = 'MI-NORMAL-SECOND'
        for card in item['cards']:
            card['id'] += '-SECOND'
            if card.get('dispatch'):
                for name in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
                    card['dispatch'][name] += '-SECOND'
        step['instances'][new_id] = item
        step['entries'][0]['path'].append(new_id)
        before, _ = c.compile_source(self.source, self.review)
        step['entries'][0]['path'].reverse()
        after, _ = c.compile_source(self.source, self.review)
        self.assertIn('| 1 | MI-NORMAL-SECOND |', after['steps/STEP-001.md'])
        self.assertEqual(before['steps/STEP-002.md'], after['steps/STEP-002.md'])

    def test_defaults_precedence_cycle_unknown_field(self):
        card = self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']['cards'][1]
        self.source['defaults'] = {'base': {'fields': {'objective': 'base objective'}},
                                   'child': {'extends': 'base', 'fields': {'objective': 'child objective'}}}
        card['extends'] = 'child'
        fields = c.expand_card(card, self.source['defaults'], 'MI-NORMAL-ACCEPT')
        self.assertEqual(card['fields']['objective'], fields['objective'])
        del card['fields']['objective']
        self.assertEqual('child objective', c.expand_card(card, self.source['defaults'], 'MI-NORMAL-ACCEPT')['objective'])
        self.source['defaults']['base']['extends'] = 'child'
        with self.assertRaisesRegex(c.SourceError, 'cycle'):
            c.expand_card(card, self.source['defaults'], 'MI-NORMAL-ACCEPT')
        self.source['defaults']['base'].pop('extends')
        card['fields']['typo'] = 'bad'
        with self.assertRaisesRegex(c.SourceError, 'unknown fields'):
            c.expand_card(card, self.source['defaults'], 'MI-NORMAL-ACCEPT')

    def test_local_manifests_aggregate_without_root_edit(self):
        step = self.source['steps']['STEP-001']
        step['manifests']['MANIFEST_4'] = [['ALLOC-001', 'isolated', 'worktree-a', 'worker', 'root-a', 'orchestrator', 'terminal', 'cleanup']]
        files, _ = c.compile_source(self.source, self.review)
        self.assertIn('| ALLOC-001 |', files['plan-workflow.md'])
        self.assertNotIn('ALLOC-001', self.source['topology']['root_layout'])

    def test_unknown_policy_dependency_fails(self):
        self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']['policy_rows'].append('P99-ROW-001')
        with self.assertRaisesRegex(c.SourceError, 'unknown policy'):
            c.compile_source(self.source, self.review)

    def test_noop_hand_edits_stale_approval_and_separation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, output = root / 'source', root / 'generated'
            mapping = root / 'mapping.json'
            c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
            self.source['topology']['root_layout'] = self.source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
            self.approve_fixture()
            c.save_source(source_dir, self.source, self.review)
            c.build(source_dir, output, mapping=mapping)
            times = {p: p.stat().st_mtime_ns for p in output.rglob('*.md')}
            c.build(source_dir, output, mapping=mapping)
            self.assertEqual(times, {p: p.stat().st_mtime_ns for p in output.rglob('*.md')})
            c.build(source_dir, output, check=True, mapping=mapping)
            path = output / 'steps/STEP-001.md'
            path.write_text(path.read_text() + '\nmanual edit\n')
            with self.assertRaisesRegex(c.SourceError, 'hand-edited'):
                c.build(source_dir, output, check=True, mapping=mapping)
            with self.assertRaisesRegex(c.SourceError, 'non-nested'):
                c.build(source_dir, source_dir / 'generated', draft=True)
            step_path = source_dir / 'steps/STEP-001.json'
            step = c.read_json(step_path)
            step['instances']['MI-NORMAL-ACCEPT']['cards'][1]['fields']['objective'] += '; revised'
            c.write_json(step_path, step)
            with self.assertRaisesRegex(c.SourceError, 'stale'):
                c.build(source_dir, output, mapping=mapping)

    def test_migration_rejects_ambiguous_policy_without_loss(self):
        package = list(c.v.build_self_test_package())
        package[1] = package[1].replace('MI-NORMAL-ACCEPT, MI-FL2-S1-REPAIR-EXIT, MI-FL2-S2-RECONCILE', 'M05')
        with self.assertRaisesRegex(c.SourceError, 'policy consumers'):
            c.migrate_texts(*package)

    def test_policy_reordering_preserves_consumer_binding(self):
        policy = self.source['topology']['policies']['P01']
        second = copy.deepcopy(policy[0])
        second['id'] = 'P01-ROW-SECOND'
        second['values'][2] = 'different concrete action'
        policy.append(second)
        target = self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']
        target['policy_rows'].remove('P01-ROW-001')
        target['policy_rows'].append(second['id'])
        policy.reverse()
        files, _ = c.compile_source(self.source, self.review)
        section = files['global-rules.md'].split('### P01', 1)[1].split('### P02', 1)[0]
        rows = c.v.extract_table(section, c.v.POLICY_TABLE)
        self.assertEqual('MI-NORMAL-ACCEPT', rows[0][-1])
        self.assertNotIn('MI-NORMAL-ACCEPT', rows[1][-1])

    def test_cli_migration_rejects_invalid_original_and_requires_reapproval(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package, target, mapping = root / 'legacy', root / 'source', root / 'mapping.json'
            c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
            self.source['topology']['root_layout'] = self.source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
            self.approve_fixture()
            files, _ = c.compile_source(self.source, self.review)
            for name, text in files.items():
                path = package / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')
            root_path = package / 'plan-workflow.md'
            original = root_path.read_text(encoding='utf-8')
            root_path.write_text(original.replace('| ROOT | N/A | worker |', '| ROOT | N/A | wrongworker |'), encoding='utf-8')
            self.assertEqual(1, c.main(['migrate', str(package), '--source', str(target), '--mapping', str(mapping)]))
            self.assertFalse(target.exists())
            root_path.write_text(original, encoding='utf-8')
            self.assertEqual(0, c.main(['migrate', str(package), '--source', str(target), '--mapping', str(mapping)]))
            source, review = c.load_source(target)
            self.assertEqual('', review['approved_source_sha256'])
            self.assertEqual(self.review['validation_markdown'], review['validation_markdown'])
            self.assertIn('source_sha256', c.impact(source, {}))

    def test_draft_keeps_accepted_impact_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, output, mapping = root / 'source', root / 'out', root / 'mapping.json'
            c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
            self.source['topology']['root_layout'] = self.source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
            self.approve_fixture()
            c.save_source(source_dir, self.source, self.review)
            c.build(source_dir, output, mapping=mapping)
            path = source_dir / 'steps/STEP-001.json'
            step = c.read_json(path)
            step['instances']['MI-NORMAL-ACCEPT']['cards'][1]['fields']['objective'] += '; changed objective'
            c.write_json(path, step)
            result = c.build(source_dir, output, draft=True, mapping=mapping)
            self.assertEqual('INVALID', result['status'])
            source, _ = c.load_source(source_dir)
            report = c.impact(source, c.read_json(source_dir / c.STATE))
            self.assertIn('instance:MI-NORMAL-ACCEPT', report['changed_units'])
            self.assertIn('| Status | INVALID |', (output / 'plan-workflow.md').read_text())

    def test_root_edges_contribute_public_dependency(self):
        self.two_steps()
        root = self.source['topology']['root_layout']
        self.source['topology']['root_layout'] = root.replace('| STEP-001.accepted result | terminal |', '| STEP-001.accepted result | STEP-002.candidate |')
        baseline = {'units': {key: c.digest(value) for key, value in c.units(self.source).items()}}
        self.source['steps']['STEP-001']['public_interface'][1] += '; new public promise'
        self.assertIn('step:STEP-002', c.impact(self.source, baseline)['review_candidates'])

    def test_owned_removed_step_pruned_but_unknown_file_protected(self):
        self.two_steps()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, output, mapping = root / 'source', root / 'out', root / 'mapping.json'
            c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
            self.source['topology']['root_layout'] = self.source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
            self.approve_fixture()
            c.save_source(source_dir, self.source, self.review)
            c.build(source_dir, output, mapping=mapping)
            (source_dir / 'steps/STEP-002.json').unlink()
            self.source['steps'].pop('STEP-002')
            header = c.v.REQUIRED_TABLES[c.v.HEADINGS[8]][0]
            layout, rows = c.table_extract(self.source['topology']['root_layout'], header, 'REMOVAL')
            self.source['topology']['root_layout'] = c.put(layout, 'REMOVAL', c.table(header, [row for row in rows if row[0] != 'EDGE-002']))
            doc, rows = c.table_extract(self.review['validation_markdown'], c.v.AUDIT_SCOPE_TABLE, 'REMOVAL')
            self.review['validation_markdown'] = c.put(doc, 'REMOVAL', c.table(c.v.AUDIT_SCOPE_TABLE, [row for row in rows if row[0] != 'STEP-002']))
            self.approve_fixture()
            c.write_json(source_dir / 'topology.json', self.source['topology'])
            c.write_json(source_dir / 'review.json', self.review)
            c.build(source_dir, output, mapping=mapping)
            self.assertFalse((output / 'steps/STEP-002.md').exists())
            extra = output / 'important-user-notes.txt'
            extra.write_text('must survive')
            with self.assertRaisesRegex(c.SourceError, 'unowned files'):
                c.build(source_dir, output, mapping=mapping)
            self.assertEqual('must survive', extra.read_text())

    def test_unused_default_cycle_and_unknown_source_file_rejected(self):
        self.source['defaults'] = {'unused': {'extends': 'unused', 'fields': {}}}
        with self.assertRaisesRegex(c.SourceError, 'cycle'):
            c.compile_source(self.source, self.review)
        with tempfile.TemporaryDirectory() as temporary:
            source_dir = Path(temporary) / 'source'
            c.save_source(source_dir, self.source, self.review)
            (source_dir / 'duplicate-definitions.json').write_text('{}')
            with self.assertRaisesRegex(c.SourceError, 'unexpected source'):
                c.load_source(source_dir)

    def test_fresh_approved_draft_without_mapping_is_never_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, output, mapping = root / 'source', root / 'out', root / 'mapping.json'
            self.source['topology']['root_layout'] = self.source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
            self.approve_fixture()
            c.save_source(source_dir, self.source, self.review)
            result = c.build(source_dir, output, draft=True)
            self.assertEqual('INVALID', result['status'])
            self.assertTrue(any('draft mode is explicitly nonaccepted' in item for item in result['errors']))
            self.assertEqual({}, c.read_json(source_dir / c.STATE)['accepted_units'])
            self.assertIn('| Status | INVALID |', (output / 'plan-workflow.md').read_text())
            self.assertIn('PLAN_STRUCTURE=INVALID', (output / 'validation.md').read_text())
            c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
            c.build(source_dir, output, mapping=mapping)
            accepted = c.read_json(source_dir / c.STATE)['accepted_units']
            self.source['steps']['STEP-001']['instances']['MI-NORMAL-ACCEPT']['cards'][1]['fields']['objective'] += '; new reviewed detail'
            self.approve_fixture()
            c.write_json(source_dir / 'steps/STEP-001.json', self.source['steps']['STEP-001'])
            c.write_json(source_dir / 'review.json', self.review)
            result = c.build(source_dir, output, draft=True)
            self.assertEqual('INVALID', result['status'])
            self.assertEqual(accepted, c.read_json(source_dir / c.STATE)['accepted_units'])

    def test_dangling_windows_reparse_point_is_rejected(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temporary:
            dangling = Path(temporary) / 'dangling-junction'
            self.assertFalse(dangling.exists())
            original_lstat = Path.lstat
            def simulated_lstat(path):
                if path == dangling:
                    return SimpleNamespace(st_mode=c.stat.S_IFDIR, st_file_attributes=0x400)
                return original_lstat(path)
            with patch.object(Path, 'lstat', simulated_lstat), patch.object(c.stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400, create=True):
                with self.assertRaisesRegex(c.SourceError, 'linked path is unsupported'):
                    c.safe_tree(dangling)

    def test_accepted_build_requires_every_review_group_pass(self):
        for mode in ('missing', 'blocked'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_dir, output, mapping = root / 'source', root / 'out', root / 'mapping.json'
                c.write_json(mapping, {'roles': {'orchestrator': {'provider': 'fixture'}, 'worker': {'provider': 'fixture'}}})
                source = copy.deepcopy(self.source)
                source['topology']['root_layout'] = source['topology']['root_layout'].replace('| mapping.json |', '| ../mapping.json |')
                review = copy.deepcopy(self.review)
                review['approved_source_sha256'] = c.digest(source)
                doc, rows = c.table_extract(review['validation_markdown'], c.v.AUDIT_GROUP_TABLE, 'REVIEW_TEST')
                if mode == 'missing':
                    rows.pop()
                else:
                    rows[-1][-1] = 'BLOCK'
                review['validation_markdown'] = c.put(doc, 'REVIEW_TEST', c.table(c.v.AUDIT_GROUP_TABLE, rows))
                c.save_source(source_dir, source, review)
                with self.assertRaisesRegex(c.SourceError, 'plan review'):
                    c.build(source_dir, output, mapping=mapping)
                self.assertFalse(output.exists())

    def test_init_is_invalid_and_never_synthetic_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'source'
            self.assertEqual(0, c.main(['init', '--source', str(source)]))
            data, review = c.load_source(source)
            files, fresh = c.compile_source(data, review)
            self.assertFalse(fresh)
            self.assertNotIn('PLAN_STRUCTURE=VALID', files['validation.md'])
            self.assertNotIn('| PASS |', files['validation.md'])
            self.assertEqual('', review['approved_source_sha256'])


if __name__ == '__main__':
    unittest.main()
