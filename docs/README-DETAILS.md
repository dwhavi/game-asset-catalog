# README 상세 (정리 전 원문 섹션)

README 정리(2026-11-17) 때 README에서 옮긴 원문 섹션입니다. 내용은 바꾸지 않았습니다.

## 수집 원칙

- 원본 파일 재배포가 명시적으로 허용된 라이선스(CC0, CC-BY, MIT, GPL)만 수록합니다. GPL은 원본이 밝힌 GPL-2.0·GPL-3.0 등 계열을 그대로 따릅니다(2026-11-08 A15 규칙 변경: 이전에는 CC0·CC-BY만 허용).
- CC-BY·MIT·GPL 팩은 귀속·저작권 표기와 조건을 catalog.csv의 attribution·notes 열에 함께 기록합니다.
- 카피레프트 안내: GPL 에셋은 원본 GPL 라이선스를 그대로 유지합니다. 에셋을 가져다 쓰는 사람이 재배포할 때는 GPL 조건(라이선스 고지, 소스 공개 등)을 따라야 합니다.
- MIT·GPL 팩은 라이선스 전문 파일(License.txt 또는 LICENSE-SOURCE.txt)을 팩 폴더 또는 zip에 반드시 둡니다.
- CC-BY-NC 등 NC/ND, 개별 조건이 확인되지 않은 자료는 수록하지 않습니다. CC-BY-SA도 수록하지 않지만, 에셋이 이중 라이선스로 GPL 등 허용 라이선스를 명시적으로 제공하면 그 허용 라이선스를 선택해 기록합니다.
- Unity Asset Store·Epic(Fab) 등 스토어 구매 에셋은 원본 재배포가 금지되는 경우가 많아 올리지 않습니다.
- 각 zip 안에 제작자 배포 원본 License.txt를 그대로 포함합니다. 원본에 라이선스 파일이 없는 팩은 원본 배포 페이지의 라이선스 표기를 근거로 수집자가 작성한 LICENSE-SOURCE.txt를 동봉하며, 원본 라이선스 파일과 구분합니다.

## 카탈로그

전체 목록은 [catalog.csv](catalog.csv)를 참고하세요. 장르는 tags 열로 검색합니다 (fantasy, rpg, platformer, towerdefense, shooter, ui, audio 등).
에셋이 늘어나면 장르별 저장소로 다시 나눌 수 있습니다.

## 에셋 도서관 사이트

https://sigco3111.github.io/game-asset-catalog/

에셋 하나하나를 검색·필터·미리보기로 찾는 정적 사이트입니다(바닐라 JS, 외부 라이브러리·CDN·추적기 없음). [`assets-index.min.json`](assets-index.min.json)을 불러와 보여주며, 이 파일을 읽지 못하면 `catalog.csv`로 대신합니다. 머리글의 전체·저장소별 개수는 색인에서 그때그때 계산하므로 숫자를 따로 고칠 필요가 없습니다. 사이트 파일은 `index.html`, `style.css`, `app.js`입니다.

### 기능

- 검색: 이름·태그·제작자·메모·효과 종류를 대소문자 구분 없이 한국어·영어로 찾고, 여러 단어는 모두 포함(AND)한 것만 보여줍니다. 입력이 멈추면 반영(디바운스)되며, 한국어 낱말(폭발, 마법, 던전 등)은 영어 태그로도 찾습니다.
- 필터: 저장소(2D·3D·UI·오디오·초상화), 분류, 라이선스 계열, 제작자, 효과 칩 14종(타격·충격, 마법, 폭발, 번개, 불, 얼음, 바람, 치유, 레이저, 입자, 연기, 오라, 투사체, 베기; 여러 개를 고르면 하나라도 해당하는 것), '표기 필요 없는 것만', 'AI 생성 제외'.
- 정렬: 최근 추가(기본), 이름, 종류.
- 결과 수, 적용 중인 조건 요약, 초기화 버튼. 결과는 60개씩 표시하고 '더 보기'로 이어서 봅니다.
- 카드: 분류·라이선스 배지(전체 라이선스 문구와 `license_note`는 마우스를 올리거나 '상세'에서 확인), '표기 필요'/'표기 불필요', AI 생성 표시, 제작자, 태그 5개까지, 추가일, 출처 링크, 다운로드 링크(분할 업로드는 조각 목록), 지연 로딩 미리보기(클릭하면 확대), '상세'(메모·파일 경로·표기 문구·오디오 샘플).
- '크레딧 복사': `"이름" by 제작자 — 출처 — 라이선스` 형식 한 줄을 복사합니다. 표기가 필수가 아닌 에셋(CC0 등)에는 `(표기 선택)`이 붙습니다. '링크 복사': 그 에셋을 바로 찾는 주소(`?q=이름`)를 복사합니다.
- 초상화 탭에서는 팩 안의 인물을 이름으로 검색할 수 있습니다: 확정 한국어명과 한자명으로 찾고, 한국어명이 확정되지 않은 204명은 '미정'으로 표시되어 '미정' 검색으로 모아볼 수 있습니다. 결과는 60명씩 표시되고 '더 보기'로 전체를 탐색하며, 인물별 썸네일 미리보기와 개별 원본 다운로드(릴리스 개별 에셋)를 제공합니다.
- 접근성·모바일: 키보드로 모든 버튼 사용, 포커스 표시, 360px 너비까지 한 열로 맞춤.

