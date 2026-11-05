# AdSense 신청 준비 추가 개선 · 2026-11-05

판정: **신청 보류**. 공개 접근 검사와 신청 준비, Google의 실제 승인은 별개다. 이번 변경은 PR 검토본이며 병합·공개 배포·심사 제출·광고 요청은 실행하지 않았다.

## 도메인 및 공식 기준

- AdSense 등록 주소: `https://kllollain-max.github.io` (공통 호스트 한 항목). `/careerpick/`, `/supportpick/`는 별도 사이트 등록 주소가 아니다. 두 프로젝트의 저장소·데이터·배포는 독립 유지한다.
- Google은 PSL 플랫폼 하위 도메인 등록을 허용한다. 공식 PSL에 github.io가 있다. 루트는 두 서비스 안내, 실제 계정 메타와 ads.txt가 공개되어 있다. 기존 계정의 소유확인 완료 표시는 과거 직접 확인 기록이며 이번에는 로그인 화면을 재검사하지 않았다.
- 독립 도메인은 선택 사항이다. 각각의 브랜드·심사를 분리할 수 있지만 구매·DNS·이전·canonical·기록 이전 비용과 검증이 따른다. 현재 공통 호스트로 먼저 준비할 수 있으므로 구매를 제안하거나 실행하지 않는다. 향후 독립 등록이 필요할 때 도메인 확정 후 승인한다.
- 루트 robots.txt·ads.txt는 `kllollain-max/kllollain-max.github.io`가 관리한다. 프로젝트 아래 ads.txt/robots.txt로 대체하지 않는다. 이번 두 PR에서 루트 저장소는 변경하지 않았다. 공유 호스트 파일은 두 서비스가 함께 영향을 받는다.
- 가치 있는 독자 콘텐츠·기만 방지·저작권·실제 처리에 맞는 개인정보 공개는 정책 준수 항목이다. 소개·문의·이용약관·사이트맵·Search Console 등록을 모두 일률적인 AdSense 필수 페이지라고 주장하지 않는다. 실제 광고 도입 전 지역·광고 설정에 맞는 동의/CMP와 개인정보 안내가 필요하다.
- 공식 근거: https://support.google.com/adsense/answer/12170421 · https://support.google.com/adsense/answer/2784438 · https://publicsuffix.org/list/public_suffix_list.dat · https://support.google.com/adsense/answer/7584263 · https://support.google.com/adsense/answer/7679060 · https://support.google.com/publisherpolicies/answer/11190248 · https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

## 실제 추가 구현

`check_public_readiness.py`는 고정된 공개 호스트의 HTML/XML/TXT/JSON만 조회한다. 리디렉션을 따라가지 않고 JS·광고·SDK·외부 블로그를 실행하지 않는다. 루트의 게시자 메타와 ads.txt 일치, 사이트맵 범위·중복, 주요 정책·본문 페이지 canonical·noindex·H1, Google/광고 크롤러 robots 규칙을 검사한다. 공개 응답 해시를 영수증에 남긴다. 0=관찰 범위 통과, 1=오류, 2=미확인으로 실패를 숨기지 않는다. 읽기 전용 정기/배포 후 검사를 준비했으며 병합 전 운영 자동화로 간주하지 않는다.

검사에는 `none`(noindex,nofollow 동의어), Googlebot 전용 메타, 중복 메타와 HTTP 응답 차단 회귀를 추가했다. `max-image-preview:none`을 전체 색인 차단으로 오인하지 않는 사례도 검사한다. 이는 검사 누락 수정이며, 현재 운영 사이트의 색인 차단이 발견됐다는 뜻이 아니다.

## 보존·한계와 최종 적용

수집 원본·ID·사용자 기록 키·SNS 발행·웹푸시·R2 설정을 변경하지 않았다. 실제 수집·발송·구독·계약·결제·삭제를 실행하지 않았다. 기존 R2 PR #26은 실제 연결 증거가 별도로 필요하며 이번 점검으로 장기 백업 성공을 선언하지 않는다. main Git 이력과 보존 아티팩트는 유지된다. 신규 유료 자원 생성 없음.

