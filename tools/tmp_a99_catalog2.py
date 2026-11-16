import io, os, re, subprocess

ROWS = [
    ["3D Vehicles Pack", "assets-3d-lowpoly-2", "3d-vehicles-pack/vehicle_pack.zip", "3D 모델",
     "vehicles,3d,lowpoly,clay", "mehrasaur", "https://opengameart.org/content/3d-vehicles-pack", "CC0",
     "없음 (CC0)", "2026-11-16", "파일 14개 차량 모델(obj/fbx/blend); zip 2.6MB 저장소 내 포함"],
    ["Low Poly RPG Pack", "assets-3d-lowpoly-2", "releases/download/v1.0/ultimate_rpg_items_pack_by_quaternius_0.zip", "3D 모델",
     "rpg,items,3d,lowpoly", "quaternius", "https://opengameart.org/content/low-poly-rpg-pack", "CC0",
     "없음 (CC0)", "2026-11-16", "파일 533개; 42.6MB 릴리스 v1.0 첨부"],
    ["LowPoly Survival Pack", "assets-3d-lowpoly-2", "releases/download/v1.0/survival_pack_-_sept_2020.zip", "3D 모델",
     "survival,3d,lowpoly,props", "quaternius", "https://opengameart.org/content/lowpoly-survival-pack", "CC0",
     "없음 (CC0)", "2026-11-16", "파일 214개; 5.7MB 릴리스 v1.0 첨부"],
    ["IgnisForge Free SFX Sampler", "assets-audio", "ignisforge-free-sfx-sampler/ignisforge-oga-sampler-cc0_7.zip", "효과음",
     "sfx,retro,arcade,spell,audio", "ignisforge",
     "https://opengameart.org/content/ignisforge-free-sfx-sampler-43-synthesized-retro-sound-effects", "CC0",
     "없음 (CC0)", "2026-11-16", "합성 레트로 효과음 43종(주문·폭발·타격); zip 1.2MB 저장소 내 포함"],
]


def sh(cmd):
    print(cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


def csv_line(row):
    out = []
    for c in row:
        if "," in c or '"' in c:
            out.append('"' + c.replace('"', '""') + '"')
        else:
            out.append(c)
    return ",".join(out)


def main():
    text = open("catalog.csv", encoding="utf-8").read()
    for row in ROWS:
        if row[0] in text:
            print("skip existing", row[0], flush=True)
            continue
        text = text.rstrip("\n") + "\n" + csv_line(row) + "\n"
        print("added row", row[0], flush=True)
    open("catalog.csv", "w", encoding="utf-8").write(text)
    total = len([l for l in text.splitlines() if l.strip()]) - 1
    print("csv data rows", total, flush=True)
    log = open("docs/log.md", encoding="utf-8").read()
    if "A99:" not in log:
        entry = ("- 2026-11-16 A99: 3D Vehicles Pack, Low Poly RPG Pack, LowPoly Survival Pack, IgnisForge Free SFX Sampler"
                 "(4팩, catalog.csv " + str(total) + "행; 3D 3 + 효과음 1). 임시 GitHub Actions 워크플로(tmp-a99-*.yml)와 파이썬 스크립트로 러너에서 OpenGameArt 원본 zip을 받아 팩 폴더 생성·커밋."
                 " 3D 3팩은 assets-3d-lowpoly-2, 효과음 1팩은 assets-audio. 모두 CC0(출처 페이지 표기 확인)."
                 " 42.6MB·5.7MB zip은 릴리스 v1.0 첨부, 2.6MB·1.2MB는 저장소 내 포함."
                 " 중복 검사는 assets-index.min.json 이름 대조로 스크립트에서 수행. catalog.csv·docs/log.md만 수정(색인은 Actions 자동 갱신).\n")
        open("docs/log.md", "w", encoding="utf-8").write(log.rstrip("\n") + "\n" + entry)
    sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" add catalog.csv docs/log.md')
    sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" commit -m "카탈로그: A99 4팩 등록"')
    sh("git push origin HEAD:main")
    print("pushed", flush=True)


main()
