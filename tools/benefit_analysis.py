"""Small, source-checked explanations; never generated once per API record.

Facts refer to the stated year and review date. The scenarios are our own
reading aids, not eligibility decisions. Keep sources beside the relevant facts.
"""
from html import escape
from family_housing_analysis import FOCUS_ARTICLES
from tax_benefit_analysis import TAX_ARTICLES
from savings_voucher_analysis import RECORD_ARTICLES
from birth_benefit_analysis import BIRTH_ARTICLES
from culture_pension_analysis import CULTURE_PENSION_ARTICLES, source_advisory
from forest_transport_analysis import FOREST_TRANSPORT_ARTICLES, source_advisory as forest_source_advisory
from winter_energy_analysis import WINTER_ARTICLES
from housing_service_analysis import HOUSING_SERVICE_ARTICLES
from claim_preparation_analysis import CLAIM_ARTICLES
from education_business_analysis import EDUCATION_BUSINESS_ARTICLES
from incheon_maternity_analysis import MATERNITY_ARTICLES
from incheon_child_analysis import CHILD_ARTICLES
from maternal_service_analysis import MATERNAL_SERVICE_ARTICLES
from rental_guarantee_analysis import RENTAL_GUARANTEE_ARTICLES
from legacy_youth_savings_analysis import LEGACY_YOUTH_SAVINGS_ARTICLES
from youth_subscription_analysis import YOUTH_SUBSCRIPTION_ARTICLES
from didimdol_analysis import DIDIMDOL_ARTICLES
from school_welfare_analysis import SCHOOL_WELFARE_ARTICLES
from reviewed_amount_analysis import REVIEWED_AMOUNT_ARTICLES, review_advisory
from sunchang_birth_analysis import SUNCHANG_BIRTH_ARTICLES

REVIEWED = '2026-11-17'
ENERGY = 'https://www.energyv.or.kr/info/'
EMERGENCY = 'https://www.mohw.go.kr/menu.es?mid=a10708010100'
LIVELIHOOD = 'https://www.mohw.go.kr/menu.es?mid=a10708010500'

