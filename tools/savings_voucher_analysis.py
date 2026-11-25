"""Record-specific reading aids for actual source ambiguities found in review."""

VOUCHER_PDF = 'https://gwangyang.go.kr/boardDownload.es?bid=0170&list_no=196475&seq=1'
VOUCHER_ROUNDS_PDF = 'https://gwangyang.go.kr/boardDownload.es?bid=0174&list_no=197073&seq=1'
SAVINGS = 'https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309724_1122.html'
API_VOUCHER_A = 'https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1003085&bnefType=all&svcId=646000000145'
API_VOUCHER_B = 'https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1005831&bnefType=all&svcId=629000000182'

RECORD_ARTICLES = [
('women-farmer-voucher-records-2026', '여성농업인 행복바우처: 같은 이름의 자료와 지역별 공고를 구분하는 법',
 '대상·금액·접수기관이 다른 두 API 자료를 비교하고, 광양시 2026년 안내의 연령·신청기간·사용기간을 나누어 확인합니다.', '''
<h2>이름보다 주소지와 문의 창구를 먼저 확인하세요</h2>
<p>같은 이름의 지원 안내라도 대상·금액·문의 창구가 다를 수 있습니다. 아래 두 공식 연결자료도 문의 지역과 지원 내용이 다릅니다. 큰 금액 쪽이 나에게 적용된다고 고르기 전에 주소지에서 어느 공고를 확인해야 하는지 찾아보세요.</p>
<div class="guide-table"><table><caption>공식 연결자료의 원문 비교 · 현행 자격 확정표 아님</caption><thead><tr><th scope="col">항목</th><th scope="col">전남도청·시군 문의 안내</th><th scope="col">광주 자치구 문의 안내</th></tr></thead><tbody>
<tr><th scope="row">나이·대상 표기</th><td>20~75세 여성농어업인</td><td>19세 이상~75세 미만 여성농업인</td></tr>
<tr><th scope="row">금액 표기</th><td>연 20만원권</td><td>연 10만원 카드: 지원 8만원·자부담 2만원</td></tr>
<tr><th scope="row">문의 창구 표기</th><td>전남도청·목포·여수·광양 등</td><td>동구·서구·남구·북구·광산구</td></tr>
<tr><th scope="row">기간 표기</th><td>접수기관별 상이</td><td>4~6월 중 별도 신청기간</td></tr>
</tbody></table></div>
<p>표의 지역 이름은 각 자료의 문의 창구를 구분하는 표시이며 지원 지역을 확정하는 분류가 아닙니다. 이 표만으로 현재 신청 자격이나 접수 가능 여부를 판단하지 말고 거주지의 해당 연도 공고를 확인하세요. <a href="https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1003085&amp;bnefType=all&amp;svcId=646000000145" target="_blank" rel="noopener noreferrer">전남도청·시군 문의 안내의 공식 자료 ↗</a> · <a href="https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1005831&amp;bnefType=all&amp;svcId=629000000182" target="_blank" rel="noopener noreferrer">광주 자치구 문의 안내의 공식 자료 ↗</a></p>
<h2>광양시 2026년 공고에는 80세까지로 안내되어 있습니다</h2>
<p>광양시 다압면이 배포한 2026년 안내는 2026년 1월 1일 기준 도내 1년 이상 거주·실제 영농·사업년도 20~80세 요건을 함께 제시하고, 연 20만원을 안내합니다. API 첫째 자료의 75세 상한과 달라 해당 상세의 현재 조건 표시는 보류했습니다. 둘째 자료까지 같은 나이로 바꾸거나 다른 지역에 이 기준을 확대하지 않습니다. <a href="https://gwangyang.go.kr/boardDownload.es?bid=0170&amp;list_no=196475&amp;seq=1#page=26" target="_blank" rel="noopener noreferrer">광양시 공식 PDF · 파일 26쪽 / 인쇄 쪽 24 ‘여성농업인 행복바우처’ ↗</a></p>
<p>예를 들어 78세 이용자는 오래된 75세 표기만 보고 포기하기 전에 본인 거주지의 해당 연도 공고를 찾아야 합니다. 반대로 같은 이름의 다른 지역 자료에 80세를 그대로 대입해도 된다는 뜻은 아닙니다. 주소지와 나이 기준일을 함께 제시해 담당기관에 문의하세요.</p>
<h2>신청기한과 이미 받은 포인트의 사용기한은 다릅니다</h2>
<p>광양시 다압면 자료의 접수 기간은 2026년 1월 16일~2월 27일이고, 받은 포인트의 사용기한은 2026년 12월 31일입니다. 이미 포인트를 받았다면 사용기한을 먼저 확인하세요.</p>
<p>광양시의 다른 공식 자료에는 <strong>2차 접수 예정 기간이 2026년 4월 1일~30일</strong>로 적혀 있습니다. 다만 1차 접수에서 사업량을 모두 쓰면 2차를 진행하지 않는다는 조건이 붙었습니다. 이 자료로 실제 2차 접수가 열렸는지 확인할 수는 없습니다. 올해 신청하지 못했다면 거주지 읍면동에 새 모집 공고가 있는지 확인하세요.</p>
<h2>금액 비교보다 먼저 준비할 질문</h2>
<div class="guide-table"><table><caption>관할 창구에 물을 내용</caption><thead><tr><th scope="col">상황</th><th scope="col">질문</th></tr></thead><tbody>
<tr><th scope="row">두 자료의 금액이 다르게 보임</th><td>제 주소지와 농어업 유형에는 어느 공고가 적용되며, 카드 총액과 자부담은 각각 얼마인가요?</td></tr>
<tr><th scope="row">다른 문화복지 지원을 이용 중</th><td>받고 있는 지원의 정확한 이름을 밝히고, 중복 제한·선택 절차가 있는지 확인합니다.</td></tr>
<tr><th scope="row">올해 주소나 직업이 바뀜</th><td>거주 기준일·거주기간과 영농·사업자등록·상근직 제외 조항을 어떻게 확인하나요?</td></tr>
</tbody></table></div>
<p>위 광양시 자료는 유사 복지서비스, 직업·사업자등록, 농외소득 등의 제외 조항도 담고 있습니다. 일부 나이·금액이 맞는다는 이유만으로 선정되었다고 판단하지 말고 전체 공고를 읽으세요. 필요한 서류는 접수기관에서 요청한 양식을 사용하고 증빙을 지원금픽에 제출하지 않습니다.</p>
''', [(API_VOUCHER_A,'정부24 OpenAPI 첫째 서비스 연결'), (API_VOUCHER_B,'정부24 OpenAPI 둘째 서비스 연결'),
      (VOUCHER_PDF,'광양시 다압면 2026년 공식 안내 · 인쇄 쪽 24'),
      (VOUCHER_ROUNDS_PDF,'광양시 2026년 공식 안내 · 인쇄 쪽 5 · 2차 접수 조건')]),
('youth-savings-contribution-2026', '2026 청년내일저축계좌: 저축액·정부 월 30만원·만기 조건을 나누어 읽기',
 '정부 지원을 모든 본인 납입액의 세 배로 계산하지 않고, 신규 모집과 가입 후 유지·만기 절차를 구분합니다.', '''
<h2>‘1:3’이라는 짧은 설명을 모든 납입액에 곱하지 마세요</h2>
<p>API는 본인 월 10~50만원, 정부 월 30만원을 안내하면서 ‘1:3’이라는 요약도 사용합니다. 보건복지부가 복지로에 제공한 2026년 발표는 정부 지원을 <strong>월 30만원</strong>으로 설명합니다. 본인 저축액을 20만원으로 늘렸다고 정부가 60만원을 붙여준다는 뜻으로 읽으면 안 됩니다. <a href="https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309724_1122.html" target="_blank" rel="noopener noreferrer">복지로 · 보건복지부 2026년 발표 ↗</a></p>
<div class="guide-table"><table><caption>36개월 정상 납입·만기 요건 충족을 가정한 산식 예시 · 이자·추가 조정 제외</caption><thead><tr><th scope="col">본인 월 저축</th><th scope="col">본인 36개월</th><th scope="col">정부 월 30만원 × 36</th><th scope="col">단순 합계</th></tr></thead><tbody>
<tr><th scope="row">10만원</th><td>360만원</td><td>1,080만원</td><td>1,440만원</td></tr>
<tr><th scope="row">20만원</th><td>720만원</td><td>1,080만원</td><td>1,800만원</td></tr>
</tbody></table></div>
<p>둘째 줄은 지급 예정액이 아니라 산식을 설명하는 가상 예시입니다. 납입을 늘렸을 때 합계 차이는 본인 저축 차이이며, 정부 지원이 비례해서 늘어난 결과가 아닙니다. 실제 적립·유지·해지 조건과 개인 지급액은 기관에서 확인해야 합니다.</p>
<h2>2026년 신규 모집과 이미 가입한 사람의 일정은 다릅니다</h2>
<p>확인한 신규 모집은 2026.5.4.~5.20.이었습니다. 이 접수 기간은 현재 경과했습니다. 11월에도 제도 설명이나 적립 안내가 남아 있다는 이유로 신규 신청이 가능하다고 판단하지 마세요. 이 글은 추가 모집이나 다음 해 일정을 확인한 안내가 아닙니다.</p>
<p>보건복지부 발표는 2026년 신규 지원을 기준 중위소득 50% 이하의 일하는 청년에 집중한다고 설명합니다. 이전 연도의 100% 기준을 올해 신규 모집에 그대로 적용하거나, 이 발표만으로 과거 가입자의 약정이 자동 변경됐다고 판단하지 마세요. 정확한 가입연도·신청 이력을 밝히고 적용 기준을 확인하는 편이 좋습니다. <a href="https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309724_1122.html" target="_blank" rel="noopener noreferrer">2026년 대상·모집 발표 ↗</a></p>
<h2>만기는 기간만 채운다고 확정되지 않습니다</h2>
<p>공식 발표는 근로활동 지속, 본인 저축 유지, 자립역량교육 10시간, 자금활용계획서 제출을 만기 지급 요건으로 안내합니다. 납입 기록과 교육·제출 상태를 따로 점검해야 합니다. 실직·질병 등으로 납입이 어려울 때의 적립중지 제도도 설명하므로 혼자 미납 처리로 넘기기 전에 담당기관에서 승인 절차를 확인하세요.</p>
<div class="guide-table"><table><caption>신청·유지 상태에 따라 준비할 내용</caption><thead><tr><th scope="col">내 상황</th><th scope="col">확인할 일</th></tr></thead><tbody>
<tr><th scope="row">올해 신청한 적이 없음</th><td>확인한 접수 기간은 경과했습니다. 새 공식 공고가 있는지 확인하고 임의의 다음 접수일을 달력에 넣지 않습니다.</td></tr>
<tr><th scope="row">신청했지만 결과가 불명확함</th><td>접수일·신청 경로를 확인해 기관에 선정 결과와 후속 절차를 묻습니다. 지원금픽의 신청 메모는 기관 접수가 아닙니다.</td></tr>
<tr><th scope="row">가입 후 소득활동이 중단됨</th><td>가입연도·중단 사유·예상 기간을 밝히고 적립중지 신청 가능 여부, 증빙, 승인 뒤 적립 일정을 확인합니다.</td></tr>
<tr><th scope="row">만기가 가까움</th><td>교육 이수 내역과 자금활용계획서 제출 상태, 누락 납입 여부를 담당기관에 확인합니다.</td></tr>
</tbody></table></div>
<p>신규 접수 당시에는 복지로 또는 주소지 시군구 내 읍면동 행정복지센터를 안내했습니다. 제출 서류·양식은 복지로와 공식 자산형성포털의 해당 공고에서 확인해야 하며, 문의는 자산형성지원콜센터 1522-3690이나 담당 행정복지센터를 이용할 수 있습니다. 이 글은 금융상품 가입 권유나 개인 자격 판정이 아닙니다. <a href="https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309724_1122.html" target="_blank" rel="noopener noreferrer">신청 경로·유지 요건·문의 공식 안내 ↗</a></p>
''', [(SAVINGS,'복지로 · 보건복지부 제공 2026년 신규 모집·유지 요건')])
]
