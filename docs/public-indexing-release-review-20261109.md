# 지원금픽 색인 정책 검토

- 현재 `index.html`은 미리보기 템플릿이므로 `noindex,nofollow`가 의도된 상태다.
- `tools/build.py`는 `public_base=https://kllollain-max.github.io/supportpick/`를 전달받은 공개 빌드에서만 `index,follow`로 전환하고 canonical·사이트맵을 생성한다.
- `tests/test_search_metadata.py`는 미리보기 비색인과 공개 빌드 색인 정책을 별도로 검증한다.
- 따라서 미리보기 원본의 robots 메타태그를 직접 수정하지 않는다. 공개 배포 여부, 빌드 인수, 배포 경로 및 실제 배포 아티팩트가 확인될 때까지 공개 전환을 보류한다.
- PR #50 최초 CI 실패 중 `indexing_policy_mismatch`는 원본 미리보기 메타태그를 변경해 발생했다. 별도 브라우저 CI 실패는 Playwright의 ubuntu26.04 Chromium 설치 미지원 문제로 구분한다.
- AdSense는 심사 중이며 이 문서는 광고 승인이나 운영 배포를 의미하지 않는다.
- 배포, 병합, 예약, 수집, Threads, 광고 코드는 변경하지 않는다.