ARTICLES = [
('energy-voucher-2026', '2026 에너지바우처: 신청 마감과 사용기한, 난방비 중복지원 확인',
 '총 지원액을 월 지급액으로 오해하지 않고, 난방 방식과 기존 지원에 맞춰 신청을 준비하는 사례별 안내입니다.', '''
<p class="context-note">고지서 부담과 단열·보일러 공사를 함께 고민한다면 <a href="winter-bills-vs-home-improvement-2026.html">요금 이용권과 주택 공사 준비 비교</a>에서 지역 접수와 소유주 동의부터 나누어 확인하세요.</p>
<h2>신청할 때와 사용할 때의 달력이 다릅니다</h2>
<div class="guide-table"><table><caption>2026년 에너지바우처의 두 기한</caption><thead><tr><th scope="col">구분</th><th scope="col">공식 안내</th><th scope="col">준비할 일</th></tr></thead><tbody>
<tr><th scope="row">신청</th><td>2026.6.15.~12.31.</td><td>신청서 접수와 처리 여부를 확인합니다. 사용기한까지 신청할 수 있는 것으로 읽지 않습니다.</td></tr>
<tr><th scope="row">사용</th><td>2026.7.1.~2027.5.31.</td><td>선정 뒤 사용할 에너지·결제 방식을 확인합니다. 사용기간이 남았다는 사실과 신청 접수 여부를 구분합니다.</td></tr>
</tbody></table></div>
<p>지원기준은 기초생활보장 생계·의료·주거·교육급여 수급 조건과 노인·영유아·장애인 등 세대원 특성 조건을 <strong>함께</strong> 확인하는 구조입니다. 전원이 보장시설 수급자인 세대는 제외됩니다. 나이 하나만으로 대상이라고 판단하지 마세요. <a href="https://www.energyv.or.kr/info/support_info.do" target="_blank" rel="noopener noreferrer">대상·기간 공식 기준 ↗</a></p>
<h2>701,300원을 매달 받는다는 뜻이 아닙니다</h2>
<div class="guide-table"><table><caption>2026년 세대원 수별 바우처 총액 · 월 지급액 아님</caption><thead><tr><th scope="col">1인</th><th scope="col">2인</th><th scope="col">3인</th><th scope="col">4인 이상</th></tr></thead><tbody><tr><td>295,200원</td><td>407,500원</td><td>532,700원</td><td>701,300원</td></tr></tbody></table></div>
<p>이는 해당 지원기간의 총액이며 현금 월급처럼 합산할 금액이 아닙니다. 예를 들어 4인 세대가 생활비 계획을 세울 때 701,300원에 지원 개월 수를 곱하면 지원 규모를 과대평가합니다. 가구원 수와 적용 총액을 먼저 확인하고, 실제 사용 내역·잔액을 따로 관리하는 편이 낫습니다. <a href="https://www.energyv.or.kr/info/support_info.do" target="_blank" rel="noopener noreferrer">금액·세대원 수 기준 ↗</a></p>
<h2>아파트와 등유 난방 가구가 준비할 질문은 다릅니다</h2>
<div class="guide-table"><table><caption>지원금픽의 신청 준비 사례 · 자격 판정 아님</caption><thead><tr><th scope="col">내 상황</th><th scope="col">먼저 확인할 질문</th><th scope="col">그 이유</th></tr></thead><tbody>
<tr><th scope="row">관리비에 난방비가 포함됨</th><td>고지서에서 난방 에너지와 고객 정보를 확인할 수 있나요?</td><td>요금차감을 신청한다면 최근 고지서가 필요합니다. 아파트는 관리비 고지서를 준비하도록 공식 안내합니다.</td></tr>
<tr><th scope="row">등유를 배달받아 사용함</th><td>구입처가 바우처 사용 가맹점이고 카드 결제가 가능한가요?</td><td>국민행복카드 사용은 에너지를 직접 구입하는 방식입니다. 카드 발급과 가맹점 확인을 나눠 준비하세요.</td></tr>
<tr><th scope="row">지난해 지원 후 이사하거나 세대원이 달라짐</th><td>변경된 주소·세대원 정보로 다시 신청했나요?</td><td>지난해 수급 이력만으로 올해 자동 신청을 단정하면 변경 사항이 빠질 수 있습니다.</td></tr>
</tbody></table></div>
<p>방문 신청은 주민등록상 거주지 행정복지센터, 온라인 신청은 복지로에서 안내합니다. 신청서 외에 대리 신청은 위임장·대리인 신분증, 요금차감은 최근 해당 에너지 고지서를 확인하세요. 정보 변동이 있으면 신규·재신청 절차를 확인해야 합니다. <a href="https://www.energyv.or.kr/info/apl_info.do" target="_blank" rel="noopener noreferrer">신청 방법·서류·변경 신청 ↗</a></p>
<p>동절기에는 요금차감과 국민행복카드 중 한 방식을 선택합니다. 요금차감은 도시가스·전기·지역난방 중 선택하고, 2027.5.31.까지 공급자의 차감 신청과 고지서 청구 조건을 확인해야 합니다. 국민행복카드는 사용처·공급자별 결제 방법이 다릅니다. <a href="https://www.energyv.or.kr/info/use_info.do" target="_blank" rel="noopener noreferrer">사용 방식·마감 조건 ↗</a></p>
<h2>다른 겨울 연료비를 받는다면 합산 전에 확인하세요</h2>
<p>2026년 동절기 긴급복지 연료비, 연탄쿠폰, 연탄전환 에너지바우처와는 동절기 중복지원 제한이 있습니다. 하절기 바우처를 사용한 뒤 다른 동절기 지원을 선택하는 경우에는 행정복지센터에 중지 처리 등을 먼저 확인해야 합니다. <a href="https://www.energyv.or.kr/info/support_info.do" target="_blank" rel="noopener noreferrer">중복지원 제한 원문 ↗</a></p>
<p>상담할 때는 ‘현재 받는 지원의 정확한 이름, 적용 기간, 이미 사용한 바우처 여부, 앞으로 사용할 난방 에너지’를 나누어 말해보세요. ‘난방비 지원을 받는다’는 말만으로는 같은 사업인지 다른 사업인지 구분하기 어렵습니다. 선택 전후의 처리 순서를 질문하고, 두 지원금을 모두 받는 것으로 생활비 계획을 먼저 세우지 않는 것이 이 안내의 핵심입니다.</p>
<p>이 글은 일반 에너지바우처 설명입니다. 연탄 보일러 전환 지원은 별도 사업이므로 명칭이 비슷해도 신청 조건을 섞지 마세요.</p>
''', [(ENERGY+'support_info.do','한국에너지공단 · 대상·총액·기간·중복지원'),
      (ENERGY+'apl_info.do','한국에너지공단 · 신청 방법·서류'),
      (ENERGY+'use_info.do','한국에너지공단 · 결제·사용기한')]),
('emergency-vs-livelihood-2026', '긴급복지 생계지원과 생계급여: 2026년 기준과 상담 준비 비교',
 '갑작스러운 위기 상담과 지속적인 생활보장 신청의 차이, 선정기준과 실제 지급액을 구분하는 계산 예시입니다.', '''
<h2>이름에 ‘생계’가 있어도 확인 순서가 다릅니다</h2>
<div class="guide-table"><table><caption>두 제도를 비교할 때의 출발점</caption><thead><tr><th scope="col">질문</th><th scope="col">긴급복지 생계지원</th><th scope="col">기초생활보장 생계급여</th></tr></thead><tbody>
<tr><th scope="row">무엇을 먼저 설명하나요?</th><td>실직·중한 질병·화재 등으로 생계가 어려워진 위기 상황</td><td>가구의 소득·재산을 반영한 소득인정액과 지속적인 생활 곤란</td></tr>
<tr><th scope="row">금액을 읽을 때 주의할 점</th><td>소득 기준 숫자는 지급액이 아닙니다. 지원 종류·가구 규모·기간은 별도로 확인합니다.</td><td>급여기준 금액 전액이 모든 신청자에게 지급되는 것은 아닙니다. 가구 소득인정액을 빼서 산정합니다.</td></tr>
<tr><th scope="row">상담·신청의 시작</th><td>시·군·구, 읍·면·동 또는 보건복지상담센터 129에 위기 상황을 설명</td><td>거주지 읍·면·동에서 가구 조사와 신청 절차 상담</td></tr>
</tbody></table></div>
<p>긴급복지는 위기 가구를 신속하게 돕기 위한 제도이며 현장 확인·지원 뒤 소득·재산 조사와 적정성 심사를 하는 절차가 있습니다. 사후 심사와 환수 가능성도 안내하므로 ‘먼저 지원’이라는 표현을 무심사 지급으로 읽지 마세요. <a href="https://www.mohw.go.kr/menu.es?mid=a10708010100" target="_blank" rel="noopener noreferrer">긴급복지 목적·절차 공식 안내 ↗</a></p>
<h2>75%와 32%를 같은 기준으로 비교하면 생기는 오해</h2>
<p>2026년 긴급복지 소득 기준은 기준 중위소득 75% 이하로, 공식 안내의 1인 가구는 1,923,179원, 4인 가구는 4,871,054원입니다. 위기 사유와 재산·금융재산 기준도 함께 봅니다. 이 숫자는 매달 받는 지원금이 아닙니다. <a href="https://www.mohw.go.kr/menu.es?mid=a10708010100" target="_blank" rel="noopener noreferrer">긴급복지 소득·재산 기준 ↗</a></p>
<p>2026년 생계급여 선정·급여기준은 기준 중위소득 32%이며, 1인 가구 820,556원, 4인 가구 2,078,316원입니다. 급여액은 이 기준에서 소득인정액을 차감해 산정합니다. <a href="https://www.mohw.go.kr/menu.es?mid=a10708010500" target="_blank" rel="noopener noreferrer">생계급여 공식 기준·계산 원칙 ↗</a></p>
<p>따라서 ‘75%보다 소득이 낮으니 두 제도를 다 받을 수 있다’거나 ‘기준이 더 높은 쪽이 더 큰 금액을 준다’고 결론 내릴 수 없습니다. 두 숫자는 제도의 목적과 조사 조건 안에서 읽어야 합니다. 동시 신청·지원 조정 여부는 현재 받는 급여를 밝히고 담당기관에 확인하세요.</p>
<h2>가상의 4인 가구로 계산 원리를 확인해보세요</h2>
<p>이미 기관이 산정한 <strong>소득인정액이 1,000,000원</strong>이라고 가정하면, 생계급여 계산 원칙에 따른 차액은 <strong>2,078,316원 − 1,000,000원 = 1,078,316원</strong>입니다. 이는 산식을 설명하기 위한 가상 예시입니다. 실제 가구의 선정이나 지급액을 보장하지 않습니다.</p>
<p>여기서 1,000,000원을 통장에 들어온 월급으로 바꾸어 대입하면 같은 결과를 보장할 수 없습니다. 소득인정액은 실제 월급과 다른 개념이기 때문입니다. 본인이 계산한 금액을 지급 예정액으로 기록하기보다, 상담에서 ‘제 가구 소득인정액은 어떻게 산정되었나요?’라고 묻는 데 이 예시를 쓰세요.</p>
<h2>상황별로 상담 질문을 준비하면 중복 설명을 줄일 수 있습니다</h2>
<div class="guide-table"><table><caption>지원금픽의 상담 준비 사례 · 접수 자격 판정 아님</caption><thead><tr><th scope="col">상황</th><th scope="col">설명할 내용</th><th scope="col">확인할 질문</th></tr></thead><tbody>
<tr><th scope="row">갑자기 실직해 당장 생활비가 부족함</th><td>소득이 끊긴 시점, 가구 상황, 현재 다른 지원을 받는지</td><td>긴급복지 위기 사유와 조사 기준에 해당하는지, 지금 필요한 자료가 무엇인지</td></tr>
<tr><th scope="row">소득이 계속 적어 생활이 어려움</th><td>가구 구성, 소득·재산의 상황, 이미 신청한 급여 여부</td><td>생계급여 신청과 가구 조사 절차, 소득인정액 산정에 반영할 정보</td></tr>
<tr><th scope="row">생계급여 심사를 기다리는 중 새 위기가 생김</th><td>진행 중인 신청과 새 위기 상황을 함께 알림</td><td>긴급 지원 상담이 가능한지, 기존 급여와 조정할 사항이 있는지</td></tr>
</tbody></table></div>
<p>이 표는 별도의 필수서류 목록이 아닙니다. 모든 서류를 미리 발급하느라 상담을 늦추기보다, 상황을 먼저 설명하고 해당 가구에 필요한 증빙·제출기한을 요청하세요. 개인정보와 증빙은 담당기관의 공식 창구로만 제출하세요.</p>
<h2>같은 정부 사이트라도 연도를 확인해야 합니다</h2>
<p>이 글은 긴급복지 공식 페이지의 2026.6.30. 수정 안내와 생계급여 페이지의 2026.9.23. 수정 안내를 2026.11.17. 대조했습니다. 예전 검색 결과의 기준을 현재 금액과 섞지 마세요. 내년 기준이나 추가 변경이 발표되면 해당 연도 공고를 다시 확인해야 합니다.</p>

''', [(EMERGENCY,'보건복지부 · 긴급복지지원'), (LIVELIHOOD,'보건복지부 · 기초생활보장 급여수준')])
]

