import subprocess

ROWS = [
    ["Low-Poly Halloween Kit", "assets-3d-lowpoly-2",
     "releases/download/v1.0/free_halloween_kit_assetquest.zip", "3D 모델",
     "halloween,props,3d,lowpoly,environment", "AssetQuest",
     "https://opengameart.org/content/low-poly-halloween-kit", "CC0", "없음 (CC0)", "2026-11-16",
     "파일 80개 할로윈 소품·환경 모델; 7.9MB 릴리스 v1.0 첨부"],
    ["Wooden Overhang Modular Kit", "assets-3d-lowpoly-2",
     "wooden-overhang-modular-kit/WoodenOverhangModularKit.zip", "3D 모델",
     "wooden,modular,3d,lowpoly,environment", "Kenney",
     "https://opengameart.org/content/wooden-overhang-modular-kit", "CC-BY 4.0",
     "있음 (제작자 Kenney · 원본 출처 링크 표기)", "2026-11-16",
     "파일 17개 목재 처마·모듈 조각; zip 3.1MB 저장소 내 포함"],
    ["Shield Spell", "assets-2d-pixel", "shield-spell/shield.zip", "2D 이펙트",
     "spell,shield,magic,effect,sprite", "Clint Bellanger",
     "https://opengameart.org/content/shield-spell", "CC-BY 3.0",
     "있음 (제작자 Clint Bellanger · 원본 출처 링크 표기)", "2026-11-16",
     "마법 방어막 이펙트 스프라이트; zip 0.48MB 저장소 내 포함"],
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

    readme = open("README.md", encoding="utf-8").read()
    readme = readme.replace("1905팩", str(total) + "팩")
    section = (
        "## 2026-11-16 A100: 3D 2팩 + 이펙트 1팩 (총 " + str(total) + "팩)\n\n"
        "A100 라운드: OpenGameArt에서 Low-Poly Halloween Kit(CC0), Wooden Overhang Modular Kit(CC-BY 4.0) 두 3D 팩과 "
        "Shield Spell(CC-BY 3.0) 마법 이펙트 스프라이트를 추가했습니다.\n"
        "3D 2팩은 assets-3d-lowpoly-2, 이펙트 1팩은 assets-2d-pixel에 있습니다. "
        "후보는 러너 안에서 assets-index.min.json 이름과 대조해 걸러냈고(중복 5+5+3건 제외), 라이선스는 각 출처 페이지 표기로 확인했습니다.\n\n"
        "| 팩 | 라이선스 | 파일 |\n| --- | --- | --- |\n"
        "| Low-Poly Halloween Kit | CC0 | 80개, 7.9MB (릴리스 v1.0) |\n"
        "| Wooden Overhang Modular Kit | CC-BY 4.0 | 17개, 3.1MB |\n"
        "| Shield Spell | CC-BY 3.0 | 방어막 스프라이트, 0.48MB |\n\n"
    )
    anchor = "## 저장소 구성"
    if "A100:" not in readme:
        if anchor in readme:
            readme = readme.replace(anchor, section + anchor, 1)
        else:
            readme = readme.rstrip("\n") + "\n\n" + section
        open("README.md", "w", encoding="utf-8").write(readme)
        print("readme updated", flush=True)
    else:
        readme = readme.replace("1905팩", str(total) + "팩")
        open("README.md", "w", encoding="utf-8").write(readme)

    log = open("docs/log.md", encoding="utf-8").read()
    if "A100:" not in log:
        entry = ("- 2026-11-16 A100: Low-Poly Halloween Kit, Wooden Overhang Modular Kit, Shield Spell"
                 "(3팩, catalog.csv " + str(total) + "행; 3D 2 + 2D 이펙트 1). 임시 GitHub Actions 워크플로(tmp-a100-*.yml)와 "
                 "파이썬 스크립트로 러너에서 OpenGameArt 원본 zip을 받아 팩 폴더 생성·커밋. 3D 2팩은 assets-3d-lowpoly-2, "
                 "이펙트 1팩은 assets-2d-pixel. 라이선스 CC0 1 + CC-BY 4.0 1 + CC-BY 3.0 1(출처 페이지 표기 확인). "
                 "7.9MB zip은 릴리스 v1.0 첨부, 3.1MB·0.48MB는 저장소 내 포함. 중복 검사는 assets-index.min.json 이름 대조로 스크립트에서 수행. "
                 "catalog.csv·README.md·docs/log.md만 수정(색인은 Actions 자동 갱신).\n")
        open("docs/log.md", "w", encoding="utf-8").write(log.rstrip("\n") + "\n" + entry)
        print("log updated", flush=True)

    sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" add catalog.csv README.md docs/log.md')
    sh('git -c user.name="sigco3111" -c user.email="sigco3111k@gmail.com" commit -m "카탈로그: A100 3팩 등록"')
    sh("git push origin HEAD:main")
    print("pushed", flush=True)


main()
