"""Prepare a read-only owner review queue from existing verification metadata.

Never upgrades a program to 'open', renews review expiry, or marks full factual
review as complete. The output is a task queue, not an editorial approval.
"""
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.editorial_freshness_audit import audit as freshness_audit
from tools.benefit_guide_evidence_audit import audit_guides

ROOT = Path(__file__).resolve().parents[1]
HIGHLIGHTS = {
    "140000000176": "2026 산림복지 신규 신청 종료와 11월 30일 이용권 사용기한 구분",
    "105100000001": "2025년 귀속 근로장려금 기한 후 신청 12월 1일 마감 및 국세청 기준",
    "641000000138": "경기도 4분기 청년기본소득 12월 1일 18시 마감과 제외 시군",
    "137100000236": "문화누리카드 11월 30일 발급 마감과 12월 31일 사용기한 구분",
    "135200000115": "2026-2027절기 접종 대상군별 변경된 시작일",
    "B55353000001": "세대별 지원액과 에너지바우처 신청/사용기간 분리",
    "171000000005": "우체국보험 공식 상품 요약서, 실제 청약 가능 여부와 면책조건",
    "SD0000016138": "거주 지자체의 개별 서비스 모집 공고와 본인부담 확인",
    "408000000419": "2026년 의료급여 일반검진 대상 연령과 출생연도, 대상자 조회",
}
# The 2026-11-09 observations record the scope actually read, NOT a current
# verification conclusion. Do not use historical observations to renew expiry.
BODY_OBSERVED_ON_20261109 = {
    "137100000236", "105100000001", "408000000419",
}

def build_queue(guides, editorials, as_of):
    if not isinstance(as_of, date):
        raise ValueError("invalid_date")
    fresh = freshness_audit(guides, editorials, as_of, window=14)
    source = audit_guides(guides)
    source_by_id = {r["benefit_id"]: r for r in source["rows"]}
    items = []
    for row in fresh["review_rows"]:
        bid, kind = row["benefit_id"], row["kind"]
        source_issue = (kind == "guide" and bid in source_by_id
                        and source_by_id[bid]["extra_source_review_needed"])
        # Old source impressions are never a valid basis to extend freshness.
        prior_body_access = (kind == "article"
                             and bid in BODY_OBSERVED_ON_20261109)
        attention = "source_gap" if source_issue else (
            "verify_public_body" if kind == "article" and not prior_body_access else
            "expiry_review")
        items.append({
            "kind": kind, "benefit_id": bid,
            "existing_review_status": row["status"],
            "existing_valid_until": row["valid_until"],
            "priority": 0 if source_issue else (1 if bid in HIGHLIGHTS else 2),
            "attention": attention,
            "specific_review": HIGHLIGHTS.get(bid,
                          "현행 공식자료의 자격, 금액, 기간, 제출서류 및 지역 조건 확인"),
            "body_observed_on_20261109": prior_body_access,
            "full_text_review_confirmed": False,
            "intake_open_verified": False,
            "renewal_authorized": False,
        })
    items.sort(key=lambda r: (r["priority"], r["existing_valid_until"] or "",
                              r["kind"], r["benefit_id"] or ""))
    return {
        "as_of": as_of.isoformat(),
        "records": len(items),
        "unique_benefits": len({r["benefit_id"] for r in items}),
        "source_gap_records": sum(x["attention"] == "source_gap" for x in items),
        "blog_body_not_observed_on_20261109": sum(x["attention"] == "verify_public_body" for x in items),
        "review_expiring_or_expired": sum(x["existing_review_status"] in
                       ("expired_review", "review_due_soon") for x in items),
        "items": items,
        "read_only": True,
        "limitations": [
            "This is a review queue, NOT completion of full fact verification.",
            "Prior public blog reading does not renew any official source's validity.",
            "A listed official source does not prove active intake or individual eligibility.",
            "No programs, editorial status or expiration dates are edited."
        ],
    }

def main():
    guides = json.loads((ROOT / "guides.json").read_text(encoding="utf-8"))
    editorials = json.loads((ROOT / "editorials.json").read_text(encoding="utf-8"))
    now = datetime.now(ZoneInfo("Asia/Seoul")).date()
    report = build_queue(guides, editorials, now)
    out = ROOT / "review-only" / "review-queue.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "items"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
