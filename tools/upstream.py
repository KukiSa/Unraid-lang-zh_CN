#!/usr/bin/env python3
"""Report upstream changes; explicitly apply by stable English key and help tag."""
import argparse
import json
import subprocess
from catalog import *

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,timeout=60)

def upstream_files(commit):
    names=git('ls-tree','-r','--name-only',commit).decode().splitlines()
    return {name:git('show',commit+':'+name) for name in names if name.endswith('.txt') and Path(name).name!='LICENSE.txt'}

def compare(old,new):
    def indexed(data):
        return {identity(row):(row['value'] or row.get('key','')) for row in parse(data.decode(),True) if row['type']!='raw'}
    result=[]
    for name in sorted(set(old)|set(new)):
        a=indexed(old[name]) if name in old else {}
        b=indexed(new[name]) if name in new else {}
        for key in sorted(set(a)|set(b)):
            if key not in a: change='added'
            elif key not in b: change='removed'
            elif a[key]!=b[key]: change='changed'
            else: continue
            result.append({'file':name,'type':key[0],'key':key[1],'change':change})
    return result

def merge(old_source,new_source,translation):
    old={identity(row):row for row in parse(old_source.decode(),True) if row['type']!='raw'}
    translated={identity(row):row for row in parse(translation.decode()) if row['type']!='raw'}
    rows=[]
    for row in parse(new_source.decode(),True):
        if row['type']=='raw': rows.append(row); continue
        key=identity(row); previous=old.get(key); target=translated.get(key)
        if previous is not None and target is not None:
            if (previous['value'] or previous['key'])!=(row['value'] or row['key']):
                rows.append({'type':'raw','value':'; TODO review changed English source: '+row['key']})
            rows.append({**row,'value':target['value']})
        else:
            rows.append({'type':'raw','value':'; TODO translate new English source: '+row['key']})
            rows.append({**row,'value':''})
    return render(rows)

def run(apply=False):
    state=lock()
    if apply and git('status','--porcelain').strip():
        raise SystemExit('Commit or stash current changes before applying an upstream update.')
    subprocess.run(['git','fetch','--no-tags',state['english_repository']+'.git','master'],cwd=ROOT,check=True,timeout=60)
    latest=git('rev-parse','FETCH_HEAD').decode().strip()
    old={name:(SNAPSHOT/name).read_bytes() for name in state['files']}
    new=upstream_files(latest)
    changes=compare(old,new)
    BUILD.mkdir(exist_ok=True)
    result={'previous':state['english_commit'],'latest':latest,'changes':changes}
    (BUILD/'upstream-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# English upstream check','',f"Pinned: `{state['english_commit']}`",f'Latest: `{latest}`','',f'Changed translation units: {len(changes)}','']
    lines += [f"- {item['change']}: `{item['file']}` / `{item['key'].replace('`','')}`" for item in changes]
    (BUILD/'upstream-report.md').write_text('\n'.join(lines)+'\n')
    print(f'English source {latest}: {len(changes)} changed translation units.')
    if apply:
        for name,data in new.items():
            target=ROOT/name
            text=merge(old.get(name,b''),data,target.read_bytes() if target.exists() else b'')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
            snap=SNAPSHOT/name;snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(data)
        for name in set(old)-set(new):
            (ROOT/name).unlink();(SNAPSHOT/name).unlink()
        for name in ['LICENSE.txt','README.md']:
            (SNAPSHOT/name).write_bytes(git('show',latest+':'+name))
        # Never silently accept an upstream license change.
        assert (SNAPSHOT/'LICENSE.txt').read_bytes()==(ROOT/'LICENSE.txt').read_bytes(), 'Upstream license changed: review required'
        state['english_commit']=latest;state['files']=sorted(new)
        state['upstream_file_sha256']={name:sha256(data) for name,data in new.items()}
        state['snapshot_date']=git('show','-s','--format=%cs',latest).decode().strip()
        (ROOT/'source.lock.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    return bool(changes)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    changed=run(args.apply)
    raise SystemExit(0 if args.apply or not changed else 2)
