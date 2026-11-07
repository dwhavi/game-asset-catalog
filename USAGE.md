# 사용 가이드 — 다른 프로젝트에서 에셋 가져다 쓰기

이 문서는 [catalog.csv](catalog.csv)에서 팩을 찾아 다운로드하고, 크레딧을 표기하는 절차를 정리합니다.

## 1. 팩 찾기

`catalog.csv`를 스프레드시트로 열거나 명령줄에서 검색합니다.

```bash
# 장르 태그로 찾기 (예: 판타지 RPG용 2D)
grep -i "fantasy" catalog.csv | grep "2D"

# 효과음만
awk -F, '$4 == "효과음"' catalog.csv
```

이미지로 둘러보려면 웹 뷰어(원본): https://sigco3111.github.io/game-asset-catalog/

찾은 행에서 이후 절차에 필요한 값은 `repo`, `file`, `license`, `attribution` 4개입니다.

## 2. 다운로드

`file` 열 값에 따라 URL이 두 가지 중 하나가 됩니다.

| `file` 값의 형태 | 다운로드 URL |
| --- | --- |
| `releases/download/<태그>/<파일>` (릴리스 첨부) | `https://github.com/sigco3111/<repo>/releases/download/<태그>/<파일>` |
| 그 외 (저장소 안의 zip) | `https://github.com/sigco3111/<repo>/raw/main/<file>` |

```bash
# 예시: Kenney Nature Kit (릴리스 첨부)
curl -L -O https://github.com/sigco3111/assets-3d-lowpoly/releases/download/v1.0/kenney_natureKit_2.1.zip

# 예시: 저장소 루트 zip
curl -L -O https://github.com/sigco3111/assets-2d-pixel/raw/main/kenney_microroguelike_1.2.zip
```

대용량 팩은 릴리스 첨부가 기본입니다. 저장소 전체를 받을 필요는 없습니다.

### 분할 ZIP 재결합

`split` 열이 있는 팩(일부 메가 킷)은 `.z01` + `.zip` 등 분할 파일을 모두 받은 뒤 합칩니다.

```bash
zip -s0 팩이름.zip --out full.zip
```

상세는 각 저장소 README의 재결합 안내를 따릅니다.

## 3. 라이선스 확인

사용 전 해당 행을 확인합니다.

- `license = CC0` — 귀속 표기 의무 없음. 표기하면 좋습니다.
- `license = CC-BY 3.0 / 4.0` — **귀속 표기 필수**. `attribution` 열의 `required:` 뒤 문구를 그대로 사용합니다.
- 그 외(MIT 등) — `notes`와 zip 안의 원본 License.txt를 따릅니다.

각 zip에는 원본 License.txt(없으면 수집자 작성 LICENSE-SOURCE.txt)가 들어 있으니, 프로젝트에 에셋을 복사할 때 이 파일도 함께 보관하면 출처 추적이 쉽습니다.

## 4. 크레딧 표기

프로젝트 루트에 `ATTRIBUTION.md`(또는 크레딧 화면)를 두고 쓴 팩마다 한 줄씩 기록하는 방식을 권장합니다.

```markdown
| 에셋 팩 | 제작자 | 라이선스 | 원본 |
| --- | --- | --- | --- |
| Space Shooter Remastered | Kenney | CC0 | https://kenney.nl/assets/space-shooter-remastered |
| Fantasy Icon Pack by Ravenmore | ravenmore | CC-BY 3.0 | https://opengameart.org/... |
```

- CC0 팩은 `optional:` 문구 그대로 적거나 생략 가능.
- CC-BY 팩은 `required:` 문구를 **반드시** 게임 크레딧·배포 문서 등 사용자가 볼 수 있는 곳에 표기.
- 에셋을 수정한 경우 "원본을 수정했음"을 함께 표기 (CC-BY 요건).

## 5. 새 팩 추가 규칙 (카탈로그 유지)

1. 에셋 저장소(유형별)에 zip과 원본 License.txt를 올립니다.
2. `catalog.csv`에 한 행을 추가합니다. `name`, `file`, `license`, `source_url`, `preview`는 필수입니다.
3. 라이선스가 CC0/CC-BY(또는 그에 준해 재배포 허용)인지 먼저 확인합니다. 조건이 불명확하면 수록하지 않습니다.
