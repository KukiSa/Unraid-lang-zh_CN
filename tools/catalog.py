"""Unraid language catalogs: stable English keys and help tags, no numeric IDs."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'upstream/en_US'
BUILD = ROOT / 'build'
DIST = ROOT / 'dist'
REPOSITORY = 'KukiSa/Unraid-lang-zh_CN'
RESERVED = {'null', 'yes', 'no', 'true', 'false', 'on', 'off', 'none'}
PROTECTED = re.compile(r'<\?.*?\?>|`[^`\n]*`|<[^>\n]+>|_\([^\n]*?\)_|\b[A-Za-z_][A-Za-z0-9_,.]*\([^\s()]*\)|\]\([^\n)]*\)|https?://[^\s<>「」]+|\x27[^\x27\n]*\x27', re.S)

def lock():
    return json.loads((ROOT / 'source.lock.json').read_text())

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def normalize_key(text):
    return re.sub(r'  +', ' ', re.sub(r'&amp;|[?{}|&~!\[\]()/\\:*^."\x27]|<.+?/?>', '', text))

def parse(text, english=False):
    rows, active, body = [], None, []
    for line in text.splitlines():
        if line.startswith(':'):
            if line == ':end':
                if active is None: raise ValueError('Orphan :end')
                rows.append({'type': 'block', 'key': active, 'value': '\n'.join(body).rstrip()})
                active, body = None, []
            else:
                if active is not None or not re.fullmatch(r':[A-Za-z0-9_]+:', line):
                    raise ValueError('Invalid block tag: ' + line)
                active = line
        elif active is not None:
            body.append(line)
        elif '=' in line and not line.startswith(';'):
            key, value = line.split('=', 1)
            rows.append({'type': 'entry', 'key': key, 'value': value})
        elif english and line.startswith('Note that this module reviews all of your previously installed Docker Containers'):
            rows.append({'type': 'entry', 'key': normalize_key(line), 'value': line})
        elif line.strip() and not line.startswith(';'):
            raise ValueError('Unrecognized catalog line: ' + line)
        else:
            rows.append({'type': 'raw', 'value': line})
    if active is not None: raise ValueError('Unterminated block: ' + active)
    return rows

def render(rows):
    lines = []
    for row in rows:
        if row['type'] == 'entry': lines.append(row['key'] + '=' + row['value'])
        elif row['type'] == 'block': lines.extend([row['key'], row['value'], ':end'])
        else: lines.append(row['value'])
    return '\n'.join(lines) + '\n'

def identity(row):
    return row['type'], row.get('key')

def prose(text):
    position = 0
    for match in PROTECTED.finditer(text):
        yield text[position:match.start()]
        position = match.end()
    yield text[position:]

def tokens(text):
    patterns = {
        'printf': r'%(?:\d+\$)?[+-]?(?:\d+)?(?:\.\d+)?[bcdeEfFgGosuxXdi]|%%',
        'PHP': r'<\?.*?\?>', 'HTML': r'<[^>\n]+>', 'code': r'`[^`\n]*`',
        'link': r'\]\([^\n)]*\)', 'inline_translation': r'_\([^\n]*?\)_',
    }
    return {name: Counter(re.findall(pattern, text, re.S)) for name, pattern in patterns.items()}

def runtime_key(row):
    if row['type'] == 'block': return '_' + row['key'][1:-1]
    key = row['key'].strip()
    return key + '.' if key.lower() in RESERVED else key
