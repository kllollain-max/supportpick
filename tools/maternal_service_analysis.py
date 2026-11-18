"""Separate service application, voucher use, and local reimbursement clocks."""
MOHW = 'https://www.mohw.go.kr/menu.es?mid=a10711020100'
FAQ = 'https://129.go.kr/faq/faq03.do'
HEALTH = 'https://www.e-health.go.kr/gh/heSrvc/selectBbsDtlViewInfo.do?bbsId=U00322&bbsNo=381829&bbsSeCd=Z6&menuId=200040'
INCHEON = 'https://www.incheon.go.kr/earlychild/EC020103'
INCHEON_API = 'https://www.incheon.go.kr/icbenefit/ICB020201/view?srvcId=628000000111'

MATERNAL_SERVICE_ARTICLES = [
('maternal-service-application-use-refund-2026',
 '산모·신생아 건강관리: 신청 60일·이용 90일·인천 환급 기한 구분',
 '출산일·퇴원일·서비스 종료일 중 어떤 날부터 세는지, 바우처 신청과 본인부담금 환급을 구분하는 준비표입니다.', '''
<h2>같은 ‘60일’이어도 기준일이 다릅니다</h2>
<p>건강관리사 방문 서비스를 신청하는 절차와 이미 낸 본인부담금의 지역 지원을 신청하는 절차는 별개입니다. 출산일만 달력에 적으면 서비스가 끝난 뒤의 환급 접수를 놓칠 수 있습니다. 아래 표는 국가 사업의 일반 기준과 인천시의 본인부담금 지원을 대조한 준비 안내이며, 다른 지역의 환급 기한까지 같다는 뜻은 아닙니다.</p>
<div class="guide-table"><table><caption>신청·사용·사후 지원의 세 시계</caption><thead><tr><th scope="col">구분</th><th scope="col">기준일과 기한</th><th scope="col">준비할 일</th></tr></thead><tbody>
<tr><th scope="row">국가 서비스 신청</th><td>일반적으로 출산예정일40일 전부터 출산일로부터60일까지</td><td>주소지 보건소 또는 공식 온라인 창구에서 접수와 지원결정을 확인합니다.</td></tr>
<tr><th scope="row">바우처 사용</th><td>원칙적으로 출산일로부터90일 이내</td><td>선택한 제공기관의 실제 이용 일정과 바우처 만료일을 따로 확인합니다.</td></tr>
<tr><th scope="row">인천 본인부담금 지원 신청</th><td>서비스(바우처 이용) 종료 후60일 이내</td><td>인천 거주·사업 이용 조건을 확인하고 영수증 등으로 별도 접수합니다.</td></tr>
</tbody></table></div>
<p>국가 사업의 신청기한은 <a href="https://www.mohw.go.kr/menu.es?mid=a10711020100" target="_blank" rel="noopener noreferrer">보건복지부 정책 안내</a>, 사용기한·예외는 <a href="https://129.go.kr/faq/faq03.do" target="_blank" rel="noopener noreferrer">129의2026.10.29. 답변</a>, 인천 환급은 <a href="https://www.incheon.go.kr/earlychild/EC020103" target="_blank" rel="noopener noreferrer">인천시 현재 안내</a>를 대조했습니다. 지원금픽의 수집 원문 중 일반 신청을 출산 후30일로 적은 자료는 현재 안내와 달라 본문 공개를 보류하고 이 해설과 공식 기관으로 연결했습니다. 원본은 보존합니다.</p>
<h2>퇴원 후30일 신청과90일 사용을 섞지 마세요</h2>
<div class="guide-table"><table><caption>예외 상황에서 담당기관에 확인할 기준일</caption><thead><tr><th scope="col">상황</th><th scope="col">신청 기준</th><th scope="col">사용 기준</th></tr></thead><tbody>
<tr><th scope="row">미숙아·선천성이상아 출산 등으로 입원</th><td>신생아 퇴원일로부터30일 이내. 입·퇴원일 증빙 확인</td><td>퇴원일로부터90일 이내. 삼태아 이상 연장 유형은100일 이내이며 출산 후2년 경과 시 소멸</td></tr>
<tr><th scope="row">임신16주 이후 유산·사산</th><td>확인일로부터30일 이내. 의사소견서·확인서 또는 사산 증빙 확인</td><td>확인일로부터60일 이내. 삼태아 이상 연장 유형은100일 이내</td></tr>
</tbody></table></div>
<p>일반 출산의 사용기한도 삼태아 이상 ‘연장’ 유형은100일로 구분됩니다. 예외를 모든 출산 가정에 적용하거나, 사용기한까지 신청해도 된다고 읽지 마세요. <a href="https://129.go.kr/faq/faq03.do" target="_blank" rel="noopener noreferrer">신청기한과 바우처 유효기간을 각각 다룬129 답변</a>과 <a href="https://www.e-health.go.kr/gh/heSrvc/selectBbsDtlViewInfo.do?bbsId=U00322&amp;bbsNo=381829&amp;bbsSeCd=Z6&amp;menuId=200040" target="_blank" rel="noopener noreferrer">e보건소2026 안내</a>를 출발점으로 본인 사유·증빙과 적용일을 보건소에 확인하세요.</p>
<h2>서비스 이용권은 일괄 현금 지급과 다릅니다</h2>
<p>국가 사업은 건강관리사가 출산 가정을 방문하는 서비스 이용권입니다. 수급·차상위 또는 가구 건강보험료를 통한 소득 기준과 지역별 예외 기준을 확인합니다. 정해진 소득 비율을 넘었다는 이유만으로 모든 지역에서 제외라고 결론 내리거나, 출산만 하면 자동 선정된다고 판단하지 마세요.</p>
<p>태아유형·출산순위·소득구간과 단축·표준·연장 선택에 따라 서비스기간과 정부지원금이 달라집니다. 부처 안내의 기간 범위는5~40일이며 서비스가격에서 정부지원금을 뺀 차액이 본인부담금입니다. 기관에 계약정보가 등록되어 바우처가 생성된 뒤에는 서비스기간 변경이 제한되므로 계약 전 유형·가격·이용 가능 날짜를 확인하세요. 부처 페이지에2025년 가격표가 남아 있어 이를2026년 확정액으로 복제하지 않았습니다. 본인 유형의2026년 표와 실제 계약금액은 보건소·제공기관에 확인합니다. <a href="https://www.mohw.go.kr/menu.es?mid=a10711020100" target="_blank" rel="noopener noreferrer">사업·계약·비용 구조 공식 안내</a></p>
<h2>인천 환급을 준비할 때는 납부 자료를 따로 챙깁니다</h2>
<p>인천시 안내는 인천에 주민등록을 둔 상태에서 서비스를 받고 계속 인천에 거주하는 이용자를 대상으로 설명합니다. 중위소득150% 이하 및 예외 대상 등 본인 조건을 확인하세요. 본인부담금 일부 지원이 기본이며 셋째아 이상 ‘단축’ 이용의 전액 지원을 모든 유형에 확대하지 않습니다.</p>
<p>신청서·신분증·본인부담금 지불영수증·통장 사본이 수집 원문에 제시됩니다. 영수증의 이용자·서비스 기간·납부금액과 실제 종료일을 대조하고 보건소의 추가 자료를 확인하세요. 시청 사업 안내는 보건소 방문을, 혜택 원문은 방문 또는 정부24를 안내하므로 본인 주소지의 현재 접수 경로를 먼저 확인하는 편이 안전합니다. <a href="https://www.incheon.go.kr/icbenefit/ICB020201/view?srvcId=628000000111" target="_blank" rel="noopener noreferrer">인천 혜택의 서류·접수 안내</a></p>
<ol><li>서비스 신청: 출산예정일·출산일 또는 예외 기준일, 주소·소득·가구 증빙을 정리합니다.</li><li>선정 후 이용: 제공기관 계약, 본인부담금, 실제 서비스 시작·종료와 바우처 만료를 확인합니다.</li><li>인천 사후 지원: 인천 조건·서비스 종료일·영수증과 별도 신청 완료·결정·입금을 확인합니다.</li></ol>
<p>세 단계를 각각 기록하면 서비스 예약을 보건소 접수 완료로, 사후 지원 신청을 계좌 입금 완료로 오해하지 않을 수 있습니다. 지원금픽에 의료 증빙·신분증·통장 사본을 제출할 필요는 없습니다. 공식 접수처에 제출하세요.</p>
''', [(MOHW,'보건복지부 · 일반 신청60일·서비스·계약·비용 구조'),
      (FAQ,'보건복지상담센터129 ·2026.10.29. 신청·이용 예외'),
      (HEALTH,'e보건소 ·2026 국가사업·신청 경로·예외 증빙'),
      (INCHEON,'인천광역시 · 본인부담금 지원·서비스 종료 후60일'),
      (INCHEON_API,'인천광역시 ·628000000111 원문·구비서류')])
]
