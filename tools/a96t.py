import os, json, subprocess, urllib.request, shutil
REPO = os.environ.get('REPO', 'assets-3d-lowpoly-2')
AGA = 'https://github.com/AgenticGameDevs/generated-assets'
AGAB = 'https://raw.githubusercontent.com/AgenticGameDevs/generated-assets/main/'
CATPACKS = 'https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/tools/a96-packs.json'


def gb(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'a96'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def sh(*a):
    return subprocess.run(list(a), check=True)


def commit(msg):
    sh('git', 'config', 'user.name', 'sigco3111')
    sh('git', 'config', 'user.email', 'sigco3111@users.noreply.github.com')
    sh('git', 'add', '-A')
    if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode == 0:
        print('no changes:', msg)
        return
    sh('git', 'commit', '-m', msg)
    sh('git', 'push')


PACKS = json.loads(gb(CATPACKS).decode('utf-8'))
cat = json.loads(gb(AGAB + 'catalog.json').decode('utf-8'))
for p in PACKS:
    if p['repo'] != REPO or p['mode'] == 'audio':
        continue
    assets = [a for a in cat if a['collection'] == p['collection'] and a['category'] == p['category']]
    cand = [a for a in assets if a.get('preview')]
    print('cand', len(cand), cand[0]['preview'] if cand else '')
    if not cand:
        continue
    try:
        b = gb(AGAB + cand[0]['preview'])
        print('bytes', len(b))
        open('/tmp/p.png', 'wb').write(b)
        out = p['slug'] + '/preview.jpg'
        done = False
        for tool in ('convert', 'magick'):
            for q in ('82', '70', '60'):
                try:
                    sh(tool, '/tmp/p.png', '-resize', '480x480>', '-background', 'white', '-alpha', 'remove', '-alpha', 'off', '-strip', '-quality', q, out)
                    print('ok', tool, q, os.path.getsize(out))
                    done = True
                    break
                except Exception as e:
                    print('fail', tool, q, repr(e))
            if done:
                break
        os.makedirs('previews', exist_ok=True)
        shutil.copy(out, 'previews/' + p['slug'] + '.jpg')
        commit('썸네일: ' + p['name'] + ' 추가')
    except Exception as e:
        print('ERR', p['name'], repr(e))
