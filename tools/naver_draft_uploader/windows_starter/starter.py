"""SupportPick free Windows preparation tool. No automated editing or saving.

Normal launch: python starter.py diagnose | login | inspect
The isolated entry point avoids the legacy uploader's queue.py shadowing stdlib.
No credentials, cookies, page HTML, article text, or screenshots are exported.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
CTA = "다른 생활 지원 제도는 지원금픽 링크에서 확인하세요."
CTA_URL = "https://kllollain-max.github.io/supportpick/"
BLOG_URL = "https://blog.naver.com/bible_el"
TARGET = "bible_el"
ALLOW_WRITE = False
ALLOW_PUBLISH = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return obj


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".report-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(obj, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def safe_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("RELATIVE_ASSET_PATH_REQUIRED")
    # Portable packages use forward-slash relative paths, not /mnt or C:\ paths.
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError("RELATIVE_ASSET_PATH_REQUIRED")
    base = root.resolve()
    path = (base / value).resolve()
    if not path.is_relative_to(base):
        raise ValueError("ASSET_PATH_OUTSIDE_PACKAGE")
    return path


def load_payload(path: Path) -> dict:
    data = read_json(path)
    required = ("content_id", "title", "body_text", "images", "cta_text", "cta_url")
    if any(k not in data for k in required):
        raise ValueError("MANIFEST_MISSING_FIELDS")
    if not isinstance(data["content_id"], str) or not re.fullmatch(r"supportpick-[A-Za-z0-9_-]{1,160}", data["content_id"]):
        raise ValueError("INVALID_CONTENT_ID")
    if not isinstance(data["title"], str) or not data["title"].strip():
        raise ValueError("TITLE_REQUIRED")
    if not isinstance(data["body_text"], str) or not data["body_text"].strip():
        raise ValueError("BODY_REQUIRED")
    if data["cta_text"] != CTA or data["cta_url"] != CTA_URL:
        raise ValueError("WRONG_BRAND_CTA")
    if data["body_text"].count(CTA) != 1 or data["body_text"].count(CTA_URL) != 1:
        raise ValueError("CTA_MISSING_OR_DUPLICATED")
    if not isinstance(data["images"], list) or not all(isinstance(i, dict) for i in data["images"]):
        raise ValueError("INVALID_IMAGES")
    if data.get("live_publish_allowed", False) is not False:
        raise ValueError("PUBLISH_FORBIDDEN")
    # Retain producer metadata; do not pass unknown fields to a dataclass ctor.
    return data


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check_assets(manifest_path: Path) -> dict:
    data = load_payload(manifest_path)
    root = manifest_path.parent
    errors: list[str] = []
    details: list[dict] = []
    seen_hashes: set[str] = set()
    seen_ids: set[str] = set()
    from PIL import Image
    for index, item in enumerate(data["images"], 1):
        entry = {"index": index, "valid": False}
        try:
            path = safe_path(root, item.get("path"))
            if not path.is_file() or path.stat().st_size <= 0:
                raise ValueError("IMAGE_MISSING_OR_EMPTY")
            actual_hash = sha256(path)
            if item.get("sha256") != actual_hash:
                raise ValueError("IMAGE_HASH_MISMATCH")
            if type(item.get("size_bytes")) is not int or item["size_bytes"] != path.stat().st_size:
                raise ValueError("IMAGE_SIZE_MISMATCH")
            source_id = item.get("source_file_id")
            if actual_hash in seen_hashes or (source_id and source_id in seen_ids):
                raise ValueError("DUPLICATE_IMAGE")
            seen_hashes.add(actual_hash)
            if source_id:
                seen_ids.add(source_id)
            with Image.open(path) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise ValueError("UNSUPPORTED_IMAGE_FORMAT")
                width, height = image.size
                image.verify()
            # Decode pixels too: verify alone does not load all formats fully.
            with Image.open(path) as image:
                image.load()
            entry.update(valid=True, width=width, height=height, sha256=actual_hash, bytes=path.stat().st_size)
        except Exception as exc:
            known = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
            errors.append(f"image_{index}:{known}")
        details.append(entry)
    body_ok = False
    try:
        body_path = safe_path(root, data.get("source_body_path"))
        body_bytes = body_path.read_bytes()
        if len(body_bytes) != data.get("source_body_size_bytes") or hashlib.sha256(body_bytes).hexdigest() != data.get("source_body_sha256"):
            raise ValueError("BODY_FILE_HASH_OR_SIZE_MISMATCH")
        normal = lambda text: text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if normal(body_bytes.decode("utf-8-sig")) != normal(data["body_text"]):
            raise ValueError("BODY_CONTENT_MISMATCH")
        body_ok = True
    except Exception as exc:
        errors.append(str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    return {"content_id": data["content_id"], "body_file_ok": body_ok,
            "image_expected": len(data["images"]), "image_valid": sum(i["valid"] for i in details),
            "images": details, "errors": errors, "assets_ok": not errors}


def url_facts(url: str) -> dict:
    value = urlsplit(url)
    host = (value.hostname or "").lower()
    naver = host == "naver.com" or host.endswith(".naver.com")
    query = parse_qs(value.query)
    blog_match = host in {"blog.naver.com", "m.blog.naver.com"} and (
        TARGET in value.path.split("/") or query.get("blogId") == [TARGET])
    return {"naver_host": naver, "target_blog_url": blog_match,
            "login_host": host == "nid.naver.com"}


def assess_probe(observations: list[dict]) -> dict:
    if any(o.get("security_barrier_seen") for o in observations):
        status = "MANUAL_AUTH_REQUIRED"
    elif any(o.get("editable_count", 0) > 0 and o.get("save_control_count", 0) > 0 for o in observations):
        status = "EDITOR_INSPECTION_CAPTURED"
    elif any(o.get("login_host") for o in observations):
        status = "LOGIN_REQUIRED"
    else:
        status = "SITE_REACHABLE_AUTH_UNVERIFIED"
    # Public blog URL and even visible logout controls are not ownership evidence.
    return {"status": status, "account_verified": False, "draft_verified": False,
            "editor_opened_by_automation": False, "write_performed": False,
            "save_performed": False, "publish_performed": False, "observations": observations}


# No text nodes, values, URLs, cookies, localStorage, or network bodies are exported.
STRUCTURE_SCRIPT = r"""() => {
 const visible=e=>!!(e.getClientRects().length) && getComputedStyle(e).visibility!=='hidden';
 const el=[...document.querySelectorAll('input:not([type=password]),textarea,[contenteditable=true]')].filter(visible);
 const controls=[...document.querySelectorAll('button,a,[role=button]')].filter(visible);
 const labels=['글쓰기','사진','이미지','임시저장','발행','로그인','로그아웃'];
 const counts=Object.fromEntries(labels.map(x=>[x,controls.filter(e=>(e.innerText||'').trim()===x).length]));
 const security=[...document.querySelectorAll('input,iframe,[role=dialog]')].filter(visible).some(e=>
   /captcha/i.test((e.getAttribute('id')||'')+' '+(e.getAttribute('name')||'')+' '+(e.getAttribute('title')||'')));
 return {editable_count:el.length, save_control_count:counts['임시저장'], security_barrier_seen:security,
   control_counts:counts,
   editable_structure:el.slice(0,25).map(e=>({tag:e.tagName.toLowerCase(),
       contenteditable:e.getAttribute('contenteditable')==='true',
       editor_classes:[...e.classList].filter(x=>/^se[-_][a-zA-Z0-9_-]{1,60}$/.test(x)).slice(0,8)}))};
}"""


def detect_channel() -> str | None:
    if sys.platform != "win32":
        return None
    roots = [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")]
    for channel, suffix in (("chrome", "Google/Chrome/Application/chrome.exe"),
                            ("msedge", "Microsoft/Edge/Application/msedge.exe")):
        if any(root and (Path(root) / suffix).is_file() for root in roots):
            return channel
    return None


def profile_path(channel: str) -> Path:
    if channel not in {"chrome", "msedge"}:
        raise ValueError("UNSUPPORTED_CHANNEL")
    root = os.environ.get("LOCALAPPDATA")
    if sys.platform != "win32" or not root:
        raise ValueError("WINDOWS_LOCAL_PROFILE_REQUIRED")
    return Path(root) / "SupportPickNaverDraft" / (channel + "-profile")


def diagnose() -> tuple[int, dict]:
    checks = {}
    for name in ("playwright", "Pillow"):
        try:
            checks[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            checks[name] = None
    report = {"status": "LOCAL_ENV_INCOMPLETE", "checked_at": utc_now(),
              "os": sys.platform, "python": sys.version.split()[0], "packages": checks,
              "browser_channel": detect_channel(), "live_upload_enabled": False,
              "account_verified": False, "draft_verified": False}
    try:
        report["assets"] = check_assets(ROOT / "phase1_candidate.json")
    except Exception as exc:
        report["assets"] = {"assets_ok": False, "error_type": type(exc).__name__}
    ready = sys.platform == "win32" and sys.version_info >= (3, 11) and all(checks.values()) and report["browser_channel"] and report["assets"]["assets_ok"]
    if ready:
        report["status"] = "LOCAL_ENV_OK"
    return (0 if ready else 2), report


def browser_session(mode: str, channel: str | None = None) -> tuple[int, dict]:
    channel = channel or detect_channel()
    if channel not in {"chrome", "msedge"}:
        return 2, {"status": "BROWSER_NOT_FOUND", "draft_verified": False}
    from playwright.sync_api import sync_playwright
    profile = profile_path(channel)
    profile.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        # Dedicated local profile. No remote debugging port and no cloud provider.
        context = pw.chromium.launch_persistent_context(str(profile), channel=channel,
            headless=False, viewport={"width": 1440, "height": 1000})
        try:
            page = context.new_page()
            response = page.goto(BLOG_URL, wait_until="domcontentloaded", timeout=30000)
            if response and response.status >= 400:
                return 3, {"status": "NAVER_HTTP_ERROR", "http_status": response.status, "draft_verified": False}
            print("브라우저에서 bible_el 계정으로 직접 로그인하세요.")
            if mode == "inspect":
                print("로그인 후 '글쓰기'를 직접 열어주세요. 기존 글은 삭제하거나 변경하지 마세요.")
                print("화면이 열리면 이 검은 창으로 돌아와 Enter를 누르세요. 글 입력·저장은 하지 않습니다.")
            else:
                print("로그인 후 이 검은 창으로 돌아와 Enter를 누르세요. 로그인 성공으로 자동 판정하지 않습니다.")
            input()
            observations = []
            for current in list(context.pages):
                if current.is_closed():
                    continue
                for frame in list(current.frames):
                    facts = url_facts(frame.url)
                    if not facts["naver_host"]:
                        continue
                    try:
                        structure = frame.evaluate(STRUCTURE_SCRIPT)
                        observations.append({**facts, **structure})
                    except Exception:
                        observations.append({**facts, "inspection_unavailable": True})
            result = assess_probe(observations)
            result.update(checked_at=utc_now(), browser_channel=channel,
                          browser_version=context.browser.version if context.browser else None,
                          mode=mode)
            return 0, result
        finally:
            # No tab navigation/refresh/clear/save during cleanup. This tool has not typed.
            context.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["diagnose", "login", "inspect"])
    parser.add_argument("--channel", choices=["chrome", "msedge"])
    args = parser.parse_args(argv)
    try:
        if args.mode == "diagnose":
            code, report = diagnose()
        else:
            code, report = browser_session(args.mode, args.channel)
    except KeyboardInterrupt:
        code, report = 130, {"status": "STOPPED_BY_USER", "draft_verified": False}
    except Exception as exc:
        # No raw exceptions: browser messages can include sensitive URLs/paths.
        code, report = 3, {"status": "LOCAL_RUN_FAILED", "error_type": type(exc).__name__,
                          "checked_at": utc_now(), "draft_verified": False,
                          "next_step": "기존 자동화 브라우저 창을 닫고 설치·브라우저 상태를 확인하세요. 보안 인증은 직접 처리하세요."}
    output = ROOT / "reports" / (args.mode + ".json")
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("진단 파일:", output.name, "(reports 폴더)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
