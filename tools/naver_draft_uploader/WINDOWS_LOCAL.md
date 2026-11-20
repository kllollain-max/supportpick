# 무료 Windows 로컬 실행

이 방식은 원격 브라우저 과금 없이 사용자 PC의 Chrome/Edge와 Playwright를 사용합니다.

## 전제

- Windows PC가 켜져 있어야 합니다.
- Python 3.11+ 권장.
- Chrome 또는 Edge 설치.
- 네이버 로그인은 사용자가 직접 수행합니다.
- CAPTCHA/MFA/보안확인은 자동 우회하지 않습니다.
- 자동 발행은 지원하지 않습니다.

## 1. 설치

PowerShell:

```powershell
cd <supportpick 저장소>\tools\naver_draft_uploader
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
```

## 2. 최초 로그인

```powershell
powershell -ExecutionPolicy Bypass -File .\login_once.ps1
```

브라우저가 열리면 필요한 경우 네이버에 직접 로그인합니다.
로그인 완료 후 브라우저를 닫습니다.

로그인 프로필은 로컬 `.naver-browser-profile` 폴더에만 남기고 Git에 커밋하지 않습니다.

## 3. Phase 1 전 안전 설정

`config.local.json`에서 처음에는:

```json
{
  "enabled": false,
  "allow_publish": false
}
```

을 유지합니다.

브라우저 로그인/계정/블로그가 맞는지 확인한 뒤 Phase 1을 실행할 때만:

```json
"enabled": true
```

로 변경합니다.

`allow_publish`는 항상 false입니다.

## 4. Phase 1

```powershell
powershell -ExecutionPolicy Bypass -File .\run_phase1_windows.ps1
```

현 단계의 로컬 어댑터는 제목/본문/이미지/임시저장까지는 현재 UI에서 탐색을 시도하지만,
**임시저장 목록 독립 재열기 selector는 실제 bible_el UI에서 아직 검증되지 않았기 때문에**
그 지점에서 fail-closed로 REOPEN_FAILED가 나도록 되어 있습니다.

이는 버그를 숨기는 것이 아니라, 실제 UI를 확인하지 않고 VERIFIED를 만들지 않기 위한 안전장치입니다.

## 5. Windows 작업 스케줄러

Phase 1→3→5가 모두 통과한 뒤에만 등록합니다.

프로그램:
`powershell.exe`

인수 예:
`-ExecutionPolicy Bypass -File "C:\supportpick\tools\naver_draft_uploader\run_phase1_windows.ps1"`

여러 작업을 동시에 등록하지 않습니다.
항상 1개 실행만 허용합니다.

## 비용

- Playwright: 무료
- Chrome/Edge: 무료
- Windows 작업 스케줄러: 무료
- GitHub Actions: 사용하지 않아도 됨

따라서 사용자 PC에서 실행하는 범위에서는 별도 브라우저 실행 비용 없이 운영할 수 있습니다.
