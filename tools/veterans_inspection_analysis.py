"""Source-reviewed guidance on the TS vehicle inspection fee discount."""

TS_FEES = 'https://main.kotsa.or.kr/portal/contents.do?menuCode=01010102'
TS_FAQ = 'https://main.kotsa.or.kr/portal/bbs/faq_list.do?cateCode=C01&menuCode=04010000'

VETERANS_INSPECTION_SLUG = 'veterans-vehicle-inspection-discount-2026'

VETERANS_INSPECTION_ARTICLE = (
    VETERANS_INSPECTION_SLUG,
    '국가유공자 자동차검사 수수료 감면과 전산조회 실패 시 환불 절차',
    '보철용 자동차표지, 공단 검사소, 수검 후 60일 이내의 환불 조건을 확인하세요.',
    """
<h2>예약 전에 차량과 검사소를 확인하세요</h2>
<p>한국교통안전공단(TS)의 정기·종합검사 수수료 안내에서 국가유공자 항목은 <strong>국가유공자 등 보철용 자동차표지가 발급된 차량</strong>에 정상수수료의 80% 감면을 안내합니다. 감면 대상 차량인지부터 확인하세요. 비사업용 차량 기준이 적용되며, 국가유공자 감면 대상인 개인택시는 예외입니다. 다른 감면과 중복 적용되지 않습니다.</p>
<p>예약 화면에서 검사소가 공단 검사소인지 확인하세요. 지정정비사업자의 검사 수수료는 공단과 다를 수 있으므로, 해당 검사소에 적용 요금과 감면 여부를 먼저 문의하세요.</p>
<h2>접수와 환불 요청 때 확인할 사항</h2>
<div class="guide-table"><table>
<caption>전산조회 결과에 따른 다음 행동</caption>
<thead><tr><th scope="col">상황</th><th scope="col">수수료 처리</th><th scope="col">확인할 질문</th></tr></thead>
<tbody>
<tr><th scope="row">접수 전산조회 가능</th><td>감면 대상 확인 후 적용</td><td>이 차량에 적용된 정상수수료와 최종 결제액은 얼마인가요?</td></tr>
<tr><th scope="row">접수 전산조회 불가</th><td>정상수수료 납부</td><td>등록 누락 가능성은 어디에 확인하고, 환불 요청은 어느 창구에서 하나요?</td></tr>
<tr><th scope="row">수검 후 전산조회 가능</th><td>수검 후 60일 이내, 요청 시점에 조회가 가능하면 감면액 환불</td><td>제 검사일 기준 요청 기한과 필요한 정보는 무엇인가요?</td></tr>
</tbody></table></div>
<p>검사 당일에는 감면 대상 여부를 접수 직원에게 알려 전산조회를 요청하세요. 정상수수료를 냈다면 검사일과 결제 내역을 확인하고 공단에 환불 창구를 문의하세요. 공단 안내에는 <strong>수검 후 60일 이내이며 환불 요청 시점에 전산조회가 가능할 것</strong>이라는 조건이 함께 있습니다. 정확한 기한과 증빙은 공단 검사소 또는 고객콜센터(1577-0990)에서 확인할 수 있습니다.</p>
<h2>감면액과 실제 결제액 계산 예시</h2>
<p>정상수수료가 30,000원이라고 가정하면 80%인 24,000원이 감면되고 6,000원이 결제액으로 남습니다. 이 금액은 계산 예시입니다. 실제 검사 수수료는 검사 종류와 차량에 맞춰 공식 표에서 확인하세요.</p>
""",
    [(TS_FEES, '한국교통안전공단 · 검사 수수료와 감면 기준'),
     (TS_FAQ, '한국교통안전공단 · 자동차검사 자주 묻는 질문')],
)
