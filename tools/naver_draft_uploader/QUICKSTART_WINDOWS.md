# 무료 Windows 시작 — 이전 실행 안내를 대체합니다

현재는 설치·직접 로그인·읽기 전용 화면 진단까지만 허용합니다. 기존 `run_phase1_windows.ps1` 및 예약 등록은 실행하지 마세요. 실입력 진입점은 `LIVE_ADAPTER_NOT_READY`로 차단했습니다.

이 대화에 제공된 `SupportPick_Free_Windows` ZIP은 원본 TXT·PNG 3장, 상대경로 manifest, 소스, 검사 결과를 포함합니다. 압축을 완전히 푼 다음 아래 순서로 실행합니다.

1. `01_SETUP.cmd`: Python 3.11+ 확인, 폴더 전용 venv·패키지 설치, 환경/원고 검사.
2. `02_LOGIN.cmd`: 별도 로컬 Chrome/Edge 프로필에서 사용자 직접 로그인. 검은 창으로 돌아와 Enter.
3. `03_INSPECT.cmd`: 사용자가 글쓰기를 직접 열고 Enter. 기존 내용은 변경하지 않습니다. `reports/inspect.json`만 진단 결과로 공유합니다.

공개 블로그 접근이나 편집기 후보 구조 관측은 계정 권한 확인 또는 VERIFIED가 아닙니다. 로그인 프로필·쿠키·비밀번호는 공유하지 마세요. 프로그램은 본문 입력·임시저장·발행·예약 등록을 하지 않습니다.

`windows_starter/`는 같은 소스입니다. GitHub에는 원본 PNG를 추가 공개하지 않았으므로 저장소 소스만 받은 경우 자산 파일이 없으면 진단이 실패합니다. 제공된 ZIP을 사용하세요.

검증과 남은 결함은 `LOCAL_RUNNER_AUDIT.md`에 기록했습니다. 기존 원고 생성 자동화·예약·main에는 변경이 없습니다.
