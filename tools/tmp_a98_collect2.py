import os, re, sys, csv, io, json, time, zipfile, subprocess, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}
CATALOG = "https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv"
MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

CAND = [
    {"url": "https://opengameart.org/content/gothicvania-magic-pack-9", "tags": "magic,spell,impact,effect,pixel"},
    {"url": "https://opengameart.org/content/earth-impact-magic-effect", "tags": "earth,magic,impact,effect,spell"},
    {"url": "https://opengameart.org/content/2d-spell-effects", "tags": "spell,magic,effect,fx,2d"},
    {"url": "https://opengameart.org/content/weapon-slash-effect", "tags": "slash,hit,weapon,effect,pixel"},
    {"url": "https://opengameart.org/content/gothicvania-magic-pack-8", "tags": "magic,spell,impact,effect,pixel"},
    {"url": "https://opengameart.org/content/gothicvania-magic-pack-7", "tags": "magic,spell,impact,effect,pixel"},
    {"url": "https://opengameart.org/content/gothicvania-magic-pack-6", "tags": "magic,spell,impact,effect,pixel"},
    {"url": "https://opengameart.org/content/gothicvania-magic-pack-5", "tags": "magic,spell,impact,effect,pixel"},
    {"url": "https://opengameart.org/content/slash-effect", "tags": "slash,hit,effect,2d"},
    {"url": "https://opengameart.org/content/pixel-art-spells", "tags": "spell,magic,projectile,pixel"},
]
NEED = 2


def fetch(u, tries=3):
    err = None
    for _ in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read()
        except Exception as e:
            err = e
            time.sleep(3)
    raise err


def push():
    for _ in range(3):
        if subprocess.run(["git", "push", "origin", "HEAD:main"]).returncode == 0:
            return True
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        time.sleep(5)
    return False


cat = fetch(CATALOG).decode("utf-8")
rows = list(csv.reader(io.StringIO(cat)))
hdr = rows[0]
ni, ui = hdr.index("name"), hdr.index("source_url")
names = set(r[ni].strip().lower() for r in rows[1:] if r)
urls = set(r[ui].strip().lower() for r in rows[1:] if r)
print("catalog rows:", len(rows) - 1)

subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)

