import re, csv, io, json, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}

def fetch(u):
    err = None
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
        except Exception as e:
            err = e
    raise err

cat = fetch("https://raw.githubusercontent.com/sigco3111/game-asset-catalog/main/catalog.csv").decode("utf-8")
rows = list(csv.reader(io.StringIO(cat)))
hdr = rows[0]
ni = hdr.index("name")
ui = hdr.index("source_url")
names = set(r[ni].strip().lower() for r in rows[1:] if r)
urls = set(r[ui].strip().lower() for r in rows[1:] if r)
print("catalog rows", len(rows) - 1)

def listing(tid, page):
    u = "https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=%d&sort_by=created&sort_order=DESC&page=%d" % (tid, page)
    h = fetch(u).decode("utf-8", "ignore")
    items = re.findall(r'href="/content/([a-z0-9\-]+)"[^>]*>\s*([^<]{2,90}?)\s*</a>', h)
    out = []
    for slug, title in items:
        if slug not in [s for s, _ in out]:
            out.append((slug, title))
    return out

for tid in (10, 9):
    seen = []
    for page in (0, 1):
        for slug, title in listing(tid, page):
            if slug in [s for s, _ in seen]:
                continue
            seen.append((slug, title))
    print("TYPE", tid, "count", len(seen))
    for slug, title in seen[:16]:
        page = "https://opengameart.org/content/" + slug
        try:
            h = fetch(page).decode("utf-8", "ignore")
        except Exception as e:
            print("ERR", slug, e)
            continue
        m = re.search(r'field-name-field-art-licenses(.{0,600}?)</div>\s*</div>', h, re.S)
        lic = ""
        if m:
            lic = " | ".join(re.findall(r'<a[^>]*>([^<]{2,40})</a>', m.group(1)))
        if not lic:
            lic = "RAW:" + " ".join(re.findall(r'(CC0|CC-BY(?:-SA)?(?: \d\.\d)?|GPL \d\.\d|OGA-BY 3\.0|CC-BY-NC|CC-BY-ND)', h))[:120]
        zips = re.findall(r'href="((?:https://opengameart\.org)?/sites/default/files/[^"]+\.(?:zip|tar\.gz|7z|rar))"', h)
        dup = "DUP" if (title.strip().lower() in names or page.lower() in urls) else "new"
        print(json.dumps(dict(tid=tid, slug=slug, title=title.strip(), lic=lic, nzip=len(zips), zip=(zips[0] if zips else ""), dup=dup), ensure_ascii=True))
print("done")