이번에 실제 Android Chrome/휴대전화 설치·Core Web Vitals 현장 자료를 새로 측정하지 않았다. 기존 Chromium 크기별 검증은 과거 자료로만 재사용하고 실기기 검사로 확대하지 않는다. Search Console 제출·가져오기·발견·크롤링·색인 상태는 이번 HTTP 조회로 확정하지 않는다. 기존 홈 색인 관찰 기록이 전체 본문 색인을 뜻하지 않는다.

최종 순서: PR 후보 CI 확인 → 운영자 본문 검토·실제 개인정보 처리 확인 → 이 PR 두 개의 병합·공개 배포 승인 → 최신 main·최신 정상 자료로 배포 → 공개 변경·기능 재검증 → 공통 호스트 AdSense 검토 요청 승인·실행. 실제 광고 활성화는 동의/배치 구현 후 별도로 검증한다. 승인 가능성을 콘텐츠 개수나 검사 수로 보장하지 않는다.

되돌리기는 승인 PR의 공개/검사 변경만 역커밋한다. 전체 main을 과거로 되돌리거나 새 수집 자료·원장·개인 기록을 덮어쓰지 않는다.

## 지원금픽 결과

- 기존 PR #28을 재사용한다. privacy.html의 복구 사본 삭제 한계 안내를 유지한다. 별도 PR #26 운영/R2 개선은 병합하지 않았다.
- 추가: `tools/check_public_readiness.py`, `tests/test_public_readiness.py`, `.github/workflows/public-readiness-check.yml`. 수정: `tools/verify_release.py`, `tests/test_release_network.py`, `guides.json`, 검토 reader/manifest.
- 콘텐츠: 신규 0편, 기존 내일배움카드 해설 1편 보강. 훈련기관·일정·훈련비·본인부담을 과정별로 기록하는 자체 준비 FAQ를 추가했다. 금액·자격을 새로 추정하지 않고 reviewedAt·validUntil·sourceHash를 유지했다. 후보 본문 해시/reader를 갱신했다. 사람 검토 0/20·대기.
- 공개 사이트맵 11,050 URL, 대표 페이지와 root 포함 13개 응답 HTTP 200. 해시를 공개 manifest와 대조했고 세대 `gov24-41921889569-1`, 자료 10,942개, 해설 20개, 블로그 5개다. 검사 전후 manifest가 동일했다. 전체 11,050개의 오늘 네트워크 전수 조회라는 뜻은 아니다.
- 공개 sourceRevision `a890695ccaf14ccea374710d5182030f0cfbd4b1`, main `0db83684355af1f08f56ddac6461588dfc0bce39`. 공개 원본/코드 SHA와 현재 main은 구분한다. 관련 운영 배포 https://github.com/kllollain-max/supportpick/actions/runs/41921889569 의 실패·세대 검증 보완은 PR #26 참조. 이번에는 실제 공개 manifest를 확인했고 신규 배포는 없다.
- 로컬 Python 98개, Node 56개 통과. 새 Python 회귀 9개. 독립 bootstrap 재빌드 상세 10,942 / 보류 7 / 자체 해설 20 / 블로그 6 / 사이트맵 11,050 로컬 전체 검사 통과. bootstrap 세대 `gov24-41774386414-1`은 QA 전용이며 운영에 배포하지 않는다.
- 첫 로컬 빌드는 기존 collection-state의 manifest에 없는 임시 파일로 파일집합 검사가 실패했다. 실패 상태를 보존하고 무결성 검사를 변경하지 않은 채, SHA가 검증된 기존 ZIP을 독립 임시 폴더에서 복원하여 재빌드했다. 후속 검사에서 사이트맵 11,050/11,050 통과. 운영 자료를 수정한 조치가 아니다.
- 새 일일 점검 예정 07:35 KST, 승인 배포/정기운영 완료 후 추가 점검. 공개 manifest의 대표 파일 해시·세대를 검증하며 검사 중 배포가 바뀌면 미확인으로 종료한다. 기존 정상 수집/Threads/블로그 일정은 유지한다. 병합 전 미활성.
- 남음: 실제 사람 검토, 개인정보 실제 운영 확인, 현재 접수·개인 자격은 공식 창구 확인, PR #26의 R2 실연결·복원 증거와 공개 반영 장벽 적용 승인, 실기기·성능·최신 Search Console 확인. 사이트맵 제출이나 이번 HTTP 성공을 색인/AdSense 승인으로 표기하지 않는다.
