# 지원금별 해설 연결

홈페이지의 블로그·Threads 바로가기를 제거한다. 사이트 어느 화면에도 Threads 링크·배너·버튼을 추가하지 않는다. 스레드는 외부 유입 채널이며 각 지원금의 `?utm_source=threads&utm_medium=social&utm_campaign=benefit#benefit=서비스ID`로 연결한다.

## 실제 발행된 해설만 표시

- 카드: `신청방법 해설`, 상세: 공식 안내·신청 링크 아래 `지원금픽 해설 보기`.
- 발행된 `blog.naver.com/bible_el/숫자` 또는 `m.blog.naver.com/bible_el/숫자`만 허용한다. 블로그 첫 화면은 해설로 연결하지 않는다.
- 서비스 ID, 지역, 연도, 모집 차수와 원문의 제목·기관·지역·기간·요약·수정일을 특정한 sourceKey가 일치해야 한다. 제목 유사도로 연결하지 않는다.
- 원문 변경, 표본, 출처 불일치, 복수 연결 충돌, 검수 유효기간 경과 시 해설 버튼을 숨긴다. 확인 유효기간은 최대 30일이며, 발행글 삭제 여부를 실시간 감시한다고 주장하지 않는다.
- 원고 생성과 실제 네이버 발행은 별개다. 복사용 원고만 생성된 상태는 사이트 해설을 표시하지 않는다. 실제 발행 주소·발행 확인이 있어야 등록한다.
- 현재 레지스트리는 0건이다. 확인되지 않은 발행 URL이나 복사용 HTML을 대체 링크로 넣지 않는다.

## 원고 자동화와의 연결

지원금픽 원고 자동화는 다음 새 회차부터 `site-link.json`을 함께 제공한다. sourceKey는 이 저장소 editorials.js의 sourceKey 함수와 같은 JSON 문자열이며 최신 사이트 수집본의 해당 서비스 레코드로 만든다. 본문 하단에는 해당 지원금 상세 링크를 추가한다. 지원금 ID를 확정하지 못하면 제목으로 추정하지 않고 연결 보류로 표시한다.

기존 네이버 미접속·수동 발행 원칙을 유지한다. 자동화는 발행 URL을 만들어내거나 main에 쓰지 않는다. 사용자가 실제 발행 URL을 제공하면 지원금 ID·연도·모집 차수·지역·공식 정보 변경을 대조해 아래 절차로 등록할 수 있다. 현재 이 단계에는 사용자 발행 확인이 필요하며, 네이버 자동 감시/자동 발행이 연결된 상태는 아니다.

## 등록 절차

입력 JSON 필드:

- benefitId, title, url: 정확한 서비스 ID, 해설 제목, 실제 발행 URL
- sourceKey: editorials.js의 sourceKey(현재 서비스 레코드)
- scope: `{year: 2026, region: "현재 서비스의 region 값", round: "4분기 등 실제 차수"}`
- publishedAt, verifiedAt, validUntil: 시간대 포함 ISO 시각. 검수 기한은 verifiedAt 후 최대 30일
- publicationVerified: 실제 발행이 확인된 경우에만 true

`node tools/register-editorial.cjs --input site-link-published.json --feed dist/data.json --output editorials.json`

기존 해설은 삭제하지 않고 superseded로 보존하며, 새 해설과 검증 기록을 추가한다. 검증 후 사이트 빌드를 통해 editorial-data.js가 생성되며 원본 레지스트리/개발 스크립트/개인 기록은 공개하지 않는다. 이 단계의 등록과 PR 작성은 공개 배포와 별개이며 기존 배포 승인 절차를 따른다.
