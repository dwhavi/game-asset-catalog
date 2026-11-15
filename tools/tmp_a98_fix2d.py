import os, re, sys, csv, io, json, time, zipfile, traceback, shutil, subprocess, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}
CATALOG = "https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv"
MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
BAD = ["mechanized-magic-ultimate-ui-pack", "2d-magic-book"]
EFFECT_WORDS = ("effect", "spell", "hit", "impact", "slash", "explosion", "lightning", "fire", "burst", "magic", "particle", "sparkle")
BAD_WORDS = ("ui", "icon", "hud", "tile", "card", "book", "character", "font", "cursor", "emoji", "vector cards")
NEED = 1
LOG = []


def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    LOG.append(line)


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


def fix_readme():
    rd = open("README.md", encoding="utf-8").read()
    before = rd
    for b in BAD:
        rd = re.sub(r"\n### [^\n]*\n!\[[^\n]*" + re.escape(b) + r"[^\n]*\n(?:- [^\n]*\n)*", "\n", rd)
    rd = re.sub(r"A98: Mechanized Magic: Ultimate UI Pack·2d Magic Book 이펙트 2팩 추가\(\d+팩\)\. ", "", rd)
    m = re.search(r"현재 총 (\d+)팩", rd)
    if m:
        rd = rd.replace(m.group(0), "현재 총 %d팩" % (int(m.group(1)) - 2), 1)
    return rd, before != rd


