# 저장소 용량 점검 보고서

생성: 2026-11-23 14:19 KST (`python3 tools/check_sizes.py`, 매주 월요일 자동 갱신)

| 저장소 | 용량(MB) | 상태 | 900MB까지 남은 용량(MB) |
| --- | ---: | --- | ---: |
| assets-2d-pixel | 486.6 | 양호 | 413.4 |
| assets-audio | 500.4 | 양호 | 399.6 |
| assets-3d-lowpoly | 666.9 | 양호 | 233.1 |
| assets-3d-lowpoly-2 | 507.2 | 양호 | 392.8 |
| assets-ui-icons | 90.8 | 양호 | 809.2 |
| assets-2d-portraits | 50.8 | 양호 | 849.2 |
| assets-code | 17.8 | 양호 | 882.2 |
| assets-3d-polyfork | 5.8 | 양호 | 894.2 |

5개 저장소 합계: 2,326.2MB (저장소별로 판단하며 합계는 참고용입니다).

## 판정 규칙

- 양호: 700MB 미만
- 주의: 700MB 이상
- 분리 준비: 850MB 이상 (다음 저장소 `assets-<종류>-2` 준비)
- 추가 중단: 900MB 이상 (그 저장소에는 새 팩을 올리지 않음)

용량은 GitHub API의 `size`(KB)를 1024로 나눈 값입니다. 릴리스 첨부 파일은 포함되지 않습니다. 자세한 정책은 [capacity.md](capacity.md)를 참고하세요.