ARTICLES += FOCUS_ARTICLES
ARTICLES += TAX_ARTICLES
ARTICLES += RECORD_ARTICLES
ARTICLES += BIRTH_ARTICLES
ARTICLES += CULTURE_PENSION_ARTICLES
ARTICLES += FOREST_TRANSPORT_ARTICLES
ARTICLES += WINTER_ARTICLES
ARTICLES += HOUSING_SERVICE_ARTICLES
ARTICLES += CLAIM_ARTICLES
ARTICLES += EDUCATION_BUSINESS_ARTICLES
ARTICLES += MATERNITY_ARTICLES
ARTICLES += CHILD_ARTICLES
ARTICLES += MATERNAL_SERVICE_ARTICLES
ARTICLES += RENTAL_GUARANTEE_ARTICLES
ARTICLES += LEGACY_YOUTH_SAVINGS_ARTICLES
ARTICLES += YOUTH_SUBSCRIPTION_ARTICLES
ARTICLES += DIDIMDOL_ARTICLES
ARTICLES += SCHOOL_WELFARE_ARTICLES
ARTICLES += REVIEWED_AMOUNT_ARTICLES
ARTICLES += SUNCHANG_BIRTH_ARTICLES

BENEFIT_ARTICLES = {
    '626000000649': 'busan-child-care-fee-vs-copayment-2026',
    '557000000250': 'jeungpyeong-insurance-contract-vs-claim-2026',
    '875000000016': 'school-welfare-vs-education-benefit-2026',
    '477000000110': 'sunchang-birth-total-vs-installments-2026',
    'SD0000015525': 'school-welfare-vs-education-benefit-2026',
    'B55140800003': 'didimdol-cap-collateral-and-closing-2026',
    '161300000088': 'youth-housing-account-announcement-tax-conversion-2026',
    'SD0000011848': 'youth-mutual-aid-closed-enrollment-maturity-2026',
    '161300000103': 'rental-guarantee-fee-cap-and-dates-2026',
    **dict.fromkeys(('PTR000050390','628000000111'), 'maternal-service-application-use-refund-2026'),
    '628000000739': 'incheon-child-dream-birth-year-2026',
    **dict.fromkeys(('628000000735','628000000744'), 'incheon-pregnancy-transport-vs-postpartum-2026'),
    **dict.fromkeys(('SD0000004508','999000000090','134200005002','GES000000110','GES000000100'), 'scholarships-vs-student-loan-steps-2026'),
    **dict.fromkeys(('SD0000007429','SD0000018904'), 'small-business-loan-vs-guarantee-2026'),
    '999000000008': 'leave-benefit-claim-checklist-2026',
    'WII000001460': 'leave-benefit-claim-checklist-2026',
    'SD0000015536': 'unemployment-benefit-vs-pension-credit-2026',
    'B55201500004': 'unemployment-benefit-vs-pension-credit-2026',
    '999000000024': 'long-term-lease-notice-checklist-2026',
    'SD0000016138': 'local-social-service-application-vs-use-2026',
    '424000000006': 'winter-bills-vs-home-improvement-2026',
    'B55353000001': 'energy-voucher-2026',
    '135200005003': 'emergency-vs-livelihood-2026',
    'WII000001410': 'emergency-vs-livelihood-2026',
    '135200000120': 'child-allowance-2026',
    '336000000096': 'housing-benefit-2026',
    '105100000001': 'earned-income-credit-late-2026',
    '646000000145': 'women-farmer-voucher-records-2026',
    '629000000182': 'women-farmer-voucher-records-2026',
    '135200005013': 'youth-savings-contribution-2026',
    '135200005015': 'first-meeting-vs-parent-benefit-2026',
    '305000000113': 'first-meeting-vs-parent-benefit-2026',
    '319000000130': 'first-meeting-vs-parent-benefit-2026',
    '442000000135': 'first-meeting-vs-parent-benefit-2026',
    '137100000236': 'culture-card-deadlines-2026',
    '648000001107': 'culture-card-deadlines-2026',
    'B55151000066': 'culture-card-deadlines-2026',
    'SSE000000170': 'basic-pension-amounts-2026',
    '140000000176': 'forest-voucher-application-vs-use-2026',
    '641000000139': 'gyeonggi-child-transport-cap-2026',
}