def run():
    cat = fetch(CATALOG).decode("utf-8")
    rows = list(csv.reader(io.StringIO(cat)))
    hdr = rows[0]
    ni, ui = hdr.index("name"), hdr.index("source_url")
    names = set(r[ni].strip().lower() for r in rows[1:] if r)
    urls = set(r[ui].strip().lower() for r in rows[1:] if r)
    log("catalog rows:", len(rows) - 1)

    subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
    subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)

    # 1) 잘못 추가한 두 팩 제거 (UI 팩·책 스프라이트는 이펙트 아님)
    removed = []
    for b in BAD:
        if os.path.isdir(b):
            subprocess.run(["git", "rm", "-r", "-q", b], check=True)
            removed.append(b)
    rd, changed = fix_readme()
    if changed:
        open("README.md", "w", encoding="utf-8").write(rd)
        subprocess.run(["git", "add", "README.md"], check=True)
    if removed or changed:
        subprocess.run(["git", "commit", "-m", "정리: A98 이펙트가 아닌 팩 2개 제거"], check=True)
        if not push():
            raise SystemExit("push failed: cleanup")
        log("CLEANUP removed:", removed, "readme changed:", changed)

    # 2) 이펙트 팩 1개 추가 (카탈로그에 없는 CC0 이펙트)
    cands = ["https://opengameart.org/content/hit-animation-frame-by-frame"]
    for keys in ("hit", "impact", "spell", "slash"):
        try:
            h = fetch("https://opengameart.org/art-search-advanced?keys=" + keys + "&field_art_type_tid%5B%5D=9&sort_by=created&sort_order=DESC").decode("utf-8", "ignore")
            for slug, title in re.findall(r'href="/content/([a-z0-9\-]+)"[^>]*>\s*([^<]{2,90}?)\s*<', h):
                u = "https://opengameart.org/content/" + slug
                if u not in cands:
                    cands.append(u)
        except Exception as e:
            log("listing fail", keys, e)
    log("candidates:", len(cands))

    added = []
    for u in cands:
        if len(added) >= NEED:
            break
        try:
            html = fetch(u).decode("utf-8", "ignore")
            t = re.search(r"<title>\s*(.*?)\s*\|", html)
            title = re.sub(r"\s+", " ", t.group(1)).strip() if t else ""
            if not title:
                continue
            low = title.lower()
            if any(w in low for w in BAD_WORDS) or not any(w in low for w in EFFECT_WORDS):
                log("SKIP not effect title:", title)
                continue
            if title.lower() in names or u.lower() in urls:
                log("SKIP dup:", title)
                continue
            lic = re.search(r"License\(s\):[\s\S]{0,120}?>\s*([^<\n]+?)\s*<", html)
            if "CC0" not in html or (lic and "CC0" not in lic.group(1)):
                log("SKIP license:", title)
                continue
            a = re.search(r"Author:[\s\S]{0,400}?<a[^>]*>([^<]{2,60})</a>", html)
            d = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", html)
            if not a or not d:
                log("SKIP meta:", title)
                continue
            author = a.group(1).strip()
            date = "%s-%02d-%02d" % (d.group(3), MONTHS[d.group(1)], int(d.group(2)))
            zips = re.findall(r'href="([^"]+\.zip)"', html, re.I)
            if not zips:
                log("SKIP no zip:", title)
                continue
            zipurl = zips[0]
            if zipurl.startswith("/"):
                zipurl = "https://opengameart.org" + zipurl
            data = fetch(zipurl)
            if len(data) > 25 * 1024 * 1024:
                log("SKIP too big:", title)
                continue
            infos = [i for i in zipfile.ZipFile(io.BytesIO(data)).infolist() if not i.is_dir()]
            nfiles = len(infos)
            og = re.search(r'property="og:image"[^>]*content="([^"]+)"', html) or re.search(r'content="([^"]+)"[^>]*property="og:image"', html)
            prev = urllib.parse.urljoin(u, og.group(1)) if og else ""
            pdata = fetch(prev) if prev else b""
            ext = ".jpg" if re.search(r"\.jpe?g($|\?)", prev.lower()) else ".png"
            zname = urllib.parse.unquote(zipurl.rsplit("/", 1)[-1])
            slug = re.sub(r"[^a-z0-9\-]+", "-", os.path.basename(u.rstrip("/")).lower()).strip("-")
            os.makedirs(slug, exist_ok=True)
            open(os.path.join(slug, zname), "wb").write(data)
            if pdata:
                open(os.path.join(slug, "preview" + ext), "wb").write(pdata)
            credit = "선택: %s" % author if re.search(r"(?i)optional|not mandatory", html) else "없음 (CC0)"
            open(os.path.join(slug, "pack.md"), "w", encoding="utf-8").write(
                "# %s\n\n- 출처 URL: %s\n- 받은 파일: %s (%.1fKB)\n- 라이선스: CC0\n- 제작자: %s\n- 공개일: %s\n- 파일 수: %d\n- 파일 크기(바이트): %d\n- 태그: effect,hit,impact,sprite,2d\n- 표기 요구: %s\n- AI 생성 여부: 출처 페이지에 언급 없음\n"
                % (title, u, zname, len(data) / 1024.0, author, date, nfiles, len(data), credit))
            open(os.path.join(slug, "LICENSE-SOURCE.txt"), "w", encoding="utf-8").write(
                "%s\n\n출처 URL: %s\n표기 라이선스: CC0\n제작자: %s\n공개일: %s\n\n이 파일은 수집자가 출처 페이지의 라이선스 표기를 기록한 것입니다.\n원본 배포물에 라이선스 파일이 포함되어 있지 않으면 이 파일이 그 역할을 합니다.\n"
                % (title, u, author, date))
            subprocess.run(["git", "add", slug], check=True)
            subprocess.run(["git", "commit", "-m", "에셋: " + title + " 추가"], check=True)
            if not push():
                raise SystemExit("push failed: " + title)
            log("ADDED:", title, "|", author, "|", date, "|", nfiles, "files |", len(data), "bytes ->", slug)
            added.append({"name": title, "dir": slug, "author": author, "url": u, "zip": zname, "bytes": len(data)})
            names.add(title.lower())
            urls.add(u.lower())
        except SystemExit:
            raise
        except Exception as e:
            log("ERROR", u, repr(e))
    if not added:
        log("NO effect pack added")
        return
    rd, _ = fix_readme()
    m = re.search(r"현재 총 (\d+)팩", rd)
    if m:
        rd = rd.replace(m.group(0), "현재 총 %d팩" % (int(m.group(1)) + len(added)), 1)
    entries = ""
    for a in added:
        ext = ".jpg" if os.path.exists(os.path.join(a["dir"], "preview.jpg")) else ".png"
        entries += "\n### %s\n![%s 미리보기](%s/preview%s)\n- 파일: \u0060%s\u0060 (%.1fKB) — 저장소 내 포함\n- 제작: %s / 라이선스: CC0 / 원본: %s\n" % (
            a["name"], a["name"], a["dir"], ext, a["zip"], a["bytes"] / 1024.0, a["author"], a["url"])
    if "## 다운로드" in rd:
        rd = rd.replace("\n## 다운로드", entries + "\n## 다운로드", 1)
    else:
        rd = rd.rstrip("\n") + "\n" + entries
    open("README.md", "w", encoding="utf-8").write(rd)
    subprocess.run(["git", "add", "README.md"], check=True)
    subprocess.run(["git", "commit", "-m", "문서: A98 이펙트 %d팩 README 갱신" % len(added)], check=False)
    push()
    log("README updated")


try:
    run()
except SystemExit as e:
    log("EXIT", str(e))
except Exception:
    log("FATAL")
    traceback.print_exc()

try:
    open("tmp-a98-log2.txt", "w", encoding="utf-8").write("\n".join(LOG) + "\n")
    subprocess.run(["git", "add", "-f", "tmp-a98-log2.txt"], check=False)
    subprocess.run(["git", "commit", "-m", "임시: A98 정리 로그"], check=False)
    push()
except Exception:
    traceback.print_exc()
log("done")
