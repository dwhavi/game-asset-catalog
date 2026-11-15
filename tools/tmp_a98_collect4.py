import os, re, sys, csv, io, json, time, zipfile, traceback, subprocess, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}
CATALOG = "https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv"
MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
KEYWORDS = ("effect", "effects", "magic", "spell", "impact", "slash", "hit", "explosion", "fire", "lightning", "particle", "aura", "beam", "shock", "burst")
NEED = 2
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


def listing(keys, page):
    u = "https://opengameart.org/art-search-advanced?keys=" + urllib.parse.quote(keys) + "&field_art_type_tid%5B%5D=9&sort_by=created&sort_order=DESC&page=" + str(page)
    h = fetch(u).decode("utf-8", "ignore")
    out = []
    for slug, title in re.findall(r'href="/content/([a-z0-9\-]+)"[^>]*>\s*([^<]{2,90}?)\s*<', h):
        if slug not in [s for s, _ in out]:
            out.append((slug, title.strip()))
    return out


def run():
    cat = fetch(CATALOG).decode("utf-8")
    rows = list(csv.reader(io.StringIO(cat)))
    hdr = rows[0]
    ni, ui = hdr.index("name"), hdr.index("source_url")
    names = set(r[ni].strip().lower() for r in rows[1:] if r)
    urls = set(r[ui].strip().lower() for r in rows[1:] if r)
    log("catalog rows:", len(rows) - 1)

    cands = []
    seenurl = set()
    for keys in ("effect", "magic", "impact", "slash", "spell", "explosion"):
        for page in (0, 1):
            try:
                for slug, title in listing(keys, page):
                    lt = title.lower()
                    if not any(k in lt for k in KEYWORDS):
                        continue
                    u = "https://opengameart.org/content/" + slug
                    if u in seenurl:
                        continue
                    seenurl.add(u)
                    cands.append((u, title))
            except Exception as e:
                log("listing fail", keys, page, e)
    curated = [
        ("https://opengameart.org/content/gothicvania-magic-pack-9", "Gothicvania Magic Pack 9"),
        ("https://opengameart.org/content/earth-impact-magic-effect", "Earth Impact - Magic Effect"),
        ("https://opengameart.org/content/2d-spell-effects", "2D Spell Effects"),
        ("https://opengameart.org/content/weapon-slash-effect", "Weapon Slash - Effect"),
        ("https://opengameart.org/content/gothicvania-magic-pack-8", "Gothicvania Magic Pack 8"),
        ("https://opengameart.org/content/gothicvania-magic-pack-7", "Gothicvania Magic Pack 7"),
        ("https://opengameart.org/content/pixel-art-spells", "Pixel Art Spells"),
        ("https://opengameart.org/content/slash-effect", "Slash effect"),
    ]
    cands += curated

    added = []
    seen = set()
    for u, t0 in cands:
        if len(added) >= NEED:
            break
        if u in seen:
            continue
        seen.add(u)
        try:
            html = fetch(u).decode("utf-8", "ignore")
            if "CC0" not in html:
                log("SKIP license:", u)
                continue
            t = re.search(r"<title>\s*(.*?)\s*\|", html)
            title = re.sub(r"\s+", " ", t.group(1)).strip() if t else t0
            low = (title + " " + html[:4000]).lower()
            if not any(k in low for k in KEYWORDS):
                log("SKIP not effect:", title)
                continue
            if title.strip().lower() in names or u.lower() in urls:
                log("SKIP dup:", title)
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
            try:
                data = fetch(zipurl)
            except Exception as e:
                log("SKIP zip fetch:", title, e)
                continue
            if len(data) > 25 * 1024 * 1024:
                log("SKIP too big:", title, len(data))
                continue
            nfiles = sum(1 for i in zipfile.ZipFile(io.BytesIO(data)).infolist() if not i.is_dir())
            og = re.search(r'property="og:image"[^>]*content="([^"]+)"', html) or re.search(r'content="([^"]+)"[^>]*property="og:image"', html)
            prev = urllib.parse.urljoin(u, og.group(1)) if og else ""
            pdata = b""
            if prev:
                try:
                    pdata = fetch(prev)
                except Exception as e:
                    log("preview fail:", e)
            ext = ".jpg" if re.search(r"\.jpe?g($|\?)", prev.lower()) else ".png"
            zname = urllib.parse.unquote(zipurl.rsplit("/", 1)[-1])
            slug = re.sub(r"[^a-z0-9\-]+", "-", os.path.basename(u.rstrip("/")).lower()).strip("-")
            os.makedirs(slug, exist_ok=True)
            open(os.path.join(slug, zname), "wb").write(data)
            if pdata:
                open(os.path.join(slug, "preview" + ext), "wb").write(pdata)
            tags = "effect,magic,spell,impact,pixel" if "magic" in low or "spell" in low else "effect,hit,impact,pixel"
            credit = "선택: %s" % author if re.search(r"(?i)optional|not mandatory", html) else "없음 (CC0)"
            open(os.path.join(slug, "pack.md"), "w", encoding="utf-8").write(
                "# %s\n\n- 출처 URL: %s\n- 받은 파일: %s (%.1fKB)\n- 라이선스: CC0\n- 제작자: %s\n- 공개일: %s\n- 파일 수: %d\n- 파일 크기(바이트): %d\n- 태그: %s\n- 표기 요구: %s\n- AI 생성 여부: 출처 페이지에 언급 없음\n"
                % (title, u, zname, len(data) / 1024.0, author, date, nfiles, len(data), tags, credit))
            open(os.path.join(slug, "LICENSE-SOURCE.txt"), "w", encoding="utf-8").write(
                "%s\n\n출처 URL: %s\n표기 라이선스: CC0\n제작자: %s\n공개일: %s\n\n이 파일은 수집자가 출처 페이지의 라이선스 표기를 기록한 것입니다.\n원본 배포물에 라이선스 파일이 포함되어 있지 않으면 이 파일이 그 역할을 합니다.\n"
                % (title, u, author, date))
            subprocess.run(["git", "add", slug], check=True)
            subprocess.run(["git", "commit", "-m", "에셋: " + title + " 추가"], check=True)
            if not push():
                raise SystemExit("push failed: " + title)
            log("ADDED:", title, "|", author, "|", date, "|", nfiles, "files |", len(data), "bytes ->", slug)
            added.append({"name": title, "dir": slug, "author": author, "url": u, "zip": zname, "bytes": len(data)})
            names.add(title.strip().lower())
            urls.add(u.lower())
        except Exception as e:
            log("ERROR", u, repr(e))
            traceback.print_exc()
    return added


