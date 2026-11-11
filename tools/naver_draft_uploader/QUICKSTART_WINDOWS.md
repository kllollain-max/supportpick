# 지원금픽 네이버 임시저장 자동화 — 무료 Windows 빠른 시작

## 1. 설치
PowerShell에서:

    cd <supportpick 저장소>\tools\naver_draft_uploader
    powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1

## 2. 진단

    powershell -ExecutionPolicy Bypass -File .\diagnose_windows.ps1

## 3. 네이버 로그인 프로필 생성

    powershell -ExecutionPolicy Bypass -File .\login_once.ps1

브라우저가 열리면 사용자가 직접 네이버 로그인합니다. CAPTCHA·추가인증은 자동 처리하지 않습니다.

## 4. 안전 사전점검
이 단계는 글을 입력하거나 저장하지 않습니다.

    powershell -ExecutionPolicy Bypass -File .\precheck_windows.ps1

성공 기준은 PRECHECK_OK입니다. 실패하면 실제 글 입력을 시작하지 않습니다.

## 5. Phase 1
사전점검 성공 후 config.local.json에서 enabled를 true로 바꿉니다. allow_publish는 false를 유지합니다.

    powershell -ExecutionPolicy Bypass -File .\run_phase1_windows.ps1

## 6. 작업 스케줄러
Phase 1 → 3편 → 5편 검증이 모두 끝난 후에만 등록합니다.

    powershell -ExecutionPolicy Bypass -File .\register_task_windows.ps1 -Time "10:30"

동시 실행은 IgnoreNew로 차단됩니다.

## 비용
- Playwright: 무료
- Chrome/Edge: 무료
- Windows 작업 스케줄러: 무료
- GitHub Actions: 필수 아님
