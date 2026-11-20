# 지원금픽 색인 정책 검증

- `index.html` 원본의 `noindex,nofollow`는 **미리보기 빌드**를 보호하는 의도된 설정이다. 제거하지 않는다.
- `tools/build.py --public-base https://kllollain-max.github.io/supportpick/`는 공개 빌드에서 `index,follow`로 바꾸며, 404/offline은 `noindex,follow`로 유지한다.
- `tests/test_search_metadata.py`는 공개 빌드의 색인 허용과 미리보기 빌드의 색인 차단을 각각 검사한다.
- 따라서 단순히 원본 메타태그를 수정하면 `indexing_policy_mismatch`로 실패한다.
- 배포가 실제로 공개 빌드 아티팩트(`dist`)를 사용하는지, 운영 주소의 HTTP 응답에서 메타태그가 무엇인지 별도 확인해야 한다.
- AdSense는 2026-11-09 사용자 제공 화면 기준 `kllollain-max.github.io` 검토 중. 승인 결과를 추정하지 않는다.
- 이 PR은 문서만 변경한다. 운영 배포·광고 스크립트·자동화 예약 변경 없음.
