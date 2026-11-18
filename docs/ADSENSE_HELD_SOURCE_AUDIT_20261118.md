# 공개 보류 원문 갱신 추적 (2026-11-18)

## 문제와 변경
기존 source-review-report.json은 등록 준비 안내/블로그만 점검하여, 해설이 연결되지 않은 공개 보류 사업의 원문 변경을 보고하지 않았습니다.
별도 holds 배열과 holdEntries/holdReviewRequired를 더했습니다. 기존 registeredEntries/active/reviewRequired 집계의 의미는 유지합니다.

- held_source_unchanged: 기록된 원문 해시와 동일. 공개 보류 유지, 정확성 검증이나 보류 해제 아님.
- held_source_material_changed: 원문 변경으로 공식 자료 재대조 필요.
- hold_baseline_unavailable: 기록된 유효한 SHA256 기준 없음. 현재 값을 과거 확인값으로 채우지 않음.
- not_in_current_source: 현재 수집본에 없음. 삭제나 보류 해제로 해석하지 않음.
- 변경 필드는 이전 수집본의 해시가 observedSourceHash와 일치할 때만 표시. 근거가 없으면 빈 목록과 unavailable 표시.

등록 보류 11건 중 7건은 기존 observedSourceHash가 없습니다. 이번 변경은 이 누락을 드러내며 임의 기준값, 확인일, 원문, 공개 범위를 바꾸지 않습니다. 나머지 4건의 실제 현재 변경 여부는 해당 빌드 데이터에 따라 결정됩니다.

## 보호와 검증
수정은 보고서 생성기/회귀 테스트/이 문서만입니다. guides.json 및 데이터, 공개 렌더러, 검색/비교, 수집/게시, 계정, 신청기록, 자동화 일정은 그대로 둡니다.
추가 테스트는 보류 유지와 해설 집계 분리, 실제 변경/검증된 비교 기준/기준 불일치, 누락/잘못된 해시, 시각만 변경, 기존 보류 ID 전부 보고를 확인합니다.
로컬 실행 환경이 없어 PR의 기존 GitHub Actions로 테스트와 빌드 검증을 실행합니다. 성공 여부는 PR 실행 기록을 기준으로 판단합니다.

## 백업 및 배포
변경 전 main: a00bcc735bee4cb72170bad67fe317b66d10e637.
소스 백업: backup/held-source-audit-20261118-before.
동시 병합된 PR77의 Threads 복구를 포함한 최신 main을 기반으로 하며 해당 코드를 수정하지 않습니다.
현재 연결에는 workflow_dispatch 실행 기능이 없어 승인 배포 워크플로를 시작할 수 없습니다. 배포 게이트를 변경하지 않으며 이번 PR은 운영 미반영 상태로 유지합니다. 기존 PR76 배포42의 운영 검증을 이번 변경의 배포 증거로 사용하지 않습니다.

전체 콘텐츠 가치 검토는 미완료입니다. AdSense/검색 콘솔 계정 상태는 계정 확인이 필요하며 재심사 신청은 하지 않습니다.