added = []
for c in CAND:
    if len(added) >= NEED:
        break
    u = c["url"]
    try:
        html = fetch(u).decode("utf-8", "ignore")
    except Exception as e:
        print("SKIP fetch:", u, e)
        continue
    t = re.search(r"<title>\s*(.*?)\s*\|", html)
    title = re.sub(r"\s+", " ", t.group(1)).strip() if t else ""
    if not title:
        print("SKIP no title:", u)
        continue
    if title.strip().lower() in names or u.lower() in urls:
        print("SKIP dup:", title)
        continue
    if "CC0" not in html:
        print("SKIP license:", title)
        continue
    a = re.search(r"Author:[\s\S]{0,400}?<a[^>]*>([^<]{2,60})</a>", html)
    author = a.group(1).strip() if a else ""
    d = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", html)
    if not author or not d:
        print("SKIP meta:", title, repr(author), bool(d))
        continue
    date = "%s-%02d-%02d" % (d.group(3), MONTHS[d.group(1)], int(d.group(2)))
    zips = re.findall(r'href="([^"]+\.zip)"', html, re.I)
    if not zips:
        print("SKIP no zip:", title)
        continue
    zipurl = zips[0]
    if zipurl.startswith("/"):
        zipurl = "https://opengameart.org" + zipurl
    zname = urllib.parse.unquote(zipurl.rsplit("/", 1)[-1])
    data = fetch(zipurl)
    if len(data) > 25 * 1024 * 1024:
        print("SKIP too big:", title, len(data))
        continue
    try:
        nfiles = sum(1 for i in zipfile.ZipFile(io.BytesIO(data)).infolist() if not i.is_dir())
    except Exception as e:
        print("SKIP bad zip:", title, e)
        continue
    og = re.search(r'property="og:image"[^>]*content="([^"]+)"', html) or re.search(r'content="([^"]+)"[^>]*property="og:image"', html)
    prev = urllib.parse.urljoin(u, og.group(1)) if og else ""
    pdata = b""
    if prev:
        try:
            pdata = fetch(prev)
        except Exception as e:
            print("preview fail:", e)
    ext = ".jpg" if re.search(r"\.jpe?g($|\?)", prev.lower()) else ".png"
    d_slug = os.path.basename(u.rstrip("/")).lower()
    d_slug = re.sub(r"[^a-z0-9\-]+", "-", d_slug).strip("-")
    os.makedirs(d_slug, exist_ok=True)
    open(os.path.join(d_slug, zname), "wb").write(data)
    if pdata:
        open(os.path.join(d_slug, "preview" + ext), "wb").write(pdata)
    credit = "없음 (CC0)"
    if author.lower() in html.lower() and re.search(r"(?i)optional|not mandatory", html):
        credit = "선택: %s" % author
    open(os.path.join(d_slug, "pack.md"), "w", encoding="utf-8").write(
        "# %s\n\n- 출처 URL: %s\n- 받은 파일: %s (%.1fKB)\n- 라이선스: CC0\n- 제작자: %s\n- 공개일: %s\n- 파일 수: %d\n- 파일 크기(바이트): %d\n- 태그: %s\n- 표기 요구: %s\n- AI 생성 여부: 출처 페이지에 언급 없음\n"
        % (title, u, zname, len(data) / 1024.0, author, date, nfiles, len(data), c["tags"], credit))
    open(os.path.join(d_slug, "LICENSE-SOURCE.txt"), "w", encoding="utf-8").write(
        "%s\n\n출처 URL: %s\n표기 라이선스: CC0\n제작자: %s\n공개일: %s\n\n이 파일은 수집자가 출처 페이지의 라이선스 표기를 기록한 것입니다.\n원본 배포물에 라이선스 파일이 포함되어 있지 않으면 이 파일이 그 역할을 합니다.\n"
        % (title, u, author, date))
    subprocess.run(["git", "add", d_slug], check=True)
    subprocess.run(["git", "commit", "-m", "에셋: " + title + " 추가"], check=True)
    if not push():
        raise SystemExit("push failed: " + title)
    print("ADDED:", title, "|", author, "|", date, "|", nfiles, "files", len(data), "bytes ->", d_slug)
    added.append({"name": title, "dir": d_slug, "author": author, "date": date, "url": u, "zip": zname, "tags": c["tags"], "credit": credit, "nfiles": nfiles, "bytes": len(data)})
    names.add(title.strip().lower())
    urls.add(u.lower())

if len(added) < NEED:
    raise SystemExit("only %d packs added" % len(added))

rd = open("README.md", encoding="utf-8").read()
cnt = sum(1 for x in os.listdir(".") if os.path.isdir(x) and not x.startswith("."))
joined = "·".join(a["name"] for a in added)
m = re.search(r"현재 총 (\d+)팩", rd)
if m:
    new = int(m.group(1)) + len(added)
    rd = rd.replace("현재 총 %s팩" % m.group(1), "현재 총 %d팩" % new, 1)
    head = re.search(r"(저장소 팩 수; )", rd)
    if head:
        rd = rd[:head.end()] + ("A98: %s 이펙트 %d팩 추가(%d팩). " % (joined, len(added), new)) + rd[head.end():]
else:
    rd = "현재 총 %d팩 (A98: %s 이펙트 %d팩 추가).\n\n" % (cnt, joined, len(added)) + rd

entries = ""
for a in added:
    ext = ".jpg" if os.path.exists(os.path.join(a["dir"], "preview.jpg")) else ".png"
    entries += "\n### %s\n![%s 미리보기](%s/preview%s)\n- 파일: `%s` (%.1fKB) — 저장소 내 포함\n- 제작: %s / 라이선스: CC0 / 원본: %s\n" % (
        a["name"], a["name"], a["dir"], ext, a["zip"], a["bytes"] / 1024.0, a["author"], a["url"])
if "## 다운로드" in rd:
    rd = rd.replace("\n## 다운로드", entries + "\n## 다운로드", 1)
else:
    rd = rd.rstrip("\n") + "\n" + entries
open("README.md", "w", encoding="utf-8").write(rd)
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "문서: A98 이펙트 %d팩 README 갱신" % len(added)], check=True)
if not push():
    raise SystemExit("push failed: README")
print("DONE", json.dumps([a["name"] for a in added], ensure_ascii=False))
