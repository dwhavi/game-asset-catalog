import os, re, sys, csv, io, json, time, zipfile, subprocess, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}
MODE = (sys.argv[1] if len(sys.argv) > 1 else "3d").strip()
CATALOG = "https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv"


def fetch(u, tries=3):
    err = None
    for _ in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read()
        except Exception as e:
            err = e
            time.sleep(3)
    raise err


cat = fetch(CATALOG).decode("utf-8")
rows = list(csv.reader(io.StringIO(cat)))
hdr = rows[0]
ni, ui = hdr.index("name"), hdr.index("source_url")
names = set(r[ni].strip().lower() for r in rows[1:] if r)
urls = set(r[ui].strip().lower() for r in rows[1:] if r)
print("catalog rows:", len(rows) - 1)

PACKS_3D = [
    {"name": "Retro Medieval Kit", "dir": "retro-medieval-kit",
     "url": "https://opengameart.org/content/retro-medieval-kit",
     "zipname": "kenney_retro-medieval-kit.zip", "author": "Kenney",
     "date": "2025-02-19", "tags": "medieval,lowpoly,3d,retro,kenney",
     "credit": "선택: Kenney.nl (kenney.nl)"},
    {"name": "Retro Urban Kit", "dir": "retro-urban-kit",
     "url": "https://opengameart.org/content/retro-urban-kit",
     "zipname": "kenney_retro-urban-kit.zip", "author": "Kenney",
     "date": "2021-03-20", "tags": "urban,city,lowpoly,3d,retro,kenney",
     "credit": "없음 (CC0)"},
    {"name": "Low Poly Camping Assets", "dir": "low-poly-camping-assets",
     "url": "https://opengameart.org/content/low-poly-camping-assets",
     "zipname": "low_poly_camping_assets.zip", "author": "Saraskau",
     "date": "2025-05-03", "tags": "camping,outdoor,lowpoly,3d,props",
     "credit": "없음 (CC0)"},
    {"name": "Lowpoly survival item pack", "dir": "lowpoly-survival-item-pack",
     "url": "https://opengameart.org/content/lowpoly-survival-item-pack",
     "zipname": "Survival items.zip", "author": "artie31",
     "date": "2020-03-13", "tags": "survival,items,lowpoly,3d,props",
     "credit": "선택: artie31"},
    {"name": "LOW POLY 3D MODEL PACKS", "dir": "low-poly-3d-model-packs",
     "url": "https://opengameart.org/content/low-poly-3d-model-packs",
     "zipname": "model_pack_low_poly.zip", "author": "byzmod3d",
     "date": "2023-01-11", "tags": "lowpoly,3d,characters,models",
     "credit": "없음 (CC0)"},
]

PACKS_2D = [
    {"name": "Gothicvania Magic Pack 9", "dir": "gothicvania-magic-pack-9",
     "url": "https://opengameart.org/content/gothicvania-magic-pack-9",
     "zipname": "magic_pack_9_files.zip", "author": "ansimuz",
     "date": "2022-03-10", "tags": "magic,spell,impact,effect,pixel",
     "credit": "선택: Ansimuz"},
    {"name": "Earth Impact - Magic Effect", "dir": "earth-impact-magic-effect",
     "url": "https://opengameart.org/content/earth-impact-magic-effect",
     "zipname": "Earth Impact - Magic Effect.zip", "author": "Cethiel",
     "date": "2019-06-11", "tags": "earth,magic,impact,effect,spell",
     "credit": "없음 (CC0)"},
    {"name": "2D Spell Effects", "dir": "2d-spell-effects",
     "url": "https://opengameart.org/content/2d-spell-effects",
     "zipname": "FX.zip", "author": "Mikodrak",
     "date": "2013-05-14", "tags": "spell,magic,effect,fx,2d",
     "credit": "선택: Mikodrak"},
]

CAND = PACKS_3D if MODE == "3d" else PACKS_2D
NEED = 2


def push():
    for _ in range(3):
        if subprocess.run(["git", "push", "origin", "HEAD:main"]).returncode == 0:
            return True
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        time.sleep(5)
    return False


subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)

