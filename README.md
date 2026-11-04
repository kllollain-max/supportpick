# 지원금픽

검색용 사이트맵·공유 미리보기·구글/네이버 소유확인 준비는 [검색 준비 안내](docs/SEARCH_READINESS.md)에 정리했다. 사이트맵은 공개 빌드에서 생성하며 검색도구 등록·소유확인·색인 상태와 구분한다.

기존 검토본 PR #16과 저장 ZIP의 동일성을 확인한 뒤, 화면을 재사용해 보조금24 전체 수집·실제 자료 연결·실패 보존·자동 갱신 준비를 구현했다. 수정 담당: ChatGPT/Codex. 기존 커리어픽·블로그·Threads·웹푸시 운영은 변경하지 않았다.

## 실제 완료

- 2026-11-04 13:45 KST 수집 완료: 연결된 보조금24 목록·상세·지원조건 각110페이지, 각10,942건. 총건수·수신·고유ID·저장이 일치하며 중복0·표본0이다.
- 실제 호출333회. 실행: https://github.com/kllollain-max/automation-system/actions/runs/41774386414
- 검색·분야·지역·대상·지원방식·정렬·맞춤·저장·내 신청에 실제 자료를 연결했다. 목록은30개씩, 상세는 버전별32개 조각에서 필요할 때 읽는다.
- 지역 미제공과 소관기관 지역을 구분한다. 목록·상세 표기 차이가 있는174개 서비스는 두 원문 값을 함께 표시한다. API 조회는 실제 신청 가능 여부·수급 자격 확정이 아니다.
- 페이지별 체크포인트·해시·재개, 전체 ID 연결 검사, 경계 변화·부분 응답·빈 자료·급감 차단, 정상 세대 포인터 원자 교체, 실패·지연 안내를 연결했다.
- 전용 키와 백업 형식을 사용하고 다른 사이트의 서비스워커·캐시·알림을 변경하지 않는다.

## 데이터와 복구 패키지

코드 PR은 `bootstrap.json`에 초기 정상 자료 ZIP의 SHA-256·세대·건수를 기록한다. **실제 `bootstrap-state.zip`은 데이터가 포함된 배포 준비 패키지의 source/에 제공**한다. 공개 코드만 복사하고 이 파일을 빼면 전체 자료 빌드를 완료할 수 없다. source/의 모든 파일을 새 저장소 루트로 사용하면 된다. 원본 API 페이지·정확한 호출 결과는 패키지의 evidence ZIP으로 보존한다. 키 실값·방문자 개인 기록은 포함하지 않는다.

```sh
python3 tools/bootstrap_state.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/core.test.cjs
python3 tools/build.py --output dist
```

검증·복구·승인 후 실행할 정확한 단계는 [docs/OPERATIONS.md](docs/OPERATIONS.md), 확인 결과와 한계는 [VALIDATION.md](VALIDATION.md)에 있다.

## 독립 저장소 공개·운영 연결

사용자 승인(2026-11-04)에 따라 `kllollain-max/supportpick` 공개 저장소를 생성하고 승인 검토본을 이전했다. 공개 주소는 `https://kllollain-max.github.io/supportpick/`다. 실제 배포와 운영 연결 결과는 [승인 기록](docs/DEPLOYMENT_APPROVAL_20261104.md)에 이어 기록한다.

운영 워크플로를 `.github/workflows/`에 배치했으며, 정기 수집은 별도 승인 변수와 API 키 등록이 필요하다. 제안 주기는06:20·18:20 KST, 예상666호출/일, 설정 상한1,600호출/일이다. 개별 API 할당량·기간 확인 전에는 정기 수집을 활성화하지 않는다. 실제 예약 실행 성공은 수동 검증과 구분한다.
