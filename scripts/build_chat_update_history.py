#!/usr/bin/env python3
"""Rebuild the inspectable Chat update history from recorded repository evidence."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'chat/§wyrlz/assets/chat-updates-v1.json'
REGISTRY_REF = 'origin/runtime'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)

def build():
    # Do not silently present a shallow slice as the complete recorded history.
    assert git('rev-parse', '--is-shallow-repository').strip() == 'false'
    head = git('rev-parse', REGISTRY_REF).strip()
    records = []
    for row in git('log', REGISTRY_REF, '--format=%H%x09%ad%x09%s', '--date=short', '--', 'versions/web-chat.txt').splitlines():
        commit, date, title = row.split('\t', 2)
        values = dict(line.split('=', 1) for line in git('show', commit + ':versions/web-chat.txt').splitlines() if '=' in line)
        records.append({
            'id': 'registry-' + commit, 'version': values.get('VERSION', ''),
            'date': date, 'title': title, 'changes': [title], 'kind': 'Version registry record',
            'source': {'commit': commit, 'path': 'versions/web-chat.txt'},
        })
    changelog_path = 'SWRLZ_VERCEL_CHAT_CHANGELOG.md'
    changelog_commit = git('log', '-1', '--format=%H', '--', changelog_path).strip()
    changelog = (ROOT / changelog_path).read_text()
    for number, section in enumerate(re.split(r'^## ', changelog, flags=re.M)[1:]):
        heading, _, body = section.partition('\n')
        if 'Chat ' not in heading:
            continue
        date = re.search(r'\d{4}-\d{2}-\d{2}', heading).group()
        label = re.search(r'Chat ([\d.]+(?:-[\d.]+)?)', heading).group(1)
        bullets = [line[2:].strip().rstrip(';') for line in body.splitlines() if line.startswith('- ')]
        if not bullets:
            bullets = [' '.join(p.strip() for p in body.strip().splitlines() if p.strip())]
        records.append({
            'id': 'legacy-changelog-' + str(number), 'version': label, 'date': date,
            'title': heading.split(' — ')[0], 'changes': bullets, 'kind': 'Historical changelog record',
            'source': {'commit': changelog_commit, 'path': changelog_path},
        })
    records.insert(0, {
        'id': 'qwen-project-generation-6240d715', 'date': '2026-10-24',
        'title': 'Qwen project generation and verified cube viewer',
        'changes': ['Qwen 2.5 Coder 7B handles inferred coding requests alongside the 700M conversational model.',
                    'A generic cube viewer passed its recorded browser checks. Broader editor and project capability remained open.'],
        'kind': 'Source update',
        'source': {'commit': '6240d7151692898b9f30e75675707083ddb7f4cc', 'path': 'docs/engineering/entries/2026-10-24_QWEN_PROJECT_GENERATION.md'},
    })
    latest = {
        'id': 'editor-project-completion-20261025', 'date': '2026-10-25',
        'title': 'Project downloads, longer answers and Chat updates',
        'changes': [
            'Download generated project files together in a ZIP from their saved Chat artifact.',
            'New projects keep their own files and identity; follow-up edits retain the selected project.',
            'Larger response allowances give the 700M model and coding model more room to finish their answers.',
            'Open Chat updates from the side menu to read the newest notes and all recorded earlier updates.',
            'Choose “Don’t show again for this update” below to hide this popup until a newer update arrives.',
        ],
    }
    records.insert(0, {**latest, 'kind': 'Source update',
                       'source': {'commit': 'f925e2012ed7ece820e3272700bc6619846c2085',
                                  'path': 'docs/engineering/entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md'}})
    latest = {
        'id': 'chat-forge-account-panel-20261029', 'date': '2026-10-29',
        'title': 'Your Chat and account projects in §e',
        'changes': [
            'Open your full §wyrlz Chat in the §e side panel, with the same Google account history and saved settings.',
            'Sign in through the Chat account window, then use Save to account and My projects to save or load complete native §e projects.',
            'Ask Chat to inspect the active workspace or make supported mesh and scene edits. Close the panel to pause editor access.',
            'Editor actions use actual native results and Undo/Redo. Unsupported or unfinished actions are reported without claiming success.',
            'Saved communication and companion preferences now guide your conversations in both Chat surfaces.',
        ],
    }
    records.insert(0, {**latest, 'kind': 'Source update',
                       'source': {'commit': 'e4dee084f57788c3c6edc16381203d34ebc0c7e1',
                                  'path': 'docs/engineering/entries/2026-10-29_CHAT_FORGE_INTEGRATION.md'}})
    latest = {
        'id': 'chat-forge-project-workflow-20261030', 'date': '2026-10-30',
        'title': 'Create and continue projects with Chat in §e',
        'changes': [
            'Ask Chat inside §e to create a named project from a blank workspace or an available starter.',
            '§e opens a separate editable copy and keeps the bundled starter intact. Watch the active project change as it is created.',
            'Chat can inspect the project and level currently open, list available starters, and use fresh context for your next requested edits.',
            'Local project snapshots and recovery stay on this device. Save to account remains an explicit action for Google account storage.',
            'Close the Chat panel to pause editor access. Project creation requires an updated §e editor and a connected Chat account.',
        ],
    }
    return {'schema': 'swrlz-chat-updates-v1', 'latest': latest, 'history': records,
            'historyCoverage': {'registryRef': REGISTRY_REF, 'registryCommit': head,
                                'registryRecords': sum(r['kind'] == 'Version registry record' for r in records),
                                'oldestRecordedDate': min(r['date'] for r in records),
                                'description': 'All recorded Chat version-registry changes, earlier Chat changelog entries, and the preceding coding update. Historical records may include failed attempts or repeated versions.'}}

if __name__ == '__main__':
    data = build()
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'Wrote {len(data["history"])} previous recorded updates to {TARGET.relative_to(ROOT)}')