added = []
try:
    subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
    subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)
    added = run()
except Exception:
    log("FATAL")
    traceback.print_exc()


if added:
    try:
        rd = open("README.md", encoding="utf-8").read()
        m = re.search(r"현재 총 (\d+)팩", rd)
        if m:
            new = int(m.group(1)) + len(added)
            rd = rd.replace("현재 총 %s팩" % m.group(1), "현재 총 %d팩" % new, 1)
            h = re.search(r"(저장소 팩 수; )", rd)
            if h:
                rd = rd[:h.end()] + ("A98: %s 이펙트 %d팩 추가(%d팩). " % ("·".join(a["name"] for a in added), len(added), new)) + rd[h.end():]
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
        subprocess.run(["git", "commit", "-m", "문서: A98 이펙트 %d팩 README 갱신" % len(added)], check=False)
        log("README updated")
        push()
    except Exception:
        log("README update failed")
        traceback.print_exc()

try:
    open("tmp-a98-log.txt", "w", encoding="utf-8").write("\n".join(LOG) + "\n")
    subprocess.run(["git", "add", "-f", "tmp-a98-log.txt"], check=False)
    subprocess.run(["git", "commit", "-m", "임시: A98 수집 로그"], check=False)
    push()
except Exception:
    traceback.print_exc()
log("done, added=%d" % len(added))
