"""One dated, source-checked tax-benefit explanation, separate from API facts."""
NEWS='https://nts.go.kr/nts/na/ntt/selectNttInfo.do?bbsId=1028&mi=2201&nttSn=1355806'
ELIGIBILITY='https://i.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&mi=2452'
PROCESS='https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&mi=2450'
CALENDAR='https://www.korea.kr/multi/visualNewsView.do?newsId=148974865'

TAX_ARTICLES=[
('earned-income-credit-late-2026','2026 근로·자녀장려금 기한 후 신청: 귀속연도·12월 1일·감액 확인',
 '2025년 소득에 대한 기한 후 신청과 2026년 소득의 반기 신청을 구분하고, 소득·재산 기준과 실제 지급액을 나누어 읽습니다.', '''
<h2>먼저 ‘어느 해 소득’인지 확인하세요</h2>
<p>국세청은 2026년 11월 2일 발표에서 <strong>2025년 소득에 대한 근로·자녀장려금 미신청 가구</strong>의 기한 후 신청을 2026년 12월 1일까지 안내했습니다. 지원금픽 API에 정기·반기의 일반적인 월·일만 적혀 있다고 해서 올해의 기한 후 절차까지 끝난 것으로 판단하지 마세요. <a href="https://nts.go.kr/nts/na/ntt/selectNttInfo.do?bbsId=1028&amp;mi=2201&amp;nttSn=1355806" target="_blank" rel="noopener noreferrer">국세청의 2026.11.2. 안내 ↗</a></p>
<div class="guide-table"><table><caption>2025년 귀속분의 2026년 신청 일정</caption><thead><tr><th scope="col">구분</th><th scope="col">기간</th><th scope="col">읽는 기준</th></tr></thead><tbody>
<tr><th scope="row">정기 신청</th><td>2026.5.1.~6.1.</td><td>해당 정기 신청기간 안내입니다.</td></tr>
<tr><th scope="row">기한 후 신청</th><td>2026.6.2.~12.1.</td><td>해당 귀속분을 신청하지 않았다면 요건과 신청 이력을 확인합니다.</td></tr>
<tr><th scope="row">2026.12.2. 이후</th><td>위 기한 후 신청기간 경과</td><td>다른 귀속연도나 반기 일정과 섞어 연장된 것으로 읽지 않습니다.</td></tr>
</tbody></table></div>
<p>위 일정은 2025년 귀속분에 관한 것입니다. 2026년 소득을 대상으로 하는 반기 신청과는 확인할 귀속연도가 다릅니다. 신청내역 화면에서 ‘근로장려금’이라는 이름뿐 아니라 귀속연도와 신청 유형을 함께 확인하세요. <a href="https://www.korea.kr/multi/visualNewsView.do?newsId=148974865" target="_blank" rel="noopener noreferrer">국세청의 신청기간별 안내 ↗</a></p>
<h2>소득 기준은 지급액이 아닙니다</h2>
<div class="guide-table"><table><caption>2025년 부부합산 연간 총소득 기준 · 금액 미만 조건</caption><thead><tr><th scope="col">가구 구분</th><th scope="col">근로장려금</th><th scope="col">자녀장려금</th></tr></thead><tbody>
<tr><th scope="row">단독</th><td>2,200만원 미만</td><td>해당 없음</td></tr>
<tr><th scope="row">홑벌이</th><td>3,200만원 미만</td><td>7,000만원 미만</td></tr>
<tr><th scope="row">맞벌이</th><td>4,400만원 미만</td><td>7,000만원 미만</td></tr>
</tbody></table></div>
<p>자녀장려금에는 부양자녀 요건이 있습니다. 가구 유형도 본인이 붙인 명칭이 아니라 배우자·부양자녀·직계존속 및 소득 기준에 따라 대조해야 합니다. 위 표 하나만 맞는다고 신청 자격이 확정되지는 않습니다. <a href="https://i.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&amp;mi=2452" target="_blank" rel="noopener noreferrer">국세청 가구·소득·신청 제외 기준 ↗</a></p>
<p>‘연봉이 이 금액보다 적다’와 ‘총소득 요건을 충족한다’는 같은 계산이 아닐 수 있습니다. 국세청 안내의 총소득에는 근로소득 외 사업·종교인·이자·배당·연금·기타소득의 해당 범위도 포함됩니다. 지급액 산정에 쓰는 ‘총급여액 등’과 자격 확인에 쓰는 ‘총소득’을 나눠 확인하세요.</p>
<h2>재산을 계산할 때 대출부터 빼지 마세요</h2>
<p>2025년 6월 1일 기준 가구원 재산 합계액은 2억4천만원 미만이어야 하며, 재산가액에서 부채를 차감하지 않습니다. 1억7천만원 이상~2억4천만원 미만이면 산정액의 50% 지급을 안내합니다. 전세금 등 재산 종류별 평가 방식도 따로 있으므로 계좌 잔액만으로 합계를 대신하지 마세요. <a href="https://i.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&amp;mi=2452" target="_blank" rel="noopener noreferrer">재산 기준일·평가·감액 기준 ↗</a></p>
<p>상담을 준비할 때는 ‘현재 자산’과 ‘안내된 기준일의 가구원 재산’을 다른 항목으로 적어보세요. 부채가 있다는 이유로 먼저 빼서 요건표에 대입하면 기관이 확인하는 기준과 달라질 수 있습니다. 재산 목록·평가 시점을 확인할 질문만 지원금픽에 메모하고, 세부 소득·계좌자료는 공식 창구에 제출하세요.</p>
<h2>‘95% 지급’은 최대액의 95%가 아닙니다</h2>
<p>기한 후 신청에는 해당 장려금의 95% 지급을 안내합니다. 재산에 따른 감액, 자녀세액공제와의 조정, 체납 충당 등도 별도 항목입니다. <a href="https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&amp;mi=2450" target="_blank" rel="noopener noreferrer">국세청 감액·정산·충당 안내 ↗</a></p>
<p><strong>가상 계산:</strong> 다른 조정이 없고 산정액이 100만원이라고 가정하면 100만원 × 95% = 95만원입니다. 이 예시는 감액률을 읽는 방법일 뿐 실제 받을 금액을 계산한 것이 아닙니다. 인터넷에 표시된 가구별 최대액을 자신의 산정액으로 바꾸어 대입하지 마세요.</p>
<h2>내 상황에 따라 신청내역에서 확인할 칸이 다릅니다</h2>
<div class="guide-table"><table><caption>지원금픽의 신청 이력 확인 질문</caption><thead><tr><th scope="col">상황</th><th scope="col">확인할 내용</th></tr></thead><tbody>
<tr><th scope="row">2025년 소득분을 5월에 신청하지 않음</th><td>귀속연도와 가구 요건을 확인한 뒤 기한 후 신청 절차를 살펴봅니다.</td></tr>
<tr><th scope="row">2026년 9월에 반기 신청함</th><td>그 신청의 귀속연도가 무엇인지 확인합니다. 2025년분 신청 이력과 같은 것으로 단정하지 않습니다.</td></tr>
<tr><th scope="row">사업·종교인소득도 있음</th><td>근로소득만 있는 경우의 반기 절차를 그대로 적용하지 말고 맞는 신청 유형을 확인합니다.</td></tr>
<tr><th scope="row">국세청 자료와 내 자료가 다름</th><td>차이가 나는 소득·재산 항목과 필요한 증빙을 공식 안내에서 확인합니다.</td></tr>
</tbody></table></div>
<p>근로소득만 있는 경우의 정기·반기 선택과 사업·종교인소득이 있는 경우의 신청 유형은 국세청에서 구분합니다. 홈택스 신청내역·공식 안내를 먼저 확인하고, 필요한 증빙과 접수 완료 여부를 따로 챙기세요. 안내문을 받았다는 사실이나 지원금픽의 메모는 지급 결정이 아닙니다. <a href="https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&amp;mi=2450" target="_blank" rel="noopener noreferrer">정기·반기 유형과 심사 확인 ↗</a> · <a href="https://www.hometax.go.kr/" target="_blank" rel="noopener noreferrer">홈택스 공식 창구 ↗</a></p>
''',[(NEWS,'국세청 · 2026.11.2. 기한 후 신청 안내'),(ELIGIBILITY,'국세청 · 2025년 귀속 신청자격'),(PROCESS,'국세청 · 신청유형·감액·심사'),(CALENDAR,'정책브리핑 · 국세청 신청기간 안내')])
]
