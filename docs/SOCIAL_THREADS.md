# 지원금픽 사이트·블로그·Threads 연동

대상: `kllollain-max/supportpick`, Threads `@hid_1004`, 네이버 `bible_el`.

## 구현 범위

- 홈페이지에는 Threads 링크/버튼/배너/푸터를 두지 않는다. 블로그는 지원금별 검증된 해설로만 연결한다.
- 커리어픽 main `ea7b62fc6642b2bfa421da1d55c44a13141d6079`의 08·12·16·20시(KST), 본문 + 상세 답글 + 홈페이지/블로그 안내 답글, 계정 검증, 선예약, 중복 차단 원칙을 지원정보용으로 적용했다.
- 최신 무결성 검증 수집본의 상세 자료를 사용한다. 24시간 초과·미래 수집시각·표본·미래/만료 기간·취소/철회/종료·출처 상충 자료는 제외한다. 원문의 기한을 현재 접수 가능 증거로 사용하지 않는다.
- 본문은 혜택명·목적·기관·관련 태그, 첫 답글은 대상/기간/방법 요약과 공식 원문, 둘째 답글은 해당 지원금 상세 화면(#benefit=서비스ID)으로 연결한다. UTM은 Threads 유입을 구분한다. 요약은 원문 전체 조건을 대신하지 않는다. 원문 링크가 너무 길면 자르지 않고 해당 실행을 실패 처리한다.
- 사이트 해설은 실제 발행된 글만 editorials.json으로 연결하며 임시저장 원고는 제외한다. 사이트에 스레드를 노출하지 않는다. 스레드는 사이트 상세로 보내는 외부 유입 채널이다.
- 전용 영구 원장에 SHA 조건부 쓰기를 성공한 뒤에만 게시한다. 본문·답글마다 보내기 전 상태와 응답 ID를 보존한다. 타임아웃·영수증 기록 실패·실제 게시 조회 실패·답글 일부 실패는 `pending`으로 보존하고 다음 회차도 차단한다. 기존 게시물은 재게시하지 않는다.
- 당일 최대 본문 4건. 예약 지연 허용 2시간, 수동 즉시 게시·실행 재시도·지난 회차 소급 게시는 금지한다.
- 성공/건너뜀/실패 결과를 Actions 요약과 아티팩트로 제공한다. 인증·수집·원장 실패는 게시 성공으로 보고하지 않는다.

## 활성화 전에 필요한 실제 설정

현재 변경은 검토용 PR이며 main 병합·Pages 배포·실제 게시·운영변수 변경은 하지 않는다.

1. 이 PR의 검사 결과를 확인한 뒤 별도 승인된 커밋을 병합하고 기존 승인 SHA 배포 절차로 홈페이지를 배포한다.
2. 지원금픽 계정으로 Meta Threads 권한 `threads_basic`, `threads_content_publish`가 있는 토큰을 발급한다. 토큰 원문은 대화나 소스에 넣지 않는다.
3. **지원금픽 저장소 전용** Secrets: `SUPPORTPICK_THREADS_ACCESS_TOKEN`, `SUPPORTPICK_THREADS_USER_ID`를 등록한다. 커리어픽 인증정보를 복사하지 않는다.
4. 병합 후 `supportpick-threads-state` 브랜치를 만든다. `social/threads-state.initial.json`을 그 브랜치의 `social/threads-state.json`으로 복사해 초기 원장으로 한 번만 커밋한다. 초기화 전 `@hid_1004`의 다른 게시기가 중지됐는지와 기존 게시 이력 대조를 확인한다. 이전 지원금픽 게시물이 있으면 해당 혜택 ID·게시/답글 영수증을 대조해 원장에 포함한다. 이미 존재하는 원장을 초기 파일로 덮어쓰지 않는다.
5. workflow_dispatch의 `preview` 및 `check-account`를 실행한다. 두 모드는 게시하지 않는다. 계정명은 코드의 `hid_1004`와 Secret의 숫자 ID를 모두 대조한다.
6. 실제 게시 활성화 승인 후 Variables `SUPPORTPICK_THREADS_CUTOVER_READY=true`, `SUPPORTPICK_THREADS_ENABLED=true`를 설정한다. 하나라도 없으면 예약 게시는 동작하지 않는다.
7. 첫 자연 예약 회차의 본문·답글 2개 실제 ID와 조회 검증을 확인한다. GitHub 예약 시각은 실행 대기 때문에 지연될 수 있다.

설정 주소: https://github.com/kllollain-max/supportpick/settings/secrets/actions

예약 결과: https://github.com/kllollain-max/supportpick/actions/workflows/supportpick-threads.yml

## 이미지·블로그 원고 연결

`social/assets.json`은 혜택 ID별 선택적 이미지 자료다. 게시글의 블로그 주소는 사이트 해설 레지스트리를 사용하며 스레드 유입 링크는 지원금 상세로 고정한다. 예:

```json
{
  "서비스ID": {
    "publishedBlogUrl": "https://blog.naver.com/bible_el/실제숫자게시물번호",
    "imageUrl": "https://raw.githubusercontent.com/kllollain-max/supportpick/main/social/images/benefit.jpg"
  }
}
```

실제 공개된 글과 검수 완료 대표이미지만 등록한다. 첫 회차 텍스트, 다음 회차 이미지 순서로 교대하며 이미지가 등록되지 않은 경우 텍스트로 제공한다. 자동으로 낮은 품질의 대체 이미지를 생성하지 않는다. 현재 assets는 비어 있어 이미지 자동 재사용·새 이미지 자동 제작까지 연결됐다고 주장하지 않는다. 기존 블로그 원고 자동화의 승인 코드·프롬프트·예약은 변경하지 않는다.

## 프로필과 블로그에 넣을 링크

네이버에는 접속하지 않는다. 블로그 소개/배너와 Threads 프로필의 링크는 계정 소유자가 아래 주소를 등록하면 역방향 연결이 완성된다. 이번 PR이 프로필 자체를 수정하지는 않는다.

- 홈페이지: https://kllollain-max.github.io/supportpick/
- 스레드: https://www.threads.com/@hid_1004
- 블로그: https://blog.naver.com/bible_el

소개문: `지원금·생활혜택을 공식 출처로 쉽게 안내합니다. 대상·기간·신청방법은 지원금픽에서 확인하세요.`

## 장애 처리

실패 시 가장 최근 원장 레코드의 stage와 main_id/detail_id/links_id 및 Actions 로그의 영수증을 대조한다. 토큰 만료·계정 불일치·수집 지연은 원인을 해결하되 기존 pending 기록을 삭제하거나 재발행하지 않는다. 게시 응답이 불명확하면 원격 계정에서 원문과 실제 게시 ID를 확인한 후 사람이 원장을 복구한다. 실제 게시가 없다는 증거 없이 초기화·잠금 해제하지 않는다. 복구 후 계정 확인·preview·검사를 다시 통과시키고 다음 신규 회차만 진행한다.

참고한 공식 API 자료: https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api

개발자 문서: https://developers.facebook.com/docs/threads/posts
