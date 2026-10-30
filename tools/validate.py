#!/usr/bin/env python3
"""Validate the editable catalogs against the pinned English snapshot."""
import json
import re
from catalog import *

def validate():
    state = lock()
    BUILD.mkdir(exist_ok=True)
    expected, inventory = {}, []
    for filename in state['files']:
        source_data = (SNAPSHOT / filename).read_bytes()
        assert sha256(source_data) == state['upstream_file_sha256'][filename], ('snapshot hash', filename)
        data = (ROOT / filename).read_bytes()
        assert b'\r' not in data and not data.startswith(b'\xef\xbb\xbf'), ('UTF-8/LF', filename)
        text = data.decode('utf-8')
        assert not re.search(r'^; TODO', text, re.M), ('Unreviewed upstream changes', filename)
        source = [r for r in parse(source_data.decode('utf-8'), True) if r['type'] != 'raw']
        target = [r for r in parse(text) if r['type'] != 'raw']
        assert [identity(r) for r in source] == [identity(r) for r in target], ('keys/tags/order', filename)
        expected[filename] = {}
        for original, translated in zip(source, target):
            value = translated['value']
            assert value.strip(), ('empty translation', filename, translated['key'])
            original_value = original['value'] or original['key']
            assert tokens(original_value) == tokens(value), ('protected tokens', filename, translated['key'])
            for span in prose(value):
                assert not re.search(r'[“”]|（[\x20-\x7e]+）|网络电话|\b(?:VOIP|Voip)\b', span), ('typography/VoIP', filename, translated['key'])
                assert not re.search(r'\S\([\x20-\x7e]*?\)', span), ('space before bracket', filename, translated['key'])
                assert not re.search(r'\([\x20-\x7e]*?\)[^\x20\t\n，。、；：！？）」』】》〉*_]', span), ('space after bracket', filename, translated['key'])
            expected[filename][runtime_key(translated)] = value
        inventory.append({'file': filename, 'entries': sum(r['type']=='entry' for r in target),
                          'blocks': sum(r['type']=='block' for r in target), 'sha256': sha256(data)})
    basenames = [Path(name).name.lower() for name in state['files']]
    assert len(basenames) == len(set(basenames)), 'Language installer flattens filenames'
    assert (ROOT / 'LICENSE.txt').read_bytes() == (SNAPSHOT / 'LICENSE.txt').read_bytes(), 'Upstream license must be retained'
    report = {'status': 'PASS', 'english_commit': state['english_commit'], 'files': inventory,
              'language_files': len(inventory), 'single_line_occurrences': sum(r['entries'] for r in inventory),
              'multiline_blocks': sum(r['blocks'] for r in inventory),
              'runtime_keys': sum(len(values) for values in expected.values()), 'live_Unraid_tested': False}
    (BUILD / 'expected.json').write_text(json.dumps(expected, ensure_ascii=False, indent=2)+'\n')
    (BUILD / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"PASS: {report['language_files']} files; {report['single_line_occurrences']} entries; {report['multiline_blocks']} blocks")
    return report

if __name__ == '__main__': validate()
