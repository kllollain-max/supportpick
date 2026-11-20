"""Legacy live adapter is intentionally disabled pending a real UI audit.

Use windows_starter/starter.py for manual login and read-only inspection.
The previous implementation inferred account ownership from a public URL,
counted file-chooser actions as images, and lacked independent draft reopen.
No write operation is permitted while those live invariants are unverified.
"""
from runner import AdapterError, NaverAdapter


class LocalPlaywrightNaverAdapter(NaverAdapter):
    live_ready = False

    def __init__(self, *, user_data_dir, browser_channel="chrome", headless=False):
        self.user_data_dir = user_data_dir
        self.browser_channel = browser_channel
        self.headless = headless

    @staticmethod
    def _blocked(*args, **kwargs):
        raise AdapterError("LIVE_ADAPTER_NOT_READY",
                           "Use the read-only Windows starter; live draft upload is not validated.")

    start = _blocked
    precheck = _blocked
    open_editor = _blocked
    read_editor_snapshot = _blocked
    set_title = _blocked
    set_body_plain_text = _blocked
    upload_images = _blocked
    apply_minimal_formatting = _blocked
    click_temporary_save = _blocked
    locate_saved_draft = _blocked
    reopen_draft = _blocked
    verify_reopened_content = _blocked

    def stop(self):
        return None
