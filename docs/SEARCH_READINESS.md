# 지원금픽 검색·공유 준비

## 이번 변경

- 공개 빌드에서 홈페이지·정보 출처·개인정보 안내 3개 실제 HTML 주소를 `sitemap.xml`로 생성한다. `#benefit=...` 주소, JSON 조각, 임시 원고와 외부 네이버 글은 사이트맵에 넣지 않는다.
- 3개 페이지의 제목·설명·canonical·Open Graph·Twitter 미리보기를 맞춘다. 기존 정사각 배지 PNG를 그대로 사용하고 홈페이지에 WebSite JSON-LD를 넣는다.
- 미리보기 빌드는 `noindex,nofollow`를 유지한다. 실제 공개 빌드는 `index,follow`다.
- Google에서 지원금픽 URL 접두사 속성의 HTML 확인 태그를 발급받아 설정했다. 네이버 확인 값은 null이다. 공개 배포·소유확인 버튼·사이트맵 제출·색인 완료 상태는 각각 별도로 확인한다.
- 검색 정비처럼 코드만 수동 배포할 때도 최신 정상 운영 수집본을 먼저 복원한다. 서로 다른 워크플로의 실행 순번을 비교해 최신 자료를 건너뛰지 않으며, 최근 정상 상태를 조회할 수 없으면 초기 자료로 조용히 대체하지 않는다.

## Google Search Console

1. 소유자의 계정에서 URL 접두사 속성 `https://kllollain-max.github.io/supportpick/`를 추가한다. 커리어픽 속성의 등록 여부와 구분한다.
2. HTML 태그 방법에서 발급된 `google-site-verification`의 content 값만 `search-verification.json`의 google에 넣는다. 예시 값은 공개 빌드에 넣지 않는다.
3. 검증·승인된 사이트를 배포한 뒤 비로그인 홈페이지의 HTML 원문에서 태그가 나오는지 확인한다. 이후 Search Console에서 확인 버튼을 누른다.
4. 사이트맵에 `https://kllollain-max.github.io/supportpick/sitemap.xml`을 제출하고 홈페이지 URL 검사를 수행한다. 제출과 검색 결과 색인은 별도로 확인한다.

## 네이버 서치어드바이저

소유자의 계정과 실제 도구가 제시하는 등록 범위를 먼저 확인한다. 지원금픽이 `/supportpick/` 경로에서 운영되는 점과 같은 호스트의 커리어픽을 고려한다. 도구가 도메인 루트 소유확인을 요구하면 이 저장소에 태그를 넣는 것만으로는 확인되지 않을 수 있다. 루트 사이트 변경은 별도 범위로 처리하며 다른 사이트를 덮어쓰지 않는다.

해당 범위의 HTML 태그 확인이 가능한 경우 실제 `naver-site-verification` content 값을 naver에 넣고 배포 후 확인한다. 호스트 루트가 요구되는 경우에는 루트 운영 저장소·권한과 기존 확인 태그를 먼저 대조한다. 사이트맵은 도구가 허용하는 해당 사이트 범위에서 제출한다. 블로그 로그인·편집·발행은 이 작업에 포함하지 않는다.

## robots.txt와 상세 주소의 한계

`robots.txt`는 호스트 루트 `https://kllollain-max.github.io/robots.txt`에 있어야 한다. `/supportpick/robots.txt`를 만들어 검색로봇 설정이 완료됐다고 보고하지 않는다. 확인 당시 호스트 루트는 404였으며, 루트 사이트나 커리어픽 저장소는 이번 변경에서 수정하지 않는다. 사이트맵은 검색도구에 직접 제출할 수 있다.

현재 지원금 상세는 `#benefit=서비스ID`인 브라우저 내부 경로다. 이를 10,942개의 개별 검색 문서로 등록했다고 주장하지 않는다. 지원금별 검색 유입을 확대하려면 실제 HTML 응답을 제공하는 독립 주소와 제목·설명·canonical·공식 근거를 함께 설계해야 한다. 기존 저장·내 신청·해설 연결과 주소 호환성도 검증한 뒤 별도 구현한다.

## 근거

- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- https://developers.google.com/crawling/docs/robots-txt/create-robots-txt
- https://support.google.com/webmasters/answer/9008080
- https://searchadvisor.naver.com/guide/request-feed

## 복구

이 변경은 검색·공유용 빌드 산출물과 선택적인 소유확인 태그만 추가한다. 데이터 수집·기록 저장·Threads·블로그 원장과 예약은 수정하지 않는다. 이전 검증 커밋 `1fccc8877387cbe9d3025395ee14484f65f4c20e`와 정상 수집 상태로 빌드·배포하면 이전 표시로 되돌릴 수 있다. 소유확인을 실제 완료한 뒤에는 확인 태그 삭제가 소유권 유지에 미치는 영향을 먼저 확인한다.
