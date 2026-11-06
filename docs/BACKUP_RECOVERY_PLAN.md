# 지원금픽 장기 백업·복구 도입 계획 (검토용)

> 이 문서는 실행 정책이 아니다. main 병합, Secrets 설정, 저장공간 연결, 예약 실행 및 공개 배포는 별도 검증 이후 수행한다.

## 확인된 현황
- 운영 저장소: kllollain-max/supportpick (이미 생성 및 운영 중)
- 2026-11-04 정상 수집: 10,942건, run 41805765326, generation gov24-41805765326-1
- runtime-state artifact 13310042236, SHA-256 d7347d6cf920d5e24610ea968771aa350febb8c3e49f11344d5d612e9d91ab1f, 만료 2026-11-07 18:20:27 KST
- collection-evidence artifact 13310281455, SHA-256 6d1b919cd612e9893c36641a6aa28fafbbf12c3c87eed95c55632bc08a937e17, 만료 2026-11-07 18:20:30 KST
- 기존 workflow는 06:20/18:20 KST 예약, runtime/evidence 3일 보존. 실제 예약 성공은 실행별 확인 필요.
- docs/OPERATIONS.md의 '저장소 없음', '미공개', 'workflow disabled', '예약 0회' 설명은 현행 운영 사실과 불일치하므로 개정 필요.

## 우선순위 0: 아티팩트 만료 전 독립 사본
1. 현재 run의 runtime-state와 collection-evidence ZIP을 비공개 객체 스토리지에 다운로드/업로드한다.
2. GitHub가 보고한 아티팩트 digest와 다운로드 바이트 SHA-256을 비교하고 ZIP CRC, 내부 manifest, read_current 검사를 실행한다.
3. 복원 검증 결과와 객체 버전 ID를 불변 manifest에 기록한다.
4. 스토리지 업로드 및 복원 검증이 모두 성공하기 전에는 '백업 완료'라고 보고하지 않는다.

## 권장 보존 구조
- primary: GitHub Actions 3일, 현행 유지
- secondary: 별도 계정/인증의 private object storage, versioning 및 가능하면 immutable retention
- latest-good.json은 검증된 generation, run_id, created_at, last_success_at, source SHA, object keys, sha256, schema version, blog link snapshot/version을 기록한다.
- 원본 API 증거, 정규화 데이터, 세대 manifest, SHA-256, 블로그 연결 스냅샷은 각각 독립 해시로 관리한다.
- 7일 회차별, 90일 일별, 12개월 월별 기준본, 최신/직전 정상본은 별도 보호. 용량·요금제 확인 후 수명주기 정책 확정.
- 블로그 연결은 안정 ID 기준으로 별도 버전 관리하며 오래된 연결 스냅샷이 최신 링크를 덮어쓰지 않도록 한다.

## 복원 알고리즘 (구현 전 검증 필수)
1. 현재 trusted main 운영 run의 아티팩트 복원 시도.
2. 부재·만료·손상 시 장기 백업 인덱스에서 최신 검증 정상 세대 탐색; 이전 정상 세대로 순차 폴백.
3. 다운로드 제한, ZIP 경로·심볼릭 링크·압축 해제 크기 검사, SHA-256 및 read_current 검증.
4. 임시 폴더에 복원하고 수집 건수, 고유 ID, generation, last_success_at, 블로그 링크 매핑, 정적 빌드를 검사.
5. 모든 검사 성공 후에만 current 포인터를 원자 교체. 검증 실패 시 운영 데이터와 공개 사이트를 변경하지 않는다.
6. 과거 데이터를 최신 수집으로 표시하지 않고 지연 상태를 유지한다. 복구 자체는 배포 승인 변수를 우회하지 않는다.

## 검증 및 롤아웃
- unit: 만료/손상/없는 아티팩트, SHA mismatch, ZIP traversal, ID 불일치, 블로그 링크 누락, 실패 후 정상 포인터 보존.
- integration: 새 정상본 → 외부 보존 → 원격 재다운로드 → 임시 복원 → 전체 빌드 및 공개 URL 검증.
- 매일 해시 점검, 매주 샌드박스 복원, 매월 전체 복구 훈련.
- 독립 스토리지 자격증명은 별도 secret에 최소 권한으로 설정하고 공개 저장소·로그·Pages 산출물에 노출하지 않는다.
- 기존 지원금 수집, Threads, 블로그 자동화와 해당 토큰·예약·저장소는 수정하지 않는다.

## 남은 승인·환경 의존성
- 독립 객체 스토리지 공급자 및 버킷/계정, 권한, 실제 요금/용량 확정.
- 별도 백업 자동화 코드 구현 및 테스트 통과, 운영자 검토 후 main 병합·활성화.
- 만료 임박 아티팩트의 외부 사본 생성은 아직 실행/확인되지 않았다.
