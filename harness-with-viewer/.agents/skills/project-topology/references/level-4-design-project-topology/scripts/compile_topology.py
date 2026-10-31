"""Single-owner Level-4 authoring; generated Markdown remains the runtime contract.

All JSON source is data, never executable. Layout strings preserve authored prose;
@@UPPER_CASE@@ slots are reserved generated views. Review judgments are never made
by this compiler. Run ``--help`` for migration, draft creation and safe build commands.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import stat
from pathlib import Path

import validate_execution_plan as v

VERSION = 1
IDENTITY = v.TASK_FIELDS[0]
STATE = '.build-state.json'


class SourceError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise SourceError(message)


def keys(value, allowed, required=()):
    require(isinstance(value, dict), 'expected an object')
    require(not set(value) - set(allowed), f'unknown fields: {sorted(set(value) - set(allowed))}')
    require(not set(required) - set(value), f'missing fields: {sorted(set(required) - set(value))}')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def read_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, f'duplicate JSON key {key!r} in {path}')
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def safe_tree(path):
    path = Path(path).absolute()
    def linked(item):
        try:
            info = item.lstat()
        except FileNotFoundError:
            return False
        return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))
    for item in [path, *path.parents]:
        require(not linked(item),
                f'linked path is unsupported: {item}')
    if path.exists():
        for item in path.rglob('*'):
            require(not linked(item),
                    f'linked path is unsupported: {item}')
    return path.resolve()


def separate(a, b):
    require(a != b and a not in b.parents and b not in a.parents,
            'source and generated output must be separate, non-nested directories')


def table_extract(text, header, slot):
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if v.table_cells(line) == list(header)]
    require(len(starts) == 1, f'expected exactly one {header[0]} table for {slot}')
    start = starts[0]
    end = start + 2
    while end < len(lines) and v.table_cells(lines[end]) is not None:
        end += 1
    rows = v.extract_table(''.join(lines[start:end]), header)
    require(rows is not None and all(len(r) == len(header) for r in rows), f'malformed {slot} table')
    return ''.join(lines[:start]) + f'@@{slot}@@\n' + ''.join(lines[end:]), rows


def put(layout, slot, value):
    token = f'@@{slot}@@'
    require(layout.count(token) == 1, f'layout must contain {token} exactly once')
    return layout.replace(token, value)


def table(header, rows):
    require(all(len(r) == len(header) for r in rows), f'wrong row width: {header}')
    require(all(isinstance(c, str) and '\n' not in c and '|' not in c for r in rows for c in r),
            f'table values must be single-line strings without pipes: {header}')
    return v.markdown_table(header, rows)


def ordered_instances(step):
    return list(dict.fromkeys(mi for entry in step['entries'] for mi in entry['path']))


def load_source(path):
    path = safe_tree(path)
    require({child.name for child in path.iterdir()} <= {'topology.json', 'review.json', 'card-defaults.json', 'steps', 'modules', STATE}, 'unexpected source root file or directory')
    top = read_json(path / 'topology.json')
    keys(top, ('schema_version', 'root_layout', 'global_layout', 'roles', 'policies',
               'shared_handoffs', 'shared_manifests', 'mapping_name', 'mapping_roles'),
         ('schema_version', 'root_layout', 'global_layout', 'roles', 'policies',
          'shared_handoffs', 'shared_manifests', 'mapping_name', 'mapping_roles'))
    require(top['schema_version'] == VERSION, 'unsupported source schema_version')
    source = {'topology': top, 'steps': {}, 'modules': {},
              'defaults': read_json(path / 'card-defaults.json')}
    for category, pattern in (('steps', r'STEP-[A-Z0-9][A-Z0-9_-]*'), ('modules', r'M\d{2}')):
        for child in sorted((path / category).iterdir()):
            require(child.is_file() and child.suffix == '.json' and re.fullmatch(pattern, child.stem),
                    f'unexpected source item: {child}')
            source[category][child.stem] = read_json(child)
    require(set(source['modules']) == set(v.MODULE_IDS), 'source requires M01 through M10 libraries')
    review = read_json(path / 'review.json')
    keys(review, ('validation_markdown', 'approved_source_sha256'), ('validation_markdown', 'approved_source_sha256'))
    return source, review


def save_source(path, source, review):
    path = safe_tree(path)
    require(not path.exists() or not any(path.iterdir()), f'source destination is not empty: {path}')
    write_json(path / 'topology.json', source['topology'])
    write_json(path / 'card-defaults.json', source['defaults'])
    for category in ('steps', 'modules'):
        (path / category).mkdir(parents=True, exist_ok=True)
        for name, value in source[category].items():
            write_json(path / category / (name + '.json'), value)
    write_json(path / 'review.json', review)


def expand_card(card, defaults, instance_id):
    keys(card, ('kind', 'id', 'identity', 'fields', 'extends', 'layout', 'dispatch'),
         ('kind', 'id', 'identity', 'fields', 'layout'))
    require(card['kind'] in ('Governing', 'Member'), 'unknown card kind')
    def resolve(name, trail):
        require(name in defaults, f'unknown card default {name}')
        require(name not in trail, f'card-default inheritance cycle: {trail + [name]}')
        definition = defaults[name]
        keys(definition, ('extends', 'fields'), ('fields',))
        values = resolve(definition['extends'], trail + [name]) if definition.get('extends') else {}
        keys(definition['fields'], v.TASK_FIELDS[1:])
        values.update(definition['fields'])
        return values
    fields = resolve(card['extends'], []) if card.get('extends') else {}
    keys(card['fields'], v.TASK_FIELDS[1:])
    fields.update(card['fields'])
    require(set(fields) == set(v.TASK_FIELDS[1:]), f'{card["id"]}: missing concrete task fields')
    identity = card['identity']
    keys(identity, ('schema', 'deliverable_id', 'stage_cohort_id', 'gate_id', 'loop_id'),
         ('schema', 'deliverable_id', 'stage_cohort_id', 'gate_id', 'loop_id'))
    identities = {'schema': identity['schema'], 'card_id': card['id'], 'module_instance_id': instance_id,
                  **{k: value for k, value in identity.items() if k != 'schema'}}
    values = {IDENTITY: '; '.join(f'{key}={value}' for key, value in identities.items()), **fields}
    dispatch = card.get('dispatch')
    if dispatch:
        keys(dispatch, ('lane_id', 'handoff_id', 'process_id', 'invocation_id', 'lane', 'handoff'),
             ('lane_id', 'handoff_id', 'process_id', 'invocation_id', 'lane', 'handoff'))
        for name, value in values.items():
            for token in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
                value = value.replace('${' + token + '}', dispatch[token])
            values[name] = value
    require(not any('${' in val for val in values.values()), f'unresolved card reference in {card["id"]}')
    return values


def compile_source(source, review):
    """Pure compilation. Return filename->text and approval freshness; never assign PASS."""
    top = source['topology']
    # Reject invalid unused defaults too: all source definitions must be well-formed.
    for default_name in source['defaults']:
        trail, current = [], default_name
        while current:
            require(current in source['defaults'], f'unknown card default {current}')
            require(current not in trail, f'card-default inheritance cycle: {trail + [current]}')
            trail.append(current)
            definition = source['defaults'][current]
            keys(definition, ('extends', 'fields'), ('fields',))
            keys(definition['fields'], v.TASK_FIELDS[1:])
            current = definition.get('extends')
    root = top['root_layout']
    global_text = top['global_layout']
    files, instances, step_indexes, gate_indexes, lane_rows = {}, {}, [], [], []
    handoffs = copy.deepcopy(top['shared_handoffs'])
    manifests = copy.deepcopy(top['shared_manifests'])
    role_rows = []
    for role in top['roles']:
        keys(role, set(v.ROLE_TABLE) - {'Directs'}, set(v.ROLE_TABLE) - {'Directs'})
        directs = [r['Workflow role'] for r in top['roles'] if r['Reports to'] == role['Workflow role']]
        role_rows.append([', '.join(directs) or 'N/A' if key == 'Directs' else role[key] for key in v.ROLE_TABLE])
    root = put(root, 'ROLES', table(v.ROLE_TABLE, role_rows))
    for step_id, step in sorted(source['steps'].items()):
        keys(step, ('layout', 'contract', 'gates', 'entries', 'instances', 'public_interface', 'manifests', 'depends_on'),
             ('layout', 'contract', 'gates', 'entries', 'instances', 'public_interface', 'manifests'))
        sequence = ordered_instances(step)
        require(set(sequence) == set(step['instances']), f'{step_id}: orphan or unresolved instance')
        entry_rows = []
        for entry in step['entries']:
            keys(entry, ('values', 'path'), ('values', 'path'))
            require(len(entry['values']) == len(v.STEP_ENTRY_TABLE) - 1, 'entry values omit only path')
            row = entry['values'][:]
            row.insert(3, ' -> '.join(entry['path']))
            entry_rows.append(row)
        composition = []
        for number, instance_id in enumerate(sequence, 1):
            require(instance_id not in instances, f'duplicate instance owner: {instance_id}')
            item = step['instances'][instance_id]
            keys(item, ('module', 'layout', 'cards', 'binding', 'policy_rows', 'depends_on'),
                 ('module', 'layout', 'cards', 'binding', 'policy_rows'))
            require(item['module'] in source['modules'], f'unknown module {item["module"]}')
            composition.append([str(number), instance_id, item['module'], *item['binding']])
            card_texts, inventory = [], []
            for card in item['cards']:
                values = expand_card(card, source['defaults'], instance_id)
                card_layout = card['layout'].replace('${card_kind}', card['kind']).replace('${card_id}', card['id'])
                require(card_layout.splitlines()[0] == f'##### {card["kind"]} task card: {card["id"]}', 'card heading identity mismatch')
                card_texts.append(put(card_layout, 'CARD_FIELDS', table(('Field', 'Value'),
                                                    [[key, values[key]] for key in v.TASK_FIELDS])))
                if card['kind'] == 'Member':
                    require('dispatch' in card, f'member {card["id"]} has no dispatch lifecycle')
                    inventory.append(f'{card["id"]}={values["workflow_role"]}')
                    dispatch = card['dispatch']
                    def expand_cells(cells):
                        out = []
                        for val in cells:
                            for key in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
                                val = val.replace('${' + key + '}', dispatch[key])
                            out.append(val)
                        return out
                    lane_rows.append([dispatch['lane_id'], instance_id, values['workflow_role'],
                                      *expand_cells(dispatch['lane'])])
                    handoffs.append([dispatch['handoff_id'], values['workflow_role'],
                                     *expand_cells(dispatch['handoff'])])
            instance_layout = item['layout'].replace('${instance_id}', instance_id).replace('${module_id}', item['module'])
            require(instance_layout.startswith(f'### {instance_id} - {item["module"]}:'), 'instance heading identity mismatch')
            body = put(instance_layout, 'CARDS', '\n\n'.join(card_texts))
            body = put(body, 'MEMBER_INVENTORY', ', '.join(inventory))
            instances[instance_id] = (item, body)
        keys(step['contract'], v.STEP_CONTRACT_FIELDS[1:], v.STEP_CONTRACT_FIELDS[1:])
        step_layout = step['layout'].replace('${step_id}', step_id)
        require(step_layout.startswith(f'# {step_id} - '), 'step heading identity mismatch')
        layout = put(step_layout, 'CONTRACT', table(('Field', 'Value'),
                     [[key, step_id if key == 'Step ID' else step['contract'][key]] for key in v.STEP_CONTRACT_FIELDS]))
        layout = put(layout, 'GATES', table(v.STEP_GATE_TABLE, [gate['definition'] for gate in step['gates']]))
        layout = put(layout, 'ENTRIES', table(v.STEP_ENTRY_TABLE, entry_rows))
        layout = put(layout, 'COMPOSITION', table(v.STEP_COMPOSITION_TABLE, composition))
        files[f'steps/{step_id}.md'] = layout
        require(len(step['public_interface']) == 2, 'public_interface owns distinct input/output summary only')
        gate_ids = [token for gate in step['gates'] for token in re.findall(r'\bGATE-[A-Z0-9][A-Z0-9._-]*', gate['definition'][0])]
        step_indexes.append([step_id, f'steps/{step_id}.md', *step['public_interface'],
                             ', '.join(gate_ids) or 'N/A', step['contract']['Acceptance owner']])
        for gate in step['gates']:
            keys(gate, ('definition', 'public_summary'), ('definition', 'public_summary'))
            row = gate['definition']
            require(len(gate['public_summary']) == 3, 'gate public summary owns outcome, forward description, return reference')
            public_id = re.findall(r'\bGATE-[A-Z0-9][A-Z0-9._-]*', row[0])
            require(len(public_id) == 1, 'one public gate per gate definition is required')
            gate_indexes.append([public_id[0], step_id, f'steps/{step_id}.md', row[1], *gate['public_summary']])
        keys(step['manifests'], manifests.keys())
        for key, rows in step['manifests'].items():
            manifests[key].extend(rows)
    root = put(root, 'STEP_INDEX', table(v.REQUIRED_TABLES[v.HEADINGS[6]][0], step_indexes))
    root = put(root, 'GATE_INDEX', table(v.REQUIRED_TABLES[v.HEADINGS[8]][3], gate_indexes))
    root = put(root, 'LANES', table(v.REQUIRED_TABLES[v.HEADINGS[10]][0], lane_rows))
    root = put(root, 'HANDOFFS', table(v.REQUIRED_TABLES[v.HEADINGS[10]][3], handoffs))
    for key, rows in manifests.items():
        real = [row for row in rows if row[0] != 'N/A']
        root = put(root, key, table(v.REQUIRED_TABLES[v.HEADINGS[10]][int(key.split('_')[1])], real or rows))
    for module_id, module in sorted(source['modules'].items()):
        keys(module, ('layout', 'selection_reason'), ('layout', 'selection_reason'))
        members = [(mi, item, body) for mi, (item, body) in instances.items() if item['module'] == module_id]
        selection = [[module_id, 'SELECTED' if members else 'OMITTED',
                      ', '.join(mi for mi, _, _ in members) or 'N/A', module['selection_reason']]]
        module_layout = module['layout'].replace('${module_id}', module_id)
        require(module_layout.startswith(f'# {module_id} - '), 'module heading identity mismatch')
        body = put(module_layout, 'SELECTION', table(v.MODULE_SELECTION_TABLE, selection))
        files[f'modules/{module_id}.md'] = put(body, 'INSTANCES', '\n\n'.join(text for _, _, text in members))
    for key, policy in top['policies'].items():
        rows = []
        for row in policy:
            keys(row, ('id', 'values'), ('id', 'values'))
            consumers = [mi for mi, (item, _) in instances.items() if row['id'] in item['policy_rows']]
            rows.append([*row['values'], ', '.join(consumers) or 'N/A'])
        global_text = put(global_text, key, table(v.POLICY_TABLE, rows))
    policy_ids = [row['id'] for rows in top['policies'].values() for row in rows]
    require(len(policy_ids) == len(set(policy_ids)), 'duplicate policy row identity')
    known_policies = set(policy_ids)
    for item, _ in instances.values():
        require(set(item['policy_rows']) <= known_policies, 'unknown policy applicability row')
    fresh = review['approved_source_sha256'] == digest(source)
    validation = review['validation_markdown']
    if not fresh:
        validation = validation.replace('PLAN_STRUCTURE=VALID', 'PLAN_STRUCTURE=INVALID')
        validation += '\nCOMPILER_APPROVAL=STALE: source changed; independent review must be rebound.\n'
        root = re.sub(r'(?m)^\| Status \|.*$', '| Status | INVALID |', root)
    files.update({'plan-workflow.md': root, 'global-rules.md': global_text, 'validation.md': validation})
    require(not any(re.search(r'@@[A-Z_0-9]+@@', text) for text in files.values()), 'unresolved generated slot')
    return files, fresh


def migrate_texts(root, global_text, validation, steps, modules, mapping_name='mapping.json', mapping_roles=None):
    """Normalize supported validated legacy shapes; preserve all unowned narrative verbatim."""
    top = {'schema_version': VERSION, 'mapping_name': mapping_name,
           'mapping_roles': sorted(mapping_roles or {'orchestrator', 'worker'})}
    source = {'topology': top, 'steps': {}, 'modules': {}, 'defaults': {}}
    root, roles = table_extract(root, v.ROLE_TABLE, 'ROLES')
    top['roles'] = [{key: value for key, value in zip(v.ROLE_TABLE, row) if key != 'Directs'} for row in roles]
    root, indexes = table_extract(root, v.REQUIRED_TABLES[v.HEADINGS[6]][0], 'STEP_INDEX')
    root, gates = table_extract(root, v.REQUIRED_TABLES[v.HEADINGS[8]][3], 'GATE_INDEX')
    root, lanes = table_extract(root, v.REQUIRED_TABLES[v.HEADINGS[10]][0], 'LANES')
    root, handoffs = table_extract(root, v.REQUIRED_TABLES[v.HEADINGS[10]][3], 'HANDOFFS')
    top['shared_manifests'] = {}
    for index in (1, 2, 4, 5):
        key = f'MANIFEST_{index}'
        root, rows = table_extract(root, v.REQUIRED_TABLES[v.HEADINGS[10]][index], key)
        top['shared_manifests'][key] = rows
    lane_map = {row[0]: row for row in lanes}
    handoff_map = {row[0]: row for row in handoffs}
    all_instances = {}
    for name, text in sorted(modules.items()):
        module_id = Path(name).stem
        layout, selection = table_extract(text, v.MODULE_SELECTION_TABLE, 'SELECTION')
        matches = list(v.INSTANCE_RE.finditer(layout))
        if matches:
            prefix = layout[:matches[0].start()]
        else:
            prefix = layout
        require(not matches or not prefix.split(v.MODULE_HEADINGS[3], 1)[1].strip(),
                'migration requires configured-instance preamble to be empty; relocate its authored narrative explicitly')
        if not matches:
            # Preserve omitted-module rationale and configured-section prose as authored.
            prefix = layout
        for i, match in enumerate(matches):
            block = layout[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(layout)]
            instance_id = match.group(1)
            local_start = block.index('#### Local instructions') + len('#### Local instructions')
            local_end = block.index('#### Outputs and results', local_start)
            local = block[local_start:local_end]
            card_matches = list(v.TASK_CARD_RE.finditer(local))
            require(card_matches and not local[:card_matches[0].start()].strip(),
                    f'{instance_id}: non-card local preamble requires explicit migration')
            cards = []
            for n, cm in enumerate(card_matches):
                card_body = local[cm.start():card_matches[n + 1].start() if n + 1 < len(card_matches) else len(local)]
                card_layout, rows = table_extract(card_body, ('Field', 'Value'), 'CARD_FIELDS')
                fields = dict(rows)
                raw_identity = fields.pop(IDENTITY)
                identity = dict(re.findall(r'\b([a-z_]+)=([A-Za-z0-9][A-Za-z0-9._-]*)\b', raw_identity))
                require(set(identity) == {'schema', 'card_id', 'module_instance_id', 'deliverable_id', 'stage_cohort_id', 'gate_id', 'loop_id'},
                        'identity contains unsupported narrative or keys')
                remainder = re.sub(r'\b[a-z_]+=[A-Za-z0-9][A-Za-z0-9._-]*\b', '', raw_identity)
                require(not remainder.strip(' ;'), 'identity narrative cannot be discarded')
                identity.pop('card_id'); identity.pop('module_instance_id')
                card = {'kind': cm.group(1), 'id': cm.group(2), 'identity': identity,
                        'fields': fields, 'layout': card_layout.rstrip().replace(f'##### {cm.group(1)} task card: {cm.group(2)}', '##### ${card_kind} task card: ${card_id}', 1)}
                if card['kind'] == 'Member':
                    runtime = ' '.join(fields.values())
                    dispatch = {}
                    for key, regex in [('lane_id', v.LANE_RE), ('handoff_id', v.HANDOFF_RE),
                                       ('process_id', v.PROCESS_RE), ('invocation_id', v.INVOCATION_RE)]:
                        values = sorted(set(regex.findall(runtime)))
                        require(len(values) == 1, f'{card["id"]}: ambiguous {key}')
                        dispatch[key] = values[0]
                    lane = lane_map.pop(dispatch['lane_id'], None)
                    handoff = handoff_map.pop(dispatch['handoff_id'], None)
                    require(lane is not None and handoff is not None, 'missing or shared member manifest')
                    require(lane[1:3] == [instance_id, fields['workflow_role']] and handoff[1] == fields['workflow_role'],
                            'member manifest identity disagrees')
                    dispatch['lane'] = lane[3:]
                    dispatch['handoff'] = handoff[2:]
                    for key, val in list(fields.items()):
                        for token in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
                            val = re.sub(r'\b' + re.escape(dispatch[token]) + r'\b', '${' + token + '}', val)
                        fields[key] = val
                    for name2 in ('lane', 'handoff'):
                        for j, val in enumerate(dispatch[name2]):
                            for token in ('lane_id', 'handoff_id', 'process_id', 'invocation_id'):
                                val = re.sub(r'\b' + re.escape(dispatch[token]) + r'\b', '${' + token + '}', val)
                            dispatch[name2][j] = val
                    card['dispatch'] = dispatch
                cards.append(card)
            block = block[:local_start] + '\n\n@@CARDS@@\n\n' + block[local_end:]
            inv_pattern = r'\bCARD-[A-Z0-9][A-Z0-9_-]*\s*=\s*[A-Za-z][A-Za-z0-9._-]*(?:\s*[,;]\s*CARD-[A-Z0-9][A-Z0-9_-]*\s*=\s*[A-Za-z][A-Za-z0-9._-]*)*'
            owner_start = block.index('#### Owner and roles')
            owner_end = block.index('#### Preconditions', owner_start)
            owner = block[owner_start:owner_end]
            owner, count = re.subn(inv_pattern, '@@MEMBER_INVENTORY@@', owner)
            require(count == 1, f'{instance_id}: inventory must be one contiguous list; relocate interleaved narrative explicitly')
            block = block[:owner_start] + owner + block[owner_end:]
            all_instances[instance_id] = {'module': module_id, 'layout': block.rstrip().replace(f'### {instance_id} - {module_id}:', '### ${instance_id} - ${module_id}:', 1), 'cards': cards,
                                          'policy_rows': [], 'binding': []}
        source['modules'][module_id] = {'layout': prefix.rstrip().replace(f'# {module_id} - ', '# ${module_id} - ', 1) + '\n\n@@INSTANCES@@\n',
                                        'selection_reason': selection[0][3]}
    require(not lane_map, 'unowned lanes require explicit ownership before migration')
    top['shared_handoffs'] = list(handoff_map.values())
    for name, text in sorted(steps.items()):
        step_id = Path(name).stem
        layout, contract = table_extract(text, ('Field', 'Value'), 'CONTRACT')
        layout, gate_definitions = table_extract(layout, v.STEP_GATE_TABLE, 'GATES')
        layout, entries = table_extract(layout, v.STEP_ENTRY_TABLE, 'ENTRIES')
        layout, composition = table_extract(layout, v.STEP_COMPOSITION_TABLE, 'COMPOSITION')
        step_instances = {}
        for row in composition:
            require(row[1] in all_instances, f'{row[1]} absent or owned by multiple steps')
            item = all_instances.pop(row[1])
            require(item['module'] == row[2], 'composition module mismatch')
            item['binding'] = row[3:]
            step_instances[row[1]] = item
        owned_index = [row for row in indexes if row[0] == step_id]
        require(len(owned_index) == 1, f'{step_id}: missing public index')
        source['steps'][step_id] = {'layout': layout.replace(f'# {step_id} - ', '# ${step_id} - ', 1), 'entries': [
            {'values': row[:3] + row[4:], 'path': v.MI_RE.findall(row[3])} for row in entries],
            'instances': step_instances, 'public_interface': owned_index[0][2:4],
            'contract': {key: val for key, val in contract if key != 'Step ID'}, 'gates': [], 'manifests': {}}
        for definition in gate_definitions:
            ids = re.findall(r'\bGATE-[A-Z0-9][A-Z0-9._-]*', definition[0])
            matching = [row for row in gates if row[1] == step_id and row[0] in ids]
            require(len(matching) == 1, f'{step_id}: gate public summary is ambiguous')
            row = matching[0]
            require(row[3] == definition[1], 'gate class disagrees')
            source['steps'][step_id]['gates'].append({'definition': definition, 'public_summary': row[4:]})
    require(not all_instances, 'instances lack step ownership')
    top['policies'] = {}
    policy_matches = list(re.finditer(r'(?m)^### (P\d{2})[^\n]*$', global_text))
    for match in reversed(policy_matches):
        end = next((m.start() for m in policy_matches if m.start() > match.start()), len(global_text))
        block = global_text[match.start():end]
        key = match.group(1)
        block, rows = table_extract(block, v.POLICY_TABLE, key)
        top['policies'][key] = [{'id': f'{key}-ROW-{i + 1:03}', 'values': row[:-1]} for i, row in enumerate(rows)]
        for i, row in enumerate(rows):
            consumers = v.MI_RE.findall(row[-1])
            remainder = v.MI_RE.sub('', row[-1]).strip(' ,;')
            require(not remainder, f'{key}: policy consumers must be explicit MI list; unsupported: {row[-1]}')
            for mi in consumers:
                owners = [step['instances'][mi] for step in source['steps'].values() if mi in step['instances']]
                require(len(owners) == 1, f'{key}: unresolved consumer {mi}')
                owners[0]['policy_rows'].append(f'{key}-ROW-{i + 1:03}')
        global_text = global_text[:match.start()] + block + global_text[end:]
    top['root_layout'], top['global_layout'] = root, global_text
    review = {'validation_markdown': validation, 'approved_source_sha256': digest(source)}
    return source, review


def package_errors(files, source, mapping_path=None, output=None):
    top = source['topology']
    roles = set(top['mapping_roles'])
    if mapping_path:
        roles, errors = v.load_mapping(mapping_path)
        if errors:
            return errors
    return v.validate_package_texts(files['plan-workflow.md'], files['global-rules.md'], files['validation.md'],
        {Path(k).name: val for k, val in files.items() if k.startswith('steps/')},
        {Path(k).name: val for k, val in files.items() if k.startswith('modules/')},
        roles, top['mapping_name'], mapping_path, output)


def units(source):
    result = {'root': {key: value for key, value in source['topology'].items() if key not in ('roles', 'policies')}}
    result.update({f'role:{role["Workflow role"]}': role for role in source['topology']['roles']})
    result.update({f'policy:{policy}': rows for policy, rows in source['topology']['policies'].items()})
    for module, data in source['modules'].items():
        result[f'module:{module}'] = data
    for name, data in source['defaults'].items():
        result[f'default:{name}'] = data
    for step, data in source['steps'].items():
        result[f'step:{step}'] = {k: val for k, val in data.items() if k != 'instances'}
        result[f'interface:{step}'] = {'contract': data['contract'], 'public_interface': data['public_interface'],
                                      'gates': data['gates']}
        for mi, item in data['instances'].items():
            result[f'instance:{mi}'] = item
    return result


def impact(source, state):
    current = units(source)
    before = state.get('accepted_units', state.get('units', {}))
    changed = sorted(key for key in set(current) | set(before) if digest(current.get(key)) != before.get(key))
    deps = {key: set() for key in current}
    owner = {mi: f'instance:{mi}' for step in source['steps'].values() for mi in step['instances']}
    for step_id, step in source['steps'].items():
        skey = f'step:{step_id}'
        deps[skey].update(f'instance:{mi}' for mi in ordered_instances(step))
        deps[skey].update(step.get('depends_on', []))
        for mi, item in step['instances'].items():
            key = f'instance:{mi}'
            deps[key].add(f'module:{item["module"]}')
            policy_owners = {row['id']: policy for policy, rows in source['topology']['policies'].items() for row in rows}
            require(set(item['policy_rows']) <= set(policy_owners), 'unknown policy applicability row')
            deps[key].update(f'policy:{policy_owners[row]}' for row in item['policy_rows'])
            deps[key].update(f'role:{expand_card(card, source["defaults"], mi)["workflow_role"]}' for card in item['cards'])
            deps[key].update(item.get('depends_on', []))
            deps[key].update(owner[token] for token in v.MI_RE.findall(json.dumps(item)) if token in owner and token != mi)
            deps[key].update(f'default:{card["extends"]}' for card in item['cards'] if card.get('extends'))
    edge_header = v.REQUIRED_TABLES[v.HEADINGS[8]][0]
    for edge in v.extract_table(source['topology']['root_layout'], edge_header) or []:
        producers, consumers = v.STEP_RE.findall(edge[1]), v.STEP_RE.findall(edge[2])
        for consumer in consumers:
            if f'step:{consumer}' in deps:
                deps[f'step:{consumer}'].update(f'interface:{producer}' for producer in producers if producer != consumer)
    for role in source['topology']['roles']:
        if role['Reports to'] != 'N/A':
            deps[f'role:{role["Workflow role"]}'].add(f'role:{role["Reports to"]}')
    for name, data in source['defaults'].items():
        if data.get('extends'):
            deps[f'default:{name}'].add(f'default:{data["extends"]}')
    for key, values in deps.items():
        require(values <= set(current), f'{key}: unknown explicit dependency: {sorted(values - set(current))}')
    impacted = set(changed)
    while True:
        following = impacted | {key for key, values in deps.items() if values & impacted}
        if following == impacted:
            break
        impacted = following
    if 'root' in changed:
        impacted.update(current)  # Shared-contract changes need broad assessment.
    return {'source_sha256': digest(source), 'baseline': 'accepted source' if before else 'none; no accepted source baseline',
            'changed_units': changed, 'review_candidates': sorted(impacted),
            'dependencies': {k: sorted(val) for k, val in deps.items()},
            'evidence_credit': 'Not adjudicated. Trace actual inputs and observations; this report neither reruns nor preserves runtime credit.'}


def build(source_dir, output, draft=False, check=False, mapping=None):
    source_dir, output = safe_tree(source_dir), safe_tree(output)
    separate(source_dir, output)
    require(draft or mapping is not None, 'accepted build/check requires canonical --mapping; draft may omit it')
    source, review = load_source(source_dir)
    files, fresh = compile_source(source, review)
    errors = package_errors(files, source, mapping, output)
    if draft:
        errors.insert(0, 'draft mode is explicitly nonaccepted; canonical mapping and accepted build are required before execution')
    if not fresh:
        errors.insert(0, 'review approval binding is stale for material source')
    if errors and not draft:
        raise SourceError('\n'.join(errors))
    if errors:
        files['plan-workflow.md'] = re.sub(r'(?m)^\| Status \|.*$', '| Status | INVALID |', files['plan-workflow.md'])
        files['validation.md'] = files['validation.md'].replace('PLAN_STRUCTURE=VALID', 'PLAN_STRUCTURE=INVALID')
        files['validation.md'] += '\nCOMPILER_BUILD=INVALID: draft; not executable or accepted.\n'
    state_path = source_dir / STATE
    state = read_json(state_path) if state_path.exists() else {}
    if state:
        require(state.get('output') == str(output), 'source already bound to another output; use a separate source copy')
    expected_old = state.get('files', {})
    if output.exists():
        require(all(str(p.relative_to(output)).replace('\\', '/') in {'steps', 'modules'} for p in output.rglob('*') if p.is_dir()), 'output contains an unowned directory')
    existing = {str(p.relative_to(output)).replace('\\', '/'): p for p in output.rglob('*') if p.is_file()} if output.exists() else {}
    require(not set(existing) - set(expected_old), 'output contains unowned files; choose an empty output directory')
    for name, path in existing.items():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected_old[name], f'generated file was hand-edited: {name}')
    report = impact(source, state)
    if check:
        require(fresh and not errors, 'source/package is not accepted')
        require(set(existing) == set(files), 'generated file inventory is stale')
        require(all(existing[name].read_text(encoding='utf-8') == text for name, text in files.items()),
                'generated projection differs from current source')
        return report
    for name in set(expected_old) - set(files):
        target = (output / name).resolve()
        require(output in target.parents, 'obsolete generated path escapes output')
        if target.exists():
            target.unlink()  # Exact manifest-owned file, hash checked above; never recursive.
    for name, text in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = text.encode('utf-8')
        if not path.exists() or path.read_bytes() != encoded:
            path.write_bytes(encoded)
    new_state = {'schema_version': VERSION, 'output': str(output), 'source_sha256': digest(source),
                 'files': {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()},
                 'units': {key: digest(value) for key, value in units(source).items()},
                 'accepted_units': state.get('accepted_units', {}) if errors else {key: digest(value) for key, value in units(source).items()}}
    if new_state != state:
        write_json(state_path, new_state)
    return {**report, 'status': 'INVALID' if errors else 'VALID', 'errors': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('build', 'check'):
        cmd = commands.add_parser(name)
        cmd.add_argument('source', type=Path)
        cmd.add_argument('--output', required=True, type=Path)
        cmd.add_argument('--mapping', type=Path)
        if name == 'build':
            cmd.add_argument('--draft', action='store_true')
    cmd = commands.add_parser('impact'); cmd.add_argument('source', type=Path)
    cmd = commands.add_parser('migrate'); cmd.add_argument('package', type=Path)
    cmd.add_argument('--source', required=True, type=Path); cmd.add_argument('--mapping', type=Path)
    cmd = commands.add_parser('init'); cmd.add_argument('--source', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in ('build', 'check'):
            result = build(args.source, args.output, getattr(args, 'draft', False), args.command == 'check', args.mapping)
        elif args.command == 'impact':
            source, _ = load_source(args.source)
            path = args.source / STATE
            result = impact(source, read_json(path) if path.exists() else {})
        else:
            if args.command == 'migrate':
                require(args.mapping is not None, 'migration requires canonical --mapping')
                separate(safe_tree(args.source), safe_tree(args.package))
                root, rules, validation, steps, modules, errors = v.load_package(safe_tree(args.package))
                require(not errors, '\n'.join(errors))
                role_rows = v.extract_table(root, v.ROLE_TABLE) or []
                roles, mapping_errors = v.load_mapping(args.mapping)
                require(not mapping_errors, '\n'.join(mapping_errors))
                original_errors = v.validate_package_texts(root, rules, validation, steps, modules, roles, args.mapping.name, args.mapping, args.package)
                require(not original_errors, 'legacy input is invalid; migration cannot repair it while preserving approval:\n' + '\n'.join(original_errors))
                # Preserve canonical mapping target when projections are built at a new path.
                mapping_rows = v.extract_table(root, v.PACKAGE_DEPENDENCY_TABLE)
                mapping_row = next(row for row in mapping_rows if row[0] == 'Agent mapping')
                root = root.replace('| ' + ' | '.join(mapping_row) + ' |', '| ' + ' | '.join([mapping_row[0], args.mapping.resolve().as_posix(), *mapping_row[2:]]) + ' |')
                mapping_name = args.mapping.name if args.mapping else 'mapping.json'
                source, review = migrate_texts(root, rules, validation, steps, modules, mapping_name, roles)
                files, _ = compile_source(source, review)
                errors = package_errors(files, source, args.mapping, args.package)
                require(not errors, 'migration did not produce an accepted equivalent package:\n' + '\n'.join(errors))
                review['approved_source_sha256'] = ''  # Preserve earlier evidence, never confer approval on migrated source.
            else:
                # Fixture supplies schema shape only. Remove ALL synthetic acceptance assertions.
                source, review = migrate_texts(*v.build_self_test_package())
                for module in source['modules'].values():
                    module['selection_reason'] = 'TODO author the project-specific module selection reason'
                source['topology']['root_layout'] = source['topology']['root_layout'].replace('Validator Self Test', 'New Draft').replace('VALIDATED', 'INVALID')
                review = {'approved_source_sha256': '', 'validation_markdown':
                          '# New Draft - Plan Validation\n\n' + v.HEADINGS[15] + '\n\nTODO supply actual rule applications.\n\n' +
                          v.HEADINGS[16] + '\n\nTODO obtain four independent reviews and record actual judgments.\n\nPLAN_STRUCTURE=INVALID\n'}
            save_source(args.source, source, review)
            result = {'source': str(args.source), 'source_sha256': digest(source),
                      'status': 'INVALID scaffold; replace illustrative fixture facts before review' if args.command == 'init' else 'MIGRATED'}
        print(json.dumps(result, indent=2))
        return 0
    except (SourceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