### 주소 파라미터

화면 상태는 주소에 담겨 새로고침·공유해도 그대로 복원됩니다. 기본값인 항목은 주소에서 빠집니다.

| 파라미터 | 값 |
| --- | --- |
| `q` | 검색어(공백으로 여러 단어) |
| `cat` | 분류: `effect`, `sfx`, `music`, `voice`, `tileset-2d`, `sprite-2d`, `background-2d`, `map-2d`, `ui`, `icon`, `portrait`, `font`, `texture`, `model-3d`, `character-3d`, `vehicle-3d`, `building-3d`, `board`, `puzzle`, `other` |
| `repo` | 저장소: `2d`, `3d`, `ui`, `audio`, `portrait` |
| `lic` | 라이선스 계열: `cc0`, `cc-by`, `mit`, `gpl`, `other` |
| `fx` | 효과 종류(쉼표로 여러 개): `hit`(타격·충격), `magic`, `explosion`, `lightning`, `fire`, `ice`, `wind`, `heal`, `laser`, `particle`, `smoke`, `aura`, `projectile`, `slash` |
| `sort` | `name`(이름), `type`(종류). 생략하면 최근 추가 |
| `author` | 제작자 이름(정확히 일치) |
| `noattr` | `1`이면 표기 필요 없는 것만 |
| `ai` | `0`이면 AI 생성 제외 |

예: `?q=explosion&repo=audio&lic=cc0&fx=explosion&sort=name`

### 색인과 에이전트용 검색

`catalog.csv`가 원본이고, 사이트와 에이전트는 여기서 만든 색인을 읽습니다.

- [`assets-index.json`](assets-index.json): 에이전트가 검색하도록 만든 색인(전체 필드). 같은 내용을 공백 없이 줄인 [`assets-index.min.json`](assets-index.min.json)(약 2MB)을 사이트가 읽습니다.
- 필드: `id, name, repo, file, type, category, tags[], effect_kind[], author, source_url, license, license_family, license_note, attribution, attribution_required, ai_generated, added, notes, preview, sample, multipart, split_parts, download_path, download_url, download_urls`.
- 미리보기 주소: `preview`가 `previews/…` 또는 `<폴더>/…`이면 `https://raw.githubusercontent.com/sigco3111/<repo>/main/<preview>`, `releases/download/…`이면 `https://github.com/sigco3111/<repo>/<preview>`, `https://`로 시작하면 그대로 씁니다. 비어 있으면(대부분 오디오) 아이콘으로 대신 보여줍니다.

### 새 에셋을 추가할 때

1. 에셋을 올리고 `catalog.csv`에 한 줄을 추가합니다. 열은 `name, repo, file, type, tags, author, source_url, license, attribution, added, notes, preview, sample, split`이며, `preview`는 미리보기 이미지 주소, `sample`은 오디오 샘플 주소, `split`은 분할 ZIP이면 조각 파일 목록입니다.
2. 저장소 루트에서 `python3 tools/build_index.py`로 색인을 다시 만듭니다. 결과는 `assets-index.json`, `assets-index.min.json`, `docs/index-report.md`입니다(자세한 사용법은 [`tools/README.md`](tools/README.md)).
3. `catalog.csv`와 새 색인 파일을 커밋하면 약 1분 안에 사이트에 반영됩니다. 사이트 코드는 고칠 필요가 없습니다.

`catalog.csv`와 색인이 어긋나면 사이트는 색인 기준으로 보여주므로, 색인을 다시 만드는 것을 잊지 마세요.

## 위키와 에이전트용 정보

사람과 AI 에이전트가 에셋을 주제별로 찾고 라이선스·표기 규칙을 확인하도록 만든 문서입니다.

- [위키 홈](docs/wiki/README.md): 효과 종류·분류별 모음, [라이선스 정리](docs/wiki/licenses.md), [최근 추가](docs/wiki/recent.md). `python3 tools/build_wiki.py`가 `assets-index.json`에서 자동 생성합니다.
- [llms.txt](llms.txt): AI 에이전트용 안내(색인 주소, 검색 방법, 라이선스 규칙, 기록 방법).
- [사용 장부](docs/wiki/usage-ledger.md): 어느 프로젝트가 어떤 에셋을 가져다 썼는지 손으로 기록합니다.

## 자동 갱신과 용량 관리

- 자동 갱신: `catalog.csv`, `tools/build_index.py`, `tools/build_wiki.py`가 바뀌어 main에 올라가면 GitHub Actions(`.github/workflows/rebuild-index.yml`)가 색인(`assets-index.json`, `assets-index.min.json`), `docs/index-report.md`, 위키(`docs/wiki/`), `llms.txt`를 다시 만들고, 달라진 것이 있을 때만 `색인: 자동 갱신 (catalog.csv 변경)`으로 커밋합니다. Actions 탭에서 수동으로도 실행할 수 있습니다.
- 용량 점검: `.github/workflows/capacity-check.yml`이 매주 월요일 에셋 저장소 5곳의 용량을 확인해 `docs/capacity-report.md`를 갱신합니다.
- 수동 명령(저장소 루트): `python3 tools/build_index.py`, `python3 tools/build_wiki.py`, `python3 tools/check_sizes.py`
- 용량 기준과 분리 규칙: [docs/capacity.md](docs/capacity.md), 최신 용량 표: [docs/capacity-report.md](docs/capacity-report.md)
