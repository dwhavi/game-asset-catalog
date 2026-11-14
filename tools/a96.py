import os, csv, io, json, zipfile, hashlib, subprocess, shutil, urllib.request, urllib.parse
from collections import Counter

MODE = os.environ.get('MODE', 'probe')
REPO = os.environ.get('REPO', '')
DATE = '2026-11-15'
NL = chr(10)
AGA = 'https://github.com/AgenticGameDevs/generated-assets'
AGAB = 'https://raw.githubusercontent.com/AgenticGameDevs/generated-assets/main/'
CATPACKS = 'https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/tools/a96-packs.json'
CATCSV = 'https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv'
RAWB = 'https://raw.githubusercontent.com/sigco3111/%s/main/'
LIC = 'CC BY 4.0'
LICURL = 'https://creativecommons.org/licenses/by/4.0/'
LIMIT = 5242880
MAXFILE = 26214400


def gb(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'a96'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def gt(url):
    return gb(url).decode('utf-8')


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


def rows():
    return list(csv.reader(io.StringIO(gt(CATCSV))))


def names_urls():
    rws = rows()
    names = set()
    urls = set()
    for r in rws[1:]:
        if r:
            names.add((r[0] or '').strip().lower())
            urls.add((r[6] or '').strip().lower().rstrip('/'))
    return names, urls


def mb(n):
    return '%.1fMB' % (n / 1048576.0)


def packs():
    return json.loads(gt(CATPACKS))


def probe():
    cat = json.loads(gt(AGAB + 'catalog.json'))
    rws = rows()
    L = []
    L.append('header: ' + json.dumps(rws[0], ensure_ascii=False))
    L.append('rows: ' + str(len(rws) - 1))
    cnt = 0
    for r in rws[1:]:
        if r and AGA.lower() in (r[6] or '').lower():
            L.append('AGA row: ' + json.dumps(r, ensure_ascii=False))
            cnt += 1
    L.append('AGA count: ' + str(cnt))
    for r in rws[1:]:
        if r and len(r) > 10 and '릴리스' in r[10]:
            L.append('release row: ' + json.dumps(r, ensure_ascii=False))
            break
    for repo in ['assets-3d-lowpoly-2', 'assets-2d-pixel', 'assets-audio']:
        try:
            d = json.loads(gt('https://api.github.com/repos/sigco3111/' + repo))
            L.append('repo ' + repo + ' sizeKB=' + str(d.get('size')))
        except Exception as e:
            L.append('repo ' + repo + ' size unknown ' + str(e))
    groups = {}
    for a in cat:
        groups.setdefault(a['collection'] + ' | ' + a['category'], []).append(a)
    for k in sorted(groups):
        v = groups[k]
        tot = 0
        for a in v:
            tot += int(a.get('bytes') or 0)
        L.append('')
        L.append('### ' + k + ' n=' + str(len(v)) + ' kind=' + str(v[0].get('kind')) + ' bytes=' + str(tot))
        for a in v:
            L.append('  - ' + a['name'] + ' | ' + a['file'] + ' | ' + str(a.get('bytes')) + ' | ' + str(((a.get('source') or {}).get('generator')) or '') + ' | ' + str(a.get('license')) + ' | prev=' + str(bool(a.get('preview'))))
    open('a96-res.txt', 'w', encoding='utf-8').write(NL.join(L) + NL)
    commit('A96: 조사 결과')
    print(NL.join(L))


def build(p):
    names, urls = names_urls()
    if p['repo'] != REPO:
        print('SKIP other repo', p['name'])
        return False
    if p['name'].strip().lower() in names:
        print('SKIP duplicate', p['name'])
        return False
    cat = json.loads(gt(AGAB + 'catalog.json'))
    assets = [a for a in cat if a['collection'] == p['collection'] and a['category'] == p['category']]
    if not assets:
        print('no assets', p['name'])
        return False
    slug = p['slug']
    shutil.rmtree(slug, ignore_errors=True)
    os.makedirs(slug)
    tmp = '/tmp/a96files'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    files = []
    for a in assets:
        b = gb(AGAB + urllib.parse.quote(a['file'], safe='/'))
        h = hashlib.sha256(b).hexdigest()
        if a.get('sha256') and h != a['sha256']:
            print('checksum mismatch', a['id'])
            return False
        nm = os.path.basename(a['file'])
        open(os.path.join(tmp, nm), 'wb').write(b)
        files.append((a, nm, len(b)))
    total = 0
    for f in files:
        total += f[2]
    creators = sorted({str((a.get('creator') or {}).get('name') or '') for a, _, _ in files} - {''})
    gens = sorted({str((a.get('source') or {}).get('generator') or '') for a, _, _ in files} - {''})
    sub = 'models/'
    if p['mode'] == 'audio':
        sub = 'sfx/'
    elif p['mode'] == '2d':
        sub = 'sprites/'
    zipname = slug + '.zip'
    zpath = os.path.join(slug, zipname)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for a, nm, sz in files:
            z.write(os.path.join(tmp, nm), sub + nm)
    zsize = os.path.getsize(zpath)
    if zsize > MAXFILE:
        print('TOO BIG', p['name'], mb(zsize))
        shutil.rmtree(slug, ignore_errors=True)
        return False
    rel = '저장소 내 포함'
    if zsize > LIMIT:
        rel = '릴리스 첨부'
    L = []
    L.append('# ' + p['name'])
    L.append('')
    L.append('- 출처: ' + AGA + ' (' + p['collection'] + ' / ' + p['category'] + ')')
    L.append('- 원본 컬렉션: ' + p['collection'] + ' (AI 생성·AI 보조 에셋 라이브러리)')
    L.append('- 라이선스: ' + LIC + ' (' + LICURL + ') — 단일 표기')
    L.append('- 제작자: ' + ', '.join(creators))
    L.append('- 파일 수: ' + str(len(files)) + '개 (' + mb(total) + ')')
    L.append('- 파일: ' + zipname + ' (' + mb(zsize) + ') — ' + rel)
    L.append('- AI 생성: 예 — 출처 저장소가 AI 생성·AI 보조 작업물임을 명시')
    L.append('- 생성 도구: ' + ', '.join(gens))
    L.append('- 표기 요구: 저작자 표기, 라이선스 링크, 변경 여부 명시(CC BY 4.0). 원본 파일 바이트를 그대로 보관하고(zip 재압축만) 내용은 바꾸지 않음')
    L.append('- 수집일: ' + DATE)
    L.append('- 태그: ' + p['tags'])
    L.append('')
    L.append('## 구성 파일')
    L.append('')
    L.append('| 에셋 | 파일 | 생성 도구 | 바이트 |')
    L.append('| --- | --- | --- | --- |')
    for a, nm, sz in files:
        L.append('| ' + str(a['name']).replace('|', '/') + ' | ' + nm + ' | ' + str(((a.get('source') or {}).get('generator')) or '') + ' | ' + str(sz) + ' |')
    L.append('')
    L.append('## 에셋별 표기')
    L.append('')
    for a, nm, sz in files:
        L.append('- ' + str(a['name']) + ': ' + str(a.get('attribution') or ''))
    open(os.path.join(slug, 'pack.md'), 'w', encoding='utf-8').write(NL.join(L) + NL)
    S = [p['name'], '']
    S.append('출처 URL: ' + AGA)
    S.append('원본 경로: assets/' + p['collection'] + '/')
    S.append('표기 라이선스: ' + LIC)
    S.append('라이선스 원문: ' + LICURL)
    S.append('제작자: ' + ', '.join(creators))
    S.append('AI 생성: 예 (생성 도구: ' + ', '.join(gens) + ')')
    S.append('')
    S.append('이 파일은 수집자가 출처의 라이선스 표기를 기록한 것입니다.')
    S.append('원본 배포물에 라이선스 파일이 포함되어 있지 않기 때문에 이 파일이 그 역할을 합니다.')
    S.append('재배포·사용 시 저작자 표기, 라이선스 링크, 변경 여부를 함께 밝혀 주세요.')
    open(os.path.join(slug, 'LICENSE-SOURCE.txt'), 'w', encoding='utf-8').write(NL.join(S) + NL)
    C = [p['name'], '', 'CC BY 4.0 - 사용 시 아래 표기를 남겨 주세요.', '']
    for a, nm, sz in files:
        C.append(str(a['name']))
        C.append('  ' + str(a.get('attribution') or ''))
        C.append('')
    open(os.path.join(slug, 'CREDITS.txt'), 'w', encoding='utf-8').write(NL.join(C) + NL)
    prev = ''
    if p['mode'] in ('3d', '2d'):
        cand = [a for a in assets if a.get('preview')]
        if cand:
            src = '/tmp/a96prev.png'
            try:
                open(src, 'wb').write(gb(AGAB + cand[0]['preview']))
                out = os.path.join(slug, 'preview.jpg')
                for q, w in ((82, 480), (72, 440), (65, 400), (60, 360)):
                    sh('convert', src, '-resize', '%dx%d>' % (w, w), '-background', 'white', '-alpha', 'remove', '-alpha', 'off', '-strip', '-quality', str(q), out)
                    if os.path.getsize(out) <= 204800:
                        break
                os.makedirs('previews', exist_ok=True)
                shutil.copy(out, os.path.join('previews', slug + '.jpg'))
                prev = slug + '.jpg'
            except Exception as e:
                print('preview failed', str(e))
    if zsize > LIMIT:
        tag = 'a96-' + slug
        note = 'A96 에셋 팩: ' + p['name'] + ' (' + LIC + ')'
        sh('gh', 'release', 'create', tag, '--title', p['name'], '--notes', note, zpath)
        os.remove(zpath)
    commit('에셋: ' + p['name'] + ' 추가')
    if prev:
        commit('썸네일: ' + p['name'] + ' 추가')
    print('BUILT', p['name'], mb(zsize), len(files), rel)
    return True


def catalog():
    rws = rows()
    hdr = rws[0]
    data = [r for r in rws[1:] if r]
    names = {(r[0] or '').strip().lower() for r in data}
    ac = Counter(r[3] for r in data if r[1] == 'assets-audio')
    atype = ac.most_common(1)[0][0] if ac else '효과음'
    pc = Counter(r[3] for r in data if r[1] == 'assets-2d-pixel')
    ptype = pc.most_common(1)[0][0] if pc else '2D 이펙트'
    new = []
    for p in packs():
        if p['name'].strip().lower() in names:
            print('DUP', p['name'])
            continue
        md = gt(RAWB % p['repo'] + p['slug'] + '/pack.md')
        gen = ''
        cre = ''
        nf = ''
        rel = '저장소 포함'
        for ln in md.splitlines():
            if ln.startswith('- 생성 도구:'):
                gen = ln.split(':', 1)[1].strip()
            elif ln.startswith('- 제작자:'):
                cre = ln.split(':', 1)[1].strip()
            elif ln.startswith('- 파일 수:'):
                nf = ln.split(':', 1)[1].strip()
            elif ln.startswith('- 파일:') and '릴리스 첨부' in ln:
                rel = '릴리스 첨부'
        prev = ''
        if rel == '릴리스 첨부':
            fpath = 'releases/download/a96-' + p['slug'] + '/' + p['slug'] + '.zip'
        else:
            fpath = p['slug'] + '/' + p['slug'] + '.zip'
        if p['mode'] in ('3d', '2d'):
            prev = RAWB % p['repo'] + 'previews/' + p['slug'] + '.jpg'
        kind = '3D 팩'
        typ = p['type']
        if p['mode'] == 'audio':
            kind = '효과음 팩'
            typ = atype
        elif p['mode'] == '2d':
            kind = '2D 이펙트 팩'
            typ = ptype
        notes = kind + '; AI 생성(AgenticGameDevs/generated-assets; 생성 도구 ' + gen + '); 라이선스 CC BY 4.0 표기 파일(pack.md·CREDITS.txt·LICENSE-SOURCE.txt) 포함; 파일 ' + nf + '; ' + rel + ('; 썸네일 480px 이하 JPEG' if prev else '')
        new.append([p['name'], p['repo'], fpath, typ, p['tags'], cre, AGA, 'CC-BY', 'required: ' + cre + ' (CC BY 4.0)', DATE, notes, prev, '', ''])
        names.add(p['name'].strip().lower())
    if not new:
        print('nothing to add')
        return
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=NL)
    w.writerow(hdr)
    for r in data:
        w.writerow(r)
    for r in new:
        w.writerow(r)
    open('catalog.csv', 'w', encoding='utf-8').write(buf.getvalue())
    total = len(data) + len(new)
    n3 = 0
    n2 = 0
    na = 0
    for r in new:
        if r[1] == 'assets-3d-lowpoly-2':
            n3 += 1
        elif r[1] == 'assets-2d-pixel':
            n2 += 1
        else:
            na += 1
    rl = open('README.md', encoding='utf-8').read()
    sec = []
    sec.append('## 2026-11-15 A96 추가 (' + str(len(new)) + '팩, 총 ' + str(total) + '팩)')
    sec.append('')
    sec.append('A96 라운드: GitHub의 AgenticGameDevs/generated-assets(AI 생성 에셋 라이브러리; 미디어 CC BY 4.0·CC0, 코드 MIT)에서 아직 카탈로그에 없는 3D 모델 팩과 효과음 팩을 모았습니다. 후보는 러너 안에서 전체 catalog.csv(csv.reader, name+source URL)와 대조해 걸러냈고, 팩마다 원본 파일 바이트와 sha256을 확인했습니다.')
    sec.append('')
    sec.append('| 팩 | 라이선스 |')
    sec.append('| --- | --- |')
    for r in new:
        sec.append('| ' + r[0] + ' | CC BY 4.0 |')
    sec.append('')
    th = []
    for r in new:
        th.append(r[0] + '=' + ('있음' if r[11] else '해당 없음(오디오)'))
    kinds = []
    if n3:
        kinds.append('3D ' + str(n3) + '팩')
    if n2:
        kinds.append('2D 이펙트 ' + str(n2) + '팩')
    if na:
        kinds.append('효과음 ' + str(na) + '팩')
    sec.append('종류: ' + ', '.join(kinds) + '. AI 생성 표기는 각 팩 pack.md에 있고, 생성 도구와 출처 조건도 함께 적었습니다. 썸네일: ' + ', '.join(th) + '. 색인은 rebuild-index.yml 수동 실행으로 갱신합니다.')
    sec.append('')
    marker = '## 2026-11-14 A95 추가'
    if marker in rl:
        rl = rl.replace(marker, NL.join(sec) + NL + marker, 1)
    else:
        rl = rl + NL + NL.join(sec)
    open('README.md', 'w', encoding='utf-8').write(rl)
    logline = '- ' + DATE + ' A96: ' + ', '.join(r[0] for r in new) + ' (' + str(len(new)) + '팩, 총 ' + str(total) + '팩; 3D ' + str(n3) + '팩은 assets-3d-lowpoly-2, 2D 이펙트 ' + str(n2) + '팩은 assets-2d-pixel, 효과음 ' + str(na) + '팩은 assets-audio; 출처 AgenticGameDevs/generated-assets, AI 생성 표기·생성 도구·CC BY 4.0 조건 기록; 이름·출처 URL 전체 catalog.csv 대조로 중복 제거).'
    lg = open('docs/log.md', encoding='utf-8').read()
    open('docs/log.md', 'w', encoding='utf-8').write(lg.rstrip(NL) + NL + NL + logline + NL)
    commit('카탈로그: A96 ' + str(len(new)) + '팩 추가')
    print('CATALOG ADDED', len(new), 'TOTAL', total)


def cleanup():
    for f in ['tools/a96.py', 'tools/a96-packs.json', 'a96-res.txt', '.github/workflows/a96-cat.yml']:
        if os.path.exists(f):
            sh('git', 'rm', '-q', f)
    commit('정리: A96 임시 파일 삭제')
    print('cleanup done')


if MODE == 'probe':
    probe()
elif MODE == 'build':
    for p in packs():
        build(p)
elif MODE == 'catalog':
    catalog()
elif MODE == 'cleanup':
    cleanup()
else:
    print('unknown mode', MODE)
