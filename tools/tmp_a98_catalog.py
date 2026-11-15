import os, re, io, csv, json, time, zipfile, hashlib, subprocess, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; asset-collector/1.0)"}
TODAY = "2026-11-15"
ROUND = "A98"

PACKS = [
    {"repo": "assets-3d-lowpoly-2", "dir": "lowpoly-survival-item-pack", "type": "3D 모델"},
    {"repo": "assets-3d-lowpoly-2", "dir": "low-poly-3d-model-packs", "type": "3D 모델"},
    {"repo": "assets-2d-pixel", "dir": "fire-and-spell-animations", "type": "2D 이펙트",
     "tag": "a98-fire-and-spell-animations"},
]


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


for p in PACKS:
    listing = json.loads(fetch("https://api.github.com/repos/sigco3111/%s/contents/%s" % (p["repo"], p["dir"])).decode("utf-8"))
    have = {e["name"] for e in listing}
    md = fetch("https://raw.githubusercontent.com/sigco3111/%s/main/%s/pack.md" % (p["repo"], p["dir"])).decode("utf-8")

    def field(label):
        m = re.search(r"^- " + label + r": (.*)$", md, re.M)
        return m.group(1).strip() if m else ""

    p["name"] = re.search(r"^# (.*)$", md, re.M).group(1).strip()
    p["author"] = field("제작자")
    p["date"] = field("공개일")
    p["tags"] = field("태그")
    p["url"] = field("출처 URL")
    p["license"] = field("라이선스")
    p["credit"] = field("표기 요구")
    p["nfiles"] = int(field("파일 수"))
    p["bytes"] = int(field("파일 크기(바이트)")) if field("파일 크기(바이트)").isdigit() else 0
    p["zip"] = field("받은 파일").split(" (")[0].strip()
    p["thumb"] = next((n for n in have if n.startswith("preview")), "")
    if not p["thumb"] or not p["zip"]:
        raise SystemExit("missing thumb/zip in " + p["dir"])
    if p["zip"] in have:
        p["file"] = p["dir"] + "/" + p["zip"]
        p["where"] = "저장소 내 포함"
    else:
        p["file"] = "releases/download/%s/%s" % (p["tag"], p["zip"])
        p["where"] = "릴리스 첨부"
    print("OK", p["name"], "|", p["author"], "|", p["date"], "|", p["nfiles"], "|", p["file"])

csv_text = open("catalog.csv", encoding="utf-8").read()
rows = list(csv.reader(io.StringIO(csv_text)))
hdr = rows[0]
ni, ui = hdr.index("name"), hdr.index("source_url")
names = set(r[ni].strip().lower() for r in rows[1:] if r)
urls = set(r[ui].strip().lower() for r in rows[1:] if r)
for p in PACKS:
    if p["name"].strip().lower() in names or p["url"].lower() in urls:
        raise SystemExit("already in catalog: " + p["name"])

buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
for p in PACKS:
    attr = ""
    if p["credit"].startswith("선택:"):
        attr = "optional: " + p["credit"].split(":", 1)[1].strip()
    notes = "파일 %d개; 페이지 zip을 수정 없이 보관(%s); 썸네일 %s" % (p["nfiles"], p["where"], p["thumb"])
    w.writerow([p["name"], p["repo"], p["file"], p["type"], p["tags"], p["author"], p["url"], p["license"], attr, TODAY, notes])
if not csv_text.endswith("\n"):
    csv_text += "\n"
open("catalog.csv", "w", encoding="utf-8").write(csv_text + buf.getvalue())
print("rows:", len(rows) - 1 + len(PACKS))

rows2 = list(csv.reader(io.StringIO(open("catalog.csv", encoding="utf-8").read())))
ri = rows2[0].index("repo")
counts = {}
for r in rows2[1:]:
    if r:
        counts[r[ri]] = counts.get(r[ri], 0) + 1
total = sum(counts.values())

REPOS = [
    ("assets-2d-pixel", "2D 픽셀 스프라이트, 타일셋, 이펙트"),
    ("assets-3d-lowpoly", "3D 로우폴리 모델 (GLB·OBJ)"),
    ("assets-3d-lowpoly-2", "3D 로우폴리 모델 2호 저장소"),
    ("assets-ui-icons", "UI 키트, 아이콘"),
    ("assets-audio", "효과음, 배경음악 (OGG)"),
    ("assets-2d-portraits", "초상화"),
]
n3d = sum(1 for p in PACKS if p["type"].startswith("3D"))
sec = ["## %s %s 추가 (%d팩, 총 %d팩)" % (TODAY, ROUND, len(PACKS), total), ""]
sec.append("%s 라운드: OpenGameArt에서 아직 카탈로그에 없는 로우폴리 3D 팩 %d개(%s)와 타격·마법 이펙트 스프라이트 %d개(%s)를 모았습니다. 후보는 러너 안에서 전체 catalog.csv(name + source URL)와 대조해 걸러냈고, 팩마다 출처 페이지의 License(s) 항목이 CC0임을 확인했습니다." % (
    ROUND, n3d, ", ".join(p["name"] for p in PACKS if p["type"].startswith("3D")),
    len(PACKS) - n3d, ", ".join(p["name"] for p in PACKS if not p["type"].startswith("3D"))))
