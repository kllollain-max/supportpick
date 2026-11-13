import unittest
from tools.benefit_guide_evidence_audit import audit_guides

def entry(id="A1",url="https://plus.gov.kr/d?svcId=A1",external=True):
    r=[{"url":url}]
    if external: r.append({"url":"https://example.org/official"})
    return {"benefitId":id,"sourceReviews":r,"validUntil":"2026-11-18T00:00:00Z",
            "faq":[{"question":"어떤 조건인가요?","answer":"공식 자료를 확인하세요."}]}

class EvidenceAuditTests(unittest.TestCase):
    def test_valid_and_missing_external_are_distinct(self):
        x=audit_guides({"guides":[entry(),entry("B2","https://plus.gov.kr/d?svcId=B2",False)]})
        self.assertEqual(x["id_mismatches"],[])
        self.assertEqual(x["additional_source_missing"],["B2"])
    def test_wrong_gov24_id_never_passes(self):
        x=audit_guides({"guides":[entry("A1","https://plus.gov.kr/d?svcId=B2")]})
        self.assertEqual(x["id_mismatches"],["A1"])
    def test_missing_faq_and_non_https_rejected(self):
        bad=entry();bad["faq"]=[];bad["sourceReviews"].append({"url":"http://invalid.example"})
        x=audit_guides({"guides":[bad]})
        self.assertEqual(x["faq_incomplete"],["A1"])
        self.assertEqual(x["unsafe_source_records"],["A1"])
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError): audit_guides({"guides":[entry(),entry()]})
    def test_non_list_rejected(self):
        with self.assertRaises(ValueError): audit_guides({"guides":{}})
if __name__=="__main__": unittest.main()