ARTICLE_REVIEW_DATES = {'busan-child-care-fee-vs-copayment-2026':'2026-11-19', 'jeungpyeong-insurance-contract-vs-claim-2026':'2026-11-19', 'sunchang-birth-total-vs-installments-2026': '2026-11-19', 'school-welfare-vs-education-benefit-2026': '2026-11-19', 'didimdol-cap-collateral-and-closing-2026': '2026-11-19', 'youth-housing-account-announcement-tax-conversion-2026': '2026-11-18', 'youth-mutual-aid-closed-enrollment-maturity-2026': '2026-11-18', 'rental-guarantee-fee-cap-and-dates-2026': '2026-11-18', 'maternal-service-application-use-refund-2026': '2026-11-18', 'incheon-child-dream-birth-year-2026': '2026-11-18', 'incheon-pregnancy-transport-vs-postpartum-2026': '2026-11-18', 'leave-benefit-claim-checklist-2026': '2026-11-18'}


def related_analysis(sid, row=None):
    slug = BENEFIT_ARTICLES.get(sid)
    article = next((a for a in ARTICLES if a[0] == slug), None)
    if not article:
        return ''
    fragment = '#education-informatization' if sid == '875000000016' else ''
    description = 'PC·통신비의 지원 항목·지역별 기준·직접 납부 방식을 대조합니다.' if fragment else article[2]
    return (review_advisory(row or {}) + source_advisory(row or {}) + forest_source_advisory(row or {}) + '<section class="detail-block"><h2>조건을 해석하는 사업별 해설</h2><p>'
            + escape(description) + '</p><a class="editorial-link" href="../../guides/'
            + article[0] + '.html' + fragment + '">' + escape(article[1]) + ' →</a><p class="source-meta">'
            + ARTICLE_REVIEW_DATES.get(slug, REVIEWED) + ' 공식 자료 대조 · 2026년 기준</p></section>')


def coverage_report(search, rows):
    """Coverage is evidence of what exists, never a Google quality score."""
    held = search['heldReasons']
    linked = sorted(sid for sid in BENEFIT_ARTICLES if sid in rows and sid not in held)
    matched = set(search['guideIds'])
    return {
        'version': 1, 'asOf': REVIEWED,
        'indexableDetails': search['indexableDetails'],
        'matchedPreparationGuides': len(matched),
        'detailsWithoutMatchedPreparationGuide': search['indexableDetails'] - len(matched),
        'substantiveAnalysisArticles': len(ARTICLES),
        'analysisLinkedBenefitIds': linked,
        'heldBenefitAnalysisIds': sorted(sid for sid in BENEFIT_ARTICLES if sid in rows and sid in held),
        'siteWideContentValueReview': 'incomplete',
        'resubmissionRecommended': False,
        'reason': 'Original analysis exists for a small subset; site-wide value has not been demonstrated.',
        'cautions': [
            'Coverage counts are not AdSense approval thresholds or individual page quality judgments.',
            'A matched preparation guide alone does not prove substantive original value.',
            'Technical test success does not prove low-value-content remediation.',
            'No records deleted or indexing rules changed by this report.'
        ]
    }
