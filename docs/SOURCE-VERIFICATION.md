# 출처 검증 상태와 추가 확장 기록

README 정리(2026-11-17) 때 README에서 그대로 옮긴 원문입니다.

## 출처 검증 상태

- Kenney 팩(108개): kenney.nl의 CC0 배포 팩입니다. 원본 배포 페이지의 라이선스 조건과 각 팩 동봉 License.txt를 확인했습니다. 파일 바이트는 공식 미러 github.com/ETdoFresh/kenney.nl 에서 확보했으며, 공식 사이트 원본과 바이트 대조는 하지 않았습니다(kenney.nl 직접 다운로드 차단).
- KayKit 팩(10개): Kay Lousberg의 공식 GitHub 저장소(KayKit-Game-Assets) 원본 바이트를 그대로 보존했고, 동봉 LICENSE.txt(CC0)를 확인했습니다.
- Quaternius 팩(12개): quaternius.com 공식 배포 Google Drive 원본 바이트를 보존했고, 각 팩 페이지의 CC0 조건을 확인했습니다(Animated Zombie·Cute Monsters는 라이선스 미동봉으로 LICENSE-SOURCE.txt에 근거 기록).
- 저장소에 올라간 파일은 업로드 후 원격 다운로드 SHA-256을 로컬과 대조해 일치를 확인했습니다.

## 추가 확장 (총 159팩)

- 3D 16팩 추가: 식재료, 작물, 주택 실내, 모듈식 던전·SF 환경·도로, 자연, 터렛, 무기, NPC, 물고기, 선박. 실제 OBJ 파일 860개 및 대응 FBX·BLEND를 확인했습니다(형식별 중복 합산 아님). Food·Crops 사이 Coconut_Half OBJ 1개는 원본 공통 파일입니다.
- 오디오 4팩 추가: 효과음 390종, 총 720개 형식별 오디오 파일 디코딩 검사 완료.
- UI 1팩 추가: Game-icons.net SVG 4,180개. CC BY 3.0 귀속 필수이며, 원본 license.txt에 CC0로 표시된 2명 제작자 폴더는 예외입니다.
- Quaternius 신규 16팩은 제작자의 OpenGameArt 배포 페이지에서 받았습니다. 기존 Drive 배포본과 바이트 대조를 했다는 뜻은 아닙니다. 동봉 원본 라이선스가 없는 팩은 출처 페이지의 CC0 표기를 근거로 수집자 LICENSE-SOURCE.txt를 추가했습니다.
- 새 파일 모두 원격 다운로드 SHA-256 확인. Low Poly Nature Pack은 .z01+.zip 2개 분할이며 원격 파일 재결합과 내용 일치 검사를 마쳤습니다. README의 재결합 명령을 따르세요.
- v6.0(2026-10-28): Quaternius 제작자 OpenGameArt 배포 7팩 추가 — Fantasy Props MegaKit(모델 94종), Medieval Village MegaKit(176종), Modular Sci-Fi MegaKit(191종), Stylized Nature MegaKit(68종), Sci-Fi Essentials Kit 모델(37종), Universal Animation Library 1·2. 모두 11MB 분할 zip이며 49개 파일 원격 SHA-256 일치 확인. Sci-Fi Essentials 4K 텍스처(PNG 36종)는 2D 저장소 v6.0에 수록.
