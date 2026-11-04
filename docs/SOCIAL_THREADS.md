# 지원금픽 Threads 운영

대상: `kllollain-max/supportpick`, Threads `@hid_1004`.

## 2026-11-04 요청 적용

- 본문과 답글의 마지막 문구는 **자세한 사항은 프로필링크 확인**으로 통일한다.
- 유입 경로는 Threads → 프로필링크 → 지원금픽이다. 게시물에 블로그 첫 화면이나 별도 홈페이지 홍보 링크를 추가하지 않는다. 첫 답글의 공식 출처 링크는 사실 확인용으로 유지한다.
- 프로필 링크의 목표 주소는 `https://kllollain-max.github.io/supportpick/?utm_source=threads&utm_medium=social&utm_content=link_in_bio`이다. 기존 Facebook 클릭 식별자는 보존할 필요가 없다. API 출력의 `profile_link_target`은 설정할 목표이며, 실제 프로필 등록 여부를 검증했다는 뜻은 아니다.
- 본문은 혜택명·기관·요약·관련 태그, 첫 답글은 대상·기간·방법·공식 출처, 둘째 답글은 프로필링크에서 혜택명을 검색하고 저장하도록 안내한다.
- 커리어픽과 같은 08·12·16·20시(KST) 네 회차, 계정 대조, 선예약, 중복 차단, 원격 조회 검증을 사용한다. 지원금픽의 인증정보·원장·동시실행 잠금은 독립적이다.
- 사이트에 Threads를 표시하는 변경이나 네이버 접속은 이 변경의 범위에 포함하지 않는다. 기존 블로그 원고 자동화도 변경하지 않는다.

## 게시 조건과 중복 보호

최신 완전 수집본과 개별 확인시각이 모두 24시간 이내인 자료만 게시한다. 표본·미래/만료 기간·취소/철회/종료·출처 상충 자료를 제외한다. 자료가 없거나 오래되면 `skipped`로 보고하며 최신으로 위장하지 않는다. 자격·선정·현재 접수 가능 여부를 보장하지 않는다.

영구 원장은 `supportpick-threads-state` 브랜치의 `social/threads-state.json`이다. SHA 조건부 예약을 기록한 뒤에만 게시한다. 본문·답글마다 전송 전 단계·응답 ID·실제 게시 조회 결과를 보존한다. 타임아웃, 응답 저장 실패, 일부 답글 실패는 `pending`으로 유지하고 이후 게시를 차단한다. 원장을 삭제하거나 초기화해서 재발행하지 않는다.

예약 지연 허용은 두 시간이다. 놓친 회차를 소급 게시하지 않는다. 수동 `publish-one-now`는 현재 분을 새 슬롯으로 한 건만 게시하며, 동일한 원장·중복 차단·하루 최대 본문 네 건 제한을 적용한다. 수동 게시도 당일 한도에 포함된다. 실행 재시도(run attempt > 1), 타 저장소, main 외 브랜치, preview/check-account 모드에서의 게시를 차단한다.

## 설정과 실행

전용 Secrets:

- `SUPPORTPICK_THREADS_ACCESS_TOKEN`: 지원금픽 계정의 Threads 인증정보
- `SUPPORTPICK_THREADS_USER_ID`: 지원금픽 계정의 숫자 ID
- `SUPPORTPICK_GOV24_SERVICE_KEY`: 보조금24 자료를 자동 갱신할 때 필요한 별도 API 키

게시 변수 두 개를 모두 `true`로 설정해야 한다.

- `SUPPORTPICK_THREADS_CUTOVER_READY`
- `SUPPORTPICK_THREADS_ENABLED`

기존 지원금픽 게시기와 게시 이력을 먼저 대조한다. 원장이 존재하지 않는 경우에만 `social/threads-state.initial.json`을 전용 브랜치의 `social/threads-state.json`으로 한 번 복사한다. 기존 원장이 있으면 절대 덮어쓰지 않는다.

워크플로 `supportpick-threads.yml`:

1. `check-account`: 계정명과 ID 확인 및 최근 게시물 최대 100건 읽기. `more_history=true`이면 추가 이력 대조가 필요하다. 게시하지 않는다.
2. `preview`: 무결성 검증된 자료로 본문과 답글 미리보기. 게시하지 않는다. 미리보기의 빈 원장은 후보 예시용이며 실제 중복 판정은 게시 단계의 영구 원장을 따른다.
3. `publish-one-now`: 활성화된 main에서 현재 시점 한 건 게시. 본문과 답글 두 개 모두 실제 조회 검증을 마쳐야 성공이다.
4. 자연 예약: 하루 네 회차에 적합한 새 혜택 한 건씩 게시한다.

자료 복원은 기존 운영 수집 workflow의 신뢰된 main 아티팩트와 초기 검증 자료를 사용한다. 지속 운영하려면 보조금24 API 키와 정기 수집이 실제로 연결돼야 한다. 키가 빠진 상태에서는 초기 자료가 24시간을 넘으면 게시가 중단된다. 사이트 운영·배포 승인은 `docs/OPERATIONS.md`의 별도 절차를 따른다.

설정: https://github.com/kllollain-max/supportpick/settings/secrets/actions

실행 결과: https://github.com/kllollain-max/supportpick/actions/workflows/supportpick-threads.yml

## 이미지

`social/assets.json`에 혜택 ID별 검수된 공개 `imageUrl`을 등록할 수 있다. 이미지 경로는 이 저장소의 `social/images/`로 제한한다. 텍스트와 이미지 회차를 교대하되, 해당 혜택의 이미지가 없으면 텍스트로 게시한다. 현재 등록 자료가 비어 있으면 이미지 제작까지 완료된 것으로 보고하지 않는다.

## 장애 처리

성공·건너뜀·실패를 Actions 요약과 결과 아티팩트로 남긴다. 실패 시 원장의 stage, main_id/detail_id/links_id, 로그의 영수증을 실제 계정의 게시물과 대조한다. 원격 상태가 불명확하면 재게시하지 않는다. 토큰·자료 갱신·계정 오류를 해결한 뒤 계정 확인과 미리보기를 다시 통과시키고 다음 신규 회차를 진행한다.

공식 API 참고: https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api

## 게시 후 조회와 정확한 영수증 복구

실제 API는 첫 `#지원금픽`을 토픽으로 처리해 조회 본문에서 해당 `#`를 생략한다. 이 한 가지 변환만 허용하며 나머지 문자·CTA·게시 ID·permalink 검증은 유지한다. 조회 전파가 늦는 경우 읽기만 최대 세 번 반복한다.

`resume-pending` 수동 모드에서는 `resume_main_id`에 이미 게시된 본문의 정확한 숫자 ID를 지정한다. 같은 계정·main·최초 실행·당일·24시간 이내 자료·원문 해시가 모두 일치해야 한다. 기존 게시물은 먼저 조회하고 재게시하지 않으며, 아직 전송하지 않은 답글만 이어서 게시한다. 이전 전송 단계에 응답 ID가 없으면 불명확한 전송으로 판단해 복구도 차단한다. 기존 예약을 재사용하므로 당일 게시 수가 늘어나지 않는다.
