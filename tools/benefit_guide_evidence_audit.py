"""Offline evidence coverage check for SupportPick guides.

This checks metadata completeness, NOT external availability, eligibility, or
proof that a government program accepts applications today. It never writes.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "guides.json"

def audit_guides(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("guides"), list):
        raise ValueError("invalid_guides")
    rows = []
    seen = set()
    for guide in payload["guides"]:
        if not isinstance(guide, dict):
            raise ValueError("invalid_guide_record")
        sid = guide.get("benefitId")
        if not isinstance(sid, str) or not sid or sid in seen:
            raise ValueError("duplicate_or_invalid_benefit_id")
        seen.add(sid)
        refs = guide.get("sourceReviews")
        if not isinstance(refs, list):
            refs = []
        mismatched = []
        official = 0
        external = 0
        unsafe = 0
        for ref in refs:
            url = ref.get("url") if isinstance(ref, dict) else None
            parsed = urlsplit(url if isinstance(url, str) else "")
            if parsed.scheme != "https" or not parsed.hostname:
                unsafe += 1
                continue
            if parsed.hostname == "plus.gov.kr":
                official += 1
                if parse_qs(parsed.query).get("svcId") != [sid]:
                    mismatched.append(url)
            else:
                external += 1
        faq = guide.get("faq")
        faq_ok = (isinstance(faq, list) and bool(faq) and
                  all(isinstance(item, dict) and
                      isinstance(item.get("question"), str) and item["question"].strip() and
                      isinstance(item.get("answer"), str) and item["answer"].strip()
                      for item in faq))
        valid_until = guide.get("validUntil")
        rows.append({"benefit_id": sid, "matched_gov24_source": official == 1 and not mismatched,
                     "additional_agency_source_count": external,
                     "faq_complete": bool(faq_ok), "unsafe_sources": unsafe,
                     "source_id_mismatch": bool(mismatched),
                     "review_expiry_present": isinstance(valid_until, str) and bool(valid_until),
                     "extra_source_review_needed": external == 0})
    return {
        "record_count": len(rows),
        "id_mismatches": [r["benefit_id"] for r in rows if not r["matched_gov24_source"]],
        "unsafe_source_records": [r["benefit_id"] for r in rows if r["unsafe_sources"]],
        "faq_incomplete": [r["benefit_id"] for r in rows if not r["faq_complete"]],
        "additional_source_missing": [r["benefit_id"] for r in rows if r["extra_source_review_needed"]],
        "rows": rows,
        "limitations": [
            "Source URL presence does not prove that a page is reachable, recent, or accurately cited.",
            "No live application/eligibility, amount, or current intake status is checked.",
            "An additional source URL is not necessarily a relevant or valid authority."
        ]
    }

if __name__ == "__main__":
    result = audit_guides(json.loads(DATA.read_text(encoding="utf-8")))
    print(json.dumps({k:v for k,v in result.items() if k!="rows"}, ensure_ascii=False))
    if result["id_mismatches"] or result["unsafe_source_records"] or result["faq_incomplete"]:
        raise SystemExit(1)
