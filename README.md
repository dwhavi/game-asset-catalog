# game-asset-catalog

다른 프로젝트에서 바로 가져다 쓸 수 있는 게임 에셋 도서관입니다.
CC0·CC-BY 등 **원본 재배포가 허용된 에셋 1,500여 종**을 유형별 저장소에 보관하고,
이 레포의 [catalog.csv](catalog.csv) 한 곳에 출처·라이선스·작가·태그를 정리했습니다.

> 이 레포는 [sigco3111/game-asset-catalog](https://github.com/sigco3111/game-asset-catalog)의 포크입니다.
> 수집 원칙과 출처 검증 기록은 원작자(sigco3111)의 작업을 그대로 계승합니다.

## 빠른 사용법

1. **찾기** — [catalog.csv](catalog.csv)에서 `name`·`tags`·`type`으로 검색 (또는 아래 웹 뷰어)
2. **받기** — 행의 `repo`와 `file`을 조합해 zip 다운로드 ([USAGE.md](USAGE.md)의 URL 규칙)
3. **표기** — `license`와 `attribution` 열대로 크레딧 기록 ([USAGE.md](USAGE.md)의 템플릿)

자세한 절차와 복사해서 쓰는 크레딧 템플릿은 **[USAGE.md](USAGE.md)**에 있습니다.

## 저장소 구성

에셋 파일 자체는 유형별 저장소(sigco3111 계정)에 있습니다. 이 카탈로그는 그 목록과 라이선스 장부입니다.

| 저장소 | 내용 | 수록 |
| --- | --- | --- |
| [assets-2d-pixel](https://github.com/sigco3111/assets-2d-pixel) | 2D 픽셀 스프라이트, 타일셋, 텍스처 | 69팩+ |
| [assets-3d-lowpoly](https://github.com/sigco3111/assets-3d-lowpoly) | 3D 로우폴리 모델·애니메이션 캐릭터 (GLB·OBJ) | 64팩+ (릴리스 첨부) |
| [assets-ui-icons](https://github.com/sigco3111/assets-ui-icons) | UI 키트, 아이콘, 폰트 | 13팩 |
| [assets-audio](https://github.com/sigco3111/assets-audio) | 효과음, 배경음악, 음성 (OGG) | 13팩 |
| [assets-2d-portraits](https://github.com/sigco3111/assets-2d-portraits) | 삼국지 수묵담채 초상화 (자체 제작, 조건 없이 사용 가능) | 1팩 (660장) |

각 저장소 README에 팩별 미리보기 이미지와 내용·형식·개수가 있습니다.

> 장기적으로 독립성을 높이려면 위 저장소들도 같은 방식으로 포크해 두면 됩니다.

## catalog.csv 스키마

한 행 = 한 에셋 팩(일부 팩은 파일 변형별로 2행). 현재 1,529행 / 1,511종.

| 열 | 설명 |
| --- | --- |
| name | 팩 이름 |
| repo | 파일이 있는 저장소 (위 5개 중 하나) |
| file | 저장소 안 경로. `releases/...`로 시작하면 릴리스 첨부, 아니면 저장소 루트의 zip |
| type | 유형 (2D, 3D 모델, 효과음, 음악, UI·아이콘, 2D 타일셋 등) |
| tags | 장르 태그 (fantasy, rpg, platformer, shooter, ui, audio 등) |
| author | 원작자 |
| source_url | 원본 배포 페이지 |
| license | CC0, CC-BY 3.0/4.0, MIT 등 |
| attribution | 크레딧 표기 문구. `optional:`(의무 아님) / `required:`(귀속 필수) 접두사 |
| added | 수록일 |
| notes | 내용·형식·개수, 검증 상태 |
| preview | 미리보기 이미지 URL |
| sample | 오디오 샘플 URL (오디오 팩) |
| split | 분할 ZIP의 파일 목록 (`;` 구분) |

## 수집 원칙

- 원본 파일 재배포가 명시적으로 허용된 라이선스(CC0, CC-BY)만 수록합니다.
- CC-BY 팩은 귀속 문구를 카탈로그에 함께 기록합니다.
- CC-BY-SA·GPL·CC-BY-NC, 개별 조건이 확인되지 않은 자료는 수록하지 않습니다.
- Unity Asset Store·Epic(Fab) 등 스토어 구매 에셋은 원본 재배포가 금지되는 경우가 많아 올리지 않습니다.
- 각 zip 안에 제작자 배포 원본 License.txt를 그대로 포함합니다. 원본에 라이선스 파일이 없는 팩은 원본 배포 페이지의 라이선스 표기를 근거로 수집자가 작성한 LICENSE-SOURCE.txt를 동봉하며, 원본 라이선스 파일과 구분합니다.

## 출처 검증 상태

- Kenney 팩(108개): kenney.nl의 CC0 배포 팩입니다. 원본 배포 페이지의 라이선스 조건과 각 팩 동봉 License.txt를 확인했습니다. 파일 바이트는 공식 미러 github.com/ETdoFresh/kenney.nl 에서 확보했으며, 공식 사이트 원본과 바이트 대조는 하지 않았습니다(kenney.nl 직접 다운로드 차단).
- KayKit 팩(10개): Kay Lousberg의 공식 GitHub 저장소(KayKit-Game-Assets) 원본 바이트를 그대로 보존했고, 동봉 LICENSE.txt(CC0)를 확인했습니다.
- Quaternius 팩(12개): quaternius.com 공식 배포 Google Drive 원본 바이트를 보존했고, 각 팩 페이지의 CC0 조건을 확인했습니다(Animated Zombie·Cute Monsters는 라이선스 미동봉으로 LICENSE-SOURCE.txt에 근거 기록).
- 저장소에 올라간 파일은 업로드 후 원격 다운로드 SHA-256을 로컬과 대조해 일치를 확인했습니다.

## 웹 뷰어

원본 카탈로그를 이미지로 둘러보는 사이트: https://sigco3111.github.io/game-asset-catalog/

`index.html`·`style.css`·`app.js`가 정적 뷰어이며, 원본 저장소의 `catalog.csv`를 읽어 표시합니다.
이 포크 기준의 뷰어를 쓰려면 Settings → Pages에서 `main` 브랜치를 배포하고, `app.js`의 CSV 주소를 이 레포로 바꾸면 됩니다.

### 새 팩을 추가할 때

뷰어는 `catalog.csv`에 기록된 팩만 보여줍니다. 새 팩을 올린 뒤 `catalog.csv`에 한 줄을 추가하면 됩니다.
`name`, `file`, `license`, `source_url`, `preview`가 비어 있으면 뷰어가 "확인 필요"로 표시하므로 수집 시 함께 기록합니다.

## 변경 이력 (원본)

- 2026-10-28: 3D 저장소에 잘못 분류돼 있던 7팩을 2D 저장소로 이동. Sci-Fi Essentials Kit 4K Textures도 2D 저장소(v6.0)로 이동.
- 3D 16팩, 오디오 4팩, UI 1팩(Game-icons.net SVG 4,180개, CC BY 3.0 귀속 필수), Quaternius 신규 16팩 추가. 상세는 원본 README 참조.