added = []
for p in CAND:
    if len(added) >= NEED:
        break
    if p["name"].strip().lower() in names or p["url"].lower() in urls:
        print("SKIP dup:", p["name"])
        continue
    html = fetch(p["url"]).decode("utf-8", "ignore")
    if "CC0" not in html:
        print("SKIP license not CC0:", p["name"])
        continue
    if p["author"].lower() not in html.lower():
        print("SKIP author mismatch:", p["name"])
        continue
    zips = re.findall(r'href="([^"]+\.zip)"', html, re.I)
    zipurl = ""
    for z in zips:
        if p["zipname"].lower() in urllib.parse.unquote(z).lower():
            zipurl = z
            break
    if not zipurl:
        print("SKIP no zip:", p["name"], zips[:4])
        continue
    if zipurl.startswith("/"):
        zipurl = "https://opengameart.org" + zipurl
    data = fetch(zipurl)
    if len(data) > 25 * 1024 * 1024:
        print("SKIP too big:", p["name"], len(data))
        continue
    try:
        nfiles = sum(1 for i in zipfile.ZipFile(io.BytesIO(data)).infolist() if not i.is_dir())
    except Exception as e:
        print("SKIP bad zip:", p["name"], e)
        continue
    og = re.search(r'property="og:image"[^>]*content="([^"]+)"', html) or re.search(r'content="([^"]+)"[^>]*property="og:image"', html)
    prev = urllib.parse.urljoin(p["url"], og.group(1)) if og else ""
    pdata = b""
    if prev:
        try:
            pdata = fetch(prev)
        except Exception as e:
            print("preview fail:", e)
            pdata = b""
    ext = ".jpg" if re.search(r"\.jpe?g($|\?)", prev.lower()) else ".png"
    d = p["dir"]
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, p["zipname"]), "wb").write(data)
    if pdata:
        open(os.path.join(d, "preview" + ext), "wb").write(pdata)
    kb = len(data) / 1024.0
    open(os.path.join(d, "pack.md"), "w", encoding="utf-8").write(
        "# %s\n\n- 출처 URL: %s\n- 받은 파일: %s (%.1fKB)\n- 라이선스: CC0\n- 제작자: %s\n- 공개일: %s\n- 파일 수: %d\n- 파일 크기(바이트): %d\n- 태그: %s\n- 표기 요구: %s\n- AI 생성 여부: 출처 페이지에 언급 없음\n"
        % (p["name"], p["url"], p["zipname"], kb, p["author"], p["date"], nfiles, len(data), p["tags"], p["credit"]))
    open(os.path.join(d, "LICENSE-SOURCE.txt"), "w", encoding="utf-8").write(
        "%s\n\n출처 URL: %s\n표기 라이선스: CC0\n제작자: %s\n공개일: %s\n\n이 파일은 수집자가 출처 페이지의 라이선스 표기를 기록한 것입니다.\n원본 배포물에 라이선스 파일이 포함되어 있지 않으면 이 파일이 그 역할을 합니다.\n"
        % (p["name"], p["url"], p["author"], p["date"]))
    subprocess.run(["git", "add", d], check=True)
    subprocess.run(["git", "commit", "-m", "에셋: " + p["name"] + " 추가"], check=True)
    if not push():
        raise SystemExit("push failed: " + p["name"])
    print("ADDED:", p["name"], nfiles, "files", len(data), "bytes ->", d)
    added.append(p)
    names.add(p["name"].strip().lower())
    urls.add(p["url"].lower())

if len(added) < NEED:
    raise SystemExit("only %d packs added" % len(added))

rd = open("README.md", encoding="utf-8").read()
cnt = sum(1 for x in os.listdir(".") if os.path.isdir(x) and not x.startswith(".") and x != "previews")
label = "3D" if MODE == "3d" else "이펙트"
joined = "·".join(a["name"] for a in added)
if MODE == "2d":
    m = re.search(r"현재 총 (\d+)팩 \(catalog\.csv 기준 assets-2d-pixel 저장소 팩 수; ", rd)
    if m:
        new = int(m.group(1)) + len(added)
        rd = rd.replace(m.group(0), "현재 총 %d팩 (catalog.csv 기준 assets-2d-pixel 저장소 팩 수; A98: %s 이펙트 %d팩 추가(%d팩). " % (new, joined, len(added), new), 1)
    else:
        rd = "현재 총 %d팩 (A98: %s 이펙트 %d팩 추가).\n\n" % (cnt, joined, len(added)) + rd
else:
    if re.search(r"수록 팩: \d+팩?", rd):
        rd = re.sub(r"수록 팩: \d+팩?", "수록 팩: %d팩" % cnt, rd, count=1)
    elif "## 수록 팩" in rd:
        rd = rd.replace("## 수록 팩", "수록 팩: %d팩\n\n## 수록 팩" % cnt, 1)
    else:
        rd = rd.rstrip("\n") + "\n\n수록 팩: %d팩\n" % cnt

entries = ""
for p in added:
    ext = ".jpg" if os.path.exists(os.path.join(p["dir"], "preview.jpg")) else ".png"
    kb = os.path.getsize(os.path.join(p["dir"], p["zipname"])) / 1024.0
    entries += "\n### %s\n![%s 미리보기](%s/preview%s)\n- 파일: `%s` (%.1fKB) — 저장소 내 포함\n- 제작: %s / 라이선스: CC0 / 원본: %s\n" % (
        p["name"], p["name"], p["dir"], ext, p["zipname"], kb, p["author"], p["url"])
if "## 다운로드" in rd:
    rd = rd.replace("\n## 다운로드", entries + "\n## 다운로드", 1)
else:
    rd = rd.rstrip("\n") + "\n" + entries

open("README.md", "w", encoding="utf-8").write(rd)
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "문서: A98 %s %d팩 README 갱신" % (label, len(added))], check=True)
if not push():
    raise SystemExit("push failed: README")
print("README packs:", cnt)
print("DONE", json.dumps([a["name"] for a in added], ensure_ascii=False))
