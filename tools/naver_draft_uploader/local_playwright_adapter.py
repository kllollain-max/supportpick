from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import time

from runner import AdapterError, NaverAdapter


class LocalPlaywrightNaverAdapter(NaverAdapter):
    """
    Free local-browser adapter for Windows + Playwright.

    Safety:
    - uses an explicit persistent local browser profile directory
    - does not store passwords/cookies in repo
    - never bypasses CAPTCHA/MFA/security checks
    - never publishes
    - re-discovers the current editor every run
    """

    def __init__(self, *, user_data_dir: str, browser_channel: str = "chrome", headless: bool = False):
        self.user_data_dir = str(Path(user_data_dir).expanduser())
        self.browser_channel = browser_channel
        self.headless = headless
        self._pw = None
        self._context = None
        self._page = None

    def start(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise AdapterError("BROWSER_START_FAILED", f"playwright import failed: {exc}") from exc

        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)
        self._pw = sync_playwright().start()
        try:
            self._context = self._pw.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                channel=self.browser_channel,
                headless=self.headless,
                viewport={"width": 1440, "height": 1000},
                args=["--disable-notifications"],
            )
        except Exception as exc:
            self.stop()
            raise AdapterError("BROWSER_START_FAILED", str(exc)) from exc
        return self

    def stop(self):
        try:
            if self._context:
                self._context.close()
        finally:
            self._context = None
            if self._pw:
                self._pw.stop()
            self._pw = None
            self._page = None

    def _pages(self):
        if not self._context:
            return []
        return list(self._context.pages)

    def _active_or_new_page(self):
        pages = self._pages()
        for p in reversed(pages):
            if "naver.com" in (p.url or ""):
                return p
        return self._context.new_page()

    def _detect_auth_barrier(self, page):
        text = ""
        try:
            text = page.locator("body").inner_text(timeout=3000)
        except Exception:
            pass
        lower = text.lower()
        barrier_words = [
            "captcha", "보안 확인", "추가 인증", "본인확인", "휴대전화 인증",
            "비정상적인 접근", "이용이 제한", "로그인이 필요"
        ]
        if any(w.lower() in lower for w in barrier_words):
            raise AdapterError("MANUAL_AUTH_REQUIRED", "Naver authentication/security barrier detected")

    def precheck(self):
        page = self._active_or_new_page()
        page.goto("https://blog.naver.com/bible_el", wait_until="domcontentloaded", timeout=30000)
        self._detect_auth_barrier(page)

        body = page.locator("body").inner_text(timeout=10000)
        if "bible_el" not in body and "bible_el" not in page.url:
            raise AdapterError("LOGIN_REQUIRED", "target blog identity not confirmed")

        self._page = page
        return {"account_ok": True, "blog_ok": True}

    def open_editor(self):
        page = self._page or self._active_or_new_page()

        # Prefer a visible/write link from the current page. Selectors are intentionally
        # generic because Naver can change DOM structure. Failure is safe-stop.
        candidates = [
            page.get_by_role("link", name="글쓰기"),
            page.get_by_text("글쓰기", exact=True),
        ]
        opened = False
        for loc in candidates:
            try:
                if loc.count() and loc.first.is_visible():
                    loc.first.click(timeout=5000)
                    opened = True
                    break
            except Exception:
                continue

        if not opened:
            # Direct editor URL is not guessed here; unknown DOM means safe stop.
            raise AdapterError("EDITOR_NOT_READY", "write entry point not found")

        page.wait_for_load_state("domcontentloaded", timeout=15000)
        self._detect_auth_barrier(page)
        self._page = page
        return True

    def _find_title(self):
        page = self._page
        selectors = [
            'textarea[placeholder*="제목"]',
            'input[placeholder*="제목"]',
            '[contenteditable="true"][data-placeholder*="제목"]',
        ]
        for sel in selectors:
            try:
                loc = page.locator(sel)
                if loc.count() and loc.first.is_visible():
                    return loc.first
            except Exception:
                continue
        raise AdapterError("EDITOR_NOT_READY", "title editor not found")

    def _find_body(self):
        page = self._page
        selectors = [
            '[contenteditable="true"][data-placeholder*="본문"]',
            '[contenteditable="true"][aria-label*="본문"]',
            'div[contenteditable="true"]',
        ]
        for sel in selectors:
            try:
                loc = page.locator(sel)
                count = loc.count()
                if count:
                    for i in range(count):
                        item = loc.nth(i)
                        if item.is_visible():
                            return item
            except Exception:
                continue
        raise AdapterError("EDITOR_NOT_READY", "body editor not found")

    def read_editor_snapshot(self):
        title = ""
        body = ""
        try:
            title = self._find_title().input_value(timeout=2000)
        except Exception:
            try:
                title = self._find_title().inner_text(timeout=2000)
            except Exception:
                pass
        try:
            body = self._find_body().inner_text(timeout=3000)
        except Exception:
            pass
        return {"title": title, "body": body, "image_count": 0}

    def set_title(self, title: str):
        loc = self._find_title()
        try:
            loc.fill(title, timeout=5000)
            return loc.input_value(timeout=2000)
        except Exception:
            loc.click(timeout=3000)
            loc.press("Control+A")
            loc.type(title, delay=5)
            try:
                return loc.input_value(timeout=2000)
            except Exception:
                return loc.inner_text(timeout=2000)

    def set_body_plain_text(self, body: str):
        loc = self._find_body()
        loc.click(timeout=5000)
        loc.press("Control+A")
        loc.press("Backspace")
        # Insert as plain text to avoid hidden external formatting.
        loc.type(body, delay=1)
        return loc.inner_text(timeout=5000)

    def upload_images(self, images: list[dict]) -> int:
        if not images:
            return 0
        page = self._page

        # Try native file chooser from visible photo/image control.
        triggers = [
            page.get_by_text("사진", exact=True),
            page.get_by_text("이미지", exact=True),
        ]

        uploaded = 0
        for image in images:
            path = image.get("path")
            if not path or not Path(path).exists():
                raise AdapterError("IMAGE_UPLOAD_FAILED", f"image missing: {path}")

            triggered = False
            for trigger in triggers:
                try:
                    if trigger.count() and trigger.first.is_visible():
                        with page.expect_file_chooser(timeout=5000) as fc:
                            trigger.first.click(timeout=3000)
                        chooser = fc.value
                        chooser.set_files(path)
                        triggered = True
                        break
                except Exception:
                    continue

            if not triggered:
                inputs = page.locator('input[type="file"]')
                if inputs.count():
                    try:
                        inputs.first.set_input_files(path)
                        triggered = True
                    except Exception:
                        pass

            if not triggered:
                raise AdapterError("IMAGE_UPLOAD_FAILED", "photo upload control not found")

            time.sleep(1.5)
            uploaded += 1

        return uploaded

    def apply_minimal_formatting(self):
        return True

    def click_temporary_save(self):
        page = self._page
        candidates = [
            page.get_by_text("임시저장", exact=True),
            page.get_by_role("button", name="임시저장"),
        ]
        for loc in candidates:
            try:
                if loc.count() and loc.first.is_visible():
                    loc.first.click(timeout=5000)
                    return True
            except Exception:
                continue
        raise AdapterError("SAVE_CLICK_FAILED", "temporary-save control not found")

    def locate_saved_draft(self, *, title: str, content_id: str):
        # Do not assume a URL pattern. Re-discover from visible UI.
        page = self._page
        try:
            body = page.locator("body").inner_text(timeout=5000)
            if title in body:
                return {"draft_id": None, "title": title, "content_id": content_id}
        except Exception:
            pass
        raise AdapterError("DRAFT_NOT_FOUND", "saved draft not independently located")

    def reopen_draft(self, draft):
        # Real independent draft-list navigation must be verified against the current
        # Naver UI during Phase 1. Until then this adapter fails closed.
        raise AdapterError("REOPEN_FAILED", "independent draft-list reopen selector not yet verified")

    def verify_reopened_content(self, manifest):
        raise AdapterError("CONTENT_MISMATCH", "reopen verification unavailable before Phase-1 selector verification")
