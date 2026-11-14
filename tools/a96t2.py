import os, json, subprocess, urllib.request, shutil, traceback
REPO = os.environ.get('REPO', 'assets-3d-lowpoly-2')
AGAB = 'https://raw.githubusercontent.com/AgenticGameDevs/generated-assets/main/'
CATPACKS = 'https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/tools/a96-packs.json'
log = []


def gb(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'a96'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def main():
    log.append('cwd ' + os.getcwd())
    log.append('gitignore ' + str(os.path.exists('.gitignore')))
    packs = json.loads(gb(CATPACKS).decode('utf-8'))
    cat = json.loads(gb(AGAB + 'catalog.json').decode('utf-8'))
    for p in packs:
        if p['repo'] != REPO or p['mode'] == 'audio':
            log.append('skip ' + p['name'])
            continue
        assets = [a for a in cat if a['collection'] == p['collection'] and a['category'] == p['category']]
        cand = [a for a in assets if a.get('preview')]
        log.append(p['name'] + ' assets=' + str(len(assets)) + ' cand=' + str(len(cand)))
        if not cand:
            continue
        try:
            u = AGAB + cand[0]['preview']
            log.append('url ' + u)
            b = gb(u)
            log.append('bytes ' + str(len(b)))
            open('/tmp/p.png', 'wb').write(b)
            out = p['slug'] + '/preview.jpg'
            rc, o = run(['convert', '/tmp/p.png', '-resize', '480x480>', '-background', 'white', '-alpha', 'remove', '-alpha', 'off', '-strip', '-quality', '82', out])
            log.append('convert rc=' + str(rc) + ' ' + o[:200])
            log.append('out ' + str(os.path.exists(out)) + ' ' + str(os.path.getsize(out) if os.path.exists(out) else 0))
            os.makedirs('previews', exist_ok=True)
            shutil.copy(out, 'previews/' + p['slug'] + '.jpg')
            log.append('copied ' + str(os.path.exists('previews/' + p['slug'] + '.jpg')))
            for cmd in (['git', 'config', 'user.name', 'sigco3111'], ['git', 'config', 'user.email', 'sigco3111@users.noreply.github.com'], ['git', 'add', '-A'], ['git', 'commit', '-m', '썸네일: ' + p['name'] + ' 추가'], ['git', 'push']):
                rc, o = run(cmd)
                log.append('git ' + cmd[1] + ' rc=' + str(rc) + ' ' + o[:300])
        except Exception:
            log.append('ERR ' + p['name'] + ' ' + traceback.format_exc())


main()
open('thumb-log.txt', 'w', encoding='utf-8').write(chr(10).join(log) + chr(10))
subprocess.run(['git', 'config', 'user.name', 'sigco3111'])
subprocess.run(['git', 'config', 'user.email', 'sigco3111@users.noreply.github.com'])
subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit', '-m', 'A96: 썸네일 진단 로그'])
subprocess.run(['git', 'push'])
print(chr(10).join(log))