sec.append("")
sec.append("| 팩 | 저장소 | 라이선스 | 수록 위치 |")
sec.append("| --- | --- | --- | --- |")
for p in PACKS:
    sec.append("| [%s](%s) | %s | %s | %s |" % (p["name"], p["url"], p["repo"], p["license"], p["where"]))
sec.append("")
sec.append("종류: 3D %d팩, 2D 이펙트 %d팩." % (n3d, len(PACKS) - n3d))
sec.append("")
sec.append("| 저장소 | 내용 | 수록 |")
sec.append("| --- | --- | --- |")
for repo, desc in REPOS:
    sec.append("| [%s](https://github.com/sigco3111/%s) | %s | %d팩 |" % (repo, repo, desc, counts.get(repo, 0)))
sec.append("")
sec.append("총 %d팩입니다." % total)
sec.append("")
rd = open("README.md", encoding="utf-8").read()
m = re.search(r"^## 2026-", rd, re.M)
if not m:
    raise SystemExit("README anchor not found")
rd = rd[:m.start()] + "\n".join(sec) + "\n" + rd[m.start():]
open("README.md", "w", encoding="utf-8").write(rd)

log = open("docs/log.md", encoding="utf-8").read()
if not log.endswith("\n"):
    log += "\n"
log += ("- %s %s: %s (%d팩, 총 %d팩; 3D %d(assets-3d-lowpoly-2), 2D 이펙트 %d(assets-2d-pixel); AI 생성 아님; 모두 OpenGameArt 페이지 License(s) CC0 단독 표기). 소유자의 짧은 수집 라운드(팩 3~4개, 3D 절반 이상, 나머지 타격·마법 이펙트) 지시. 시작 전 catalog.csv %d행의 name·source_url로 후보를 대조했고, 이미 있는 후보(Retro Medieval Kit·Retro Urban Kit·Low Poly Camping Assets·Gothicvania Magic Pack 9·Earth Impact·2D Spell Effects·Weapon Slash·Pixel Art Spells)는 러너가 건너뛰고 다음 후보를 채택했습니다. 2D 쪽은 자동 후보 중 이펙트가 아닌 팩 2개(Mechanized Magic UI 팩, 2d Magic Book 스프라이트)가 먼저 들어와 같은 라운드에서 제거하고 FIre and Spell Animations로 교체했습니다. 팩당 1커밋(에셋: <팩 이름> 추가)으로 각 저장소 main에 반영했고, 10.8MB zip인 FIre and Spell Animations는 5MB 초과 zip 규칙에 따라 Releases(%s) 첨부로 옮기고 catalog.csv의 file 열에 releases/download 경로를 적었습니다. 카탈로그: catalog.csv %d행 추가(%d→%d행), README %s 섹션과 저장소 표·총계 줄, docs/log.md 갱신. assets-index*.json·docs/wiki·llms.txt는 직접 수정하지 않고 Actions '색인: 자동 갱신' 커밋으로 갱신하며, 임시 스크립트(tools/tmp_a98_*.py)·로그 파일·임시 워크플로는 라운드 끝에 정리합니다.\n" % (
    TODAY, ROUND, ", ".join("%s (%s, %s)" % (p["name"], p["author"], p["license"]) for p in PACKS),
    len(PACKS), total, n3d, len(PACKS) - n3d, len(rows) - 1,
    "a98-fire-and-spell-animations", len(PACKS), len(rows) - 1, len(rows) - 1 + len(PACKS), ROUND))
open("docs/log.md", "w", encoding="utf-8").write(log)

subprocess.run(["git", "config", "user.name", "sigco3111"], check=True)
subprocess.run(["git", "config", "user.email", "sigco3111k@gmail.com"], check=True)
subprocess.run(["git", "add", "catalog.csv", "README.md", "docs/log.md"], check=True)
subprocess.run(["git", "commit", "-m", "카탈로그: A98 3팩 추가"], check=True)
if not push():
    raise SystemExit("push failed")
print("DONE total=", total, json.dumps(counts, ensure_ascii=False))
