import os, json, subprocess, urllib.request, traceback
AGAB = 'https://raw.githubusercontent.com/AgenticGameDevs/generated-assets/main/'
CATPACKS = 'https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/tools/a96-packs.json'


def gb(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'a96'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


log = []
PACKS = json.loads(gb(CATPACKS).decode('utf-8'))
cat = json.loads(gb(AGAB + 'catalog.json').decode('utf-8'))
for p in PACKS:
    if p['mode'] == 'audio':
        continue
    assets = [a for a in cat if a['collection'] == p['collection'] and a['category'] == p['category']]
    cand = [a for a in assets if a.get('preview')]
    log.append(p['name'] + ' cand=' + str(len(cand)))
    if not cand:
        continue
    u = AGAB + cand[0]['preview']
    log.append('preview field: ' + str(cand[0]['preview']))
    log.append('url: ' + u)
    try:
        b = gb(u)
        log.append('bytes ' + str(len(b)))
        open('/tmp/p.png', 'wb').write(b)
    except Exception:
        log.append('gb fail: ' + traceback.format_exc())
        continue
    for tool in ('convert', 'magick'):
        r = subprocess.run([tool, '-version'], capture_output=True, text=True)
        log.append(tool + ' rc=' + str(r.returncode) + ' ' + (r.stdout or r.stderr)[:100].replace(chr(10), ' '))
    r = subprocess.run(['convert', '/tmp/p.png', '-resize', '480x480>', '/tmp/o.jpg'], capture_output=True, text=True)
    log.append('convert rc=' + str(r.returncode) + ' err=' + r.stderr[:300].replace(chr(10), ' '))
    log.append('out ' + str(os.path.exists('/tmp/o.jpg')) + ' size ' + str(os.path.getsize('/tmp/o.jpg') if os.path.exists('/tmp/o.jpg') else 0))
open('thumb-log.txt', 'w', encoding='utf-8').write(chr(10).join(log) + chr(10))
subprocess.run(['git', 'config', 'user.name', 'sigco3111'])
subprocess.run(['git', 'config', 'user.email', 'sigco3111@users.noreply.github.com'])
subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit', '-m', 'A96: 썸네일 진단'])
subprocess.run(['git', 'push'])
print(chr(10).join(log))
