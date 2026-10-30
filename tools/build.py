#!/usr/bin/env python3
"""Build deterministic ZIP and online/offline release artifacts from the catalogs."""
import argparse
import datetime
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from catalog import *
from validate import validate

def metadata(version):
    base = f'https://github.com/{REPOSITORY}/releases'
    root = ET.Element('Language')
    fields = {
        'LanguageURL': f'{base}/download/v{version}/zh_CN.zip',
        'Language': 'Chinese', 'LanguageLocal': '简体中文 · 独立译本', 'LanguagePack': 'zh_CN',
        'Author': 'gpt-6.1-sol; iks', 'Name': 'Unraid Simplified Chinese - Independent Translation',
        'TemplateURL': f'{base}/latest/download/lang-zh_CN.xml', 'Version': version,
        'Icon': 'icon-language', 'Description': '从官方英文源独立翻译，含完整帮助及插件文案。',
        'Changes': '独立翻译；专业术语中英对照；中文引号及括注排版；VoIP 保留原文。',
    }
    for key, value in fields.items(): ET.SubElement(root,key).text = value
    ET.indent(root, space='  ')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root,encoding='unicode')+'\n'

def version_value():
    version = (ROOT / 'VERSION').read_text().strip()
    assert re.fullmatch(r'20\d{2}\.\d{2}\.\d{2}\.\d{2}',version), 'Version format: YYYY.MM.DD.NN'
    datetime.date.fromisoformat(version[:10].replace('.','-'))
    return version

def archive(path, entries, stamp):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for name,data in sorted(entries.items()):
            item=zipfile.ZipInfo(name,stamp)
            item.compress_type=zipfile.ZIP_DEFLATED
            item.external_attr=(0o100755 if name.endswith('.sh') else 0o100644)<<16
            output.writestr(item,data)

def checksums(entries):
    return ''.join(f'{sha256(data)}  {name}\n' for name,data in sorted(entries.items())).encode()

def build(write_metadata=False):
    report=validate(); version=version_value(); xml=metadata(version)
    if write_metadata: (ROOT/'lang-zh_CN.xml').write_text(xml)
    assert (ROOT/'lang-zh_CN.xml').read_text()==xml, 'Run python3 tools/build.py --write-metadata after changing VERSION'
    DIST.mkdir(exist_ok=True)
    stamp=tuple(map(int,version.split('.')[:3]))+(0,0,0)
    state=lock()
    texts={Path(name).name:(ROOT/name).read_bytes() for name in state['files']}
    texts['LICENSE.txt']=(ROOT/'LICENSE.txt').read_bytes()
    archive(DIST/'zh_CN.zip',texts,stamp)
    (DIST/'lang-zh_CN.xml').write_text(xml)
    shutil.copyfile(BUILD/'validation.json',DIST/'validation.json')
    payload={name:(ROOT/name).read_bytes() for name in ['install-offline.sh','restore-language.sh','LICENSE.txt']}
    payload.update({'zh_CN.zip':(DIST/'zh_CN.zip').read_bytes(),'lang-zh_CN.xml':xml.encode(),
                    'README.md':(ROOT/'README.md').read_bytes(),'validation.json':(BUILD/'validation.json').read_bytes()})
    payload['SHA256SUMS']=checksums(payload)
    offline=f'unraid-zh_CN-offline-{version}.zip'
    archive(DIST/offline,payload,stamp)
    names=['zh_CN.zip','lang-zh_CN.xml','validation.json',offline]
    (DIST/'SHA256SUMS').write_bytes(checksums({name:(DIST/name).read_bytes() for name in names}))
    print(f'Built v{version}: zh_CN.zip, online XML, offline bundle and SHA256SUMS')
    return report

if __name__=='__main__':
    arguments=argparse.ArgumentParser()
    arguments.add_argument('--write-metadata',action='store_true')
    build(arguments.parse_args().write_metadata)
