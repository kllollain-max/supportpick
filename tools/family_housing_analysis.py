"""Two deliberately scoped 2026 guides, checked against official references."""
CHILD = 'https://www.mohw.go.kr/menu.es?mid=a10711030100'
CHILD_CHANGE = 'https://www.korea.kr/news/policyNewsView.do?newsId=148963446'
CHILD_NOTICE = 'https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309511_1122.html'
HOUSING = 'https://www.lh.or.kr/menu.es?mid=a10401050100'
MYHOME = 'https://www.myhome.go.kr/hws/portal/cont/selectHousingBenefitView.do'
RENT = 'https://www.myhome.go.kr/hws/portal/cont/selectRentalHouseholdSupView.do'

FOCUS_ARTICLES = [
('child-allowance-2026', '2026 아동수당: 8세 안내와 달라진 대상·지역별 금액 확인',
 '오래된 8세 미만 안내로 신청을 포기하지 않도록, 연령 확대와 거주지역·과거 수급 이력을 나누어 확인합니다.', '''
<h2>‘8세가 지났으니 끝났다’고 판단하기 전에 연도를 보세요</h2>
<p>보건복지부의 2026년 안내는 <strong>9세 미만</strong>이며 지급액은 아동 1인당 월 10만~13만원입니다. 지원금픽이 조회한 아동수당 API에는 변경 전 ‘8세 미만·월 10만원’ 문구가 남아 있어 현재 조건으로 표시하는 것을 보류했습니다. API를 오늘 조회했다는 사실만으로 그 내용이 오늘 기준이라고 볼 수 없습니다. <a href="https://www.mohw.go.kr/menu.es?mid=a10711030100" target="_blank" rel="noopener noreferrer">보건복지부 대상·금액 안내 ↗</a></p>
<div class="guide-table"><table><caption>연령 안내를 읽을 때의 구분</caption><thead><tr><th scope="col">보이는 문구</th><th scope="col">읽는 방법</th></tr></thead><tbody>
<tr><th scope="row">8세 미만</th><td>2026년 확대 전 안내인지 확인합니다. 예전 글만 보고 상담을 포기하지 마세요.</td></tr>
<tr><th scope="row">2026년 9세 미만</th><td>올해 적용 안내입니다. 출생연월과 과거 수급·중단 이력을 함께 확인합니다.</td></tr>
<tr><th scope="row">13세 미만으로 확대</th><td>2030년까지 매년 1세씩 확대하는 일정입니다. 올해 모든 13세 미만 아동에게 지급한다는 뜻으로 읽지 않습니다.</td></tr>
</tbody></table></div>
<p>정부의 변경 안내는 2026년 9세 미만을 시작으로 단계적 확대를 설명합니다. 일반 연령 설명만으로 경계에 있는 아동의 지급 종료월을 계산하지 말고, 담당기관에 적용 출생연월과 지급월을 확인하세요. <a href="https://www.korea.kr/news/policyNewsView.do?newsId=148963446" target="_blank" rel="noopener noreferrer">2026년 확대 일정·신청 구분 ↗</a></p>
<h2>‘최대 13만원’을 모든 지역의 현금액으로 읽지 마세요</h2>
<div class="guide-table"><table><caption>2026년 거주지역별 월 안내액 · 개인 확정액 아님</caption><thead><tr><th scope="col">지역 구분</th><th scope="col">월 안내액</th><th scope="col">추가 확인</th></tr></thead><tbody>
<tr><th scope="row">수도권</th><td>10만원</td><td>아동 주소지와 적용 지급월</td></tr>
<tr><th scope="row">비수도권</th><td>10만5천원</td><td>인구감소지역의 별도 구분에 해당하는지</td></tr>
<tr><th scope="row">인구감소 우대지역</th><td>11만원</td><td>지역사랑상품권 지급 관련 조례·운영 여부</td></tr>
<tr><th scope="row">인구감소 특별지역</th><td>12만원</td><td>지역사랑상품권 지급 관련 조례·운영 여부</td></tr>
</tbody></table></div>
<p>인구감소지역에서 지역사랑상품권으로 지급하는 경우 1만원 상당의 추가 지급을 안내합니다. 지역 구분을 모두 더해 받는 구조가 아닙니다. 현금 입금 원칙과 조례에 따른 지역상품권 방식을 구분하세요. <a href="https://www.mohw.go.kr/menu.es?mid=a10711030100" target="_blank" rel="noopener noreferrer">지역·지급방식 공식 기준 ↗</a></p>
<p>예를 들어 생활비 계획에는 본인 지역의 기본 안내액과 상품권으로 받는 부분을 다른 칸에 적어보세요. ‘최대 금액’만 통장 입금 예상액으로 적으면 실제 사용 계획과 어긋날 수 있습니다. 전입한 가구는 예전 주소의 지급액을 계속 적용한다고 가정하지 말고, 어느 지급월부터 새 주소 기준을 쓰는지 물어보는 것이 좋습니다.</p>
<h2>받다가 중단된 경우와 한 번도 신청하지 않은 경우가 다릅니다</h2>
<p>정부는 확대 전 생일 경과로 지급이 끊긴 2017년 1월생~2018년 3월생에 대해 지급 정보를 확인하는 직권 처리와 2026년 미지급분 소급 안내를 했습니다. 한 번도 받은 적 없는 아동은 신규 신청이 필요하다고 구분합니다. 이는 변경 당시의 처리 안내이며, 이 글이 개별 아동의 지급 완료를 확인한 것은 아닙니다. <a href="https://www.korea.kr/news/policyNewsView.do?newsId=148963446" target="_blank" rel="noopener noreferrer">중단 이력·신규 신청 안내 ↗</a></p>
<div class="guide-table"><table><caption>지원금픽의 문의 준비표</caption><thead><tr><th scope="col">상황</th><th scope="col">담당기관에 확인할 질문</th></tr></thead><tbody>
<tr><th scope="row">예전에 받다가 연령 초과로 중단</th><td>확대 대상에 포함되는지, 직권 처리가 끝났는지, 지급 정보 변경이 필요한지 확인합니다.</td></tr>
<tr><th scope="row">아동수당 신청 이력이 없음</th><td>신규 신청 경로와 본인 상황에 적용되는 지급 시작월을 확인합니다.</td></tr>
<tr><th scope="row">주소·보호자·계좌가 변경됨</th><td>변경 신고 여부와 반영할 지급월을 확인합니다. 계좌정보는 공식 접수창구에만 제출합니다.</td></tr>
</tbody></table></div>
<p>읍·면·동 주민센터 또는 복지로에서 신청을 안내합니다. 본인 수급 이력을 모르면 ‘예전에 받았을 것’이라고 가정하지 말고 담당기관에 먼저 확인하세요.</p>
<h2>신청 안내 문자를 받았을 때</h2>
<p>복지로에 게시된 보건복지부 변경 안내는 당시 정부 안내 문자에 접속 링크가 없고 앱 설치를 유도하지 않는다고 설명합니다. 문자 링크에 계좌정보를 입력하기보다, 알고 있는 공식 주소나 주민센터로 별도 확인하세요. 3월에 안내된 회신 일정이 지금도 접수기한인 것처럼 재사용하지 않습니다. <a href="https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309511_1122.html" target="_blank" rel="noopener noreferrer">보건복지부 변경 발표·문자 주의사항 ↗</a></p>
''', [(CHILD,'보건복지부 · 아동수당 대상·지역별 지급액'),
      (CHILD_CHANGE,'대한민국 정책브리핑 · 2026년 변경·신청 구분'),
      (CHILD_NOTICE,'복지로에 게시된 보건복지부 변경 발표')]),
('housing-benefit-2026', '2026 주거급여: 지역별 상한과 실제 월세, 임차·자가 지원 비교',
 '기준임대료를 확정 지급액으로 오해하지 않도록 임대차계약·소득인정액·주거형태를 나누어 읽는 준비 안내입니다.', '''
<h2>집이 내 소유인지, 빌려 사는지부터 나누세요</h2>
<div class="guide-table"><table><caption>주거형태에 따라 달라지는 지원</caption><thead><tr><th scope="col">주거형태</th><th scope="col">공식 안내의 방향</th><th scope="col">준비할 질문</th></tr></thead><tbody>
<tr><th scope="row">임차</th><td>기준임대료를 상한으로 실제 임차료를 지원</td><td>계약서의 보증금·월세, 실제 거주, 지급하는 임차료를 어떻게 확인하나요?</td></tr>
<tr><th scope="row">자가</th><td>주택 노후도 등을 평가해 주택개량 지원</td><td>주택 소유·거주 상태와 보수가 필요한 부분을 어떻게 조사하나요?</td></tr>
</tbody></table></div>
<p>2026년 선정기준은 기준 중위소득 48% 이하의 소득인정액입니다. 1인 가구 1,230,834원, 4인 가구 3,117,474원이며 소득인정액은 월급과 같은 개념이 아닙니다. 자가 가구의 수선 지원을 임차 가구의 월 현금액처럼 비교하지 마세요. <a href="https://www.myhome.go.kr/hws/portal/cont/selectHousingBenefitView.do" target="_blank" rel="noopener noreferrer">마이홈 · 대상·임차·자가 지원 ↗</a></p>
<h2>같은 1인 가구라도 지역별 상한이 다릅니다</h2>
<div class="guide-table"><table><caption>2026년 1인 임차가구 기준임대료 · 월 상한, 확정 지급액 아님</caption><thead><tr><th scope="col">서울</th><th scope="col">경기·인천</th><th scope="col">광역시·세종·수도권 외 특례시</th><th scope="col">그 외 지역</th></tr></thead><tbody><tr><td>369,000원</td><td>300,000원</td><td>247,000원</td><td>212,000원</td></tr></tbody></table></div>
<p>‘전국 1인 가구 최대 369,000원’처럼 서울 상한만 기억하면 다른 지역의 생활비 계획이 달라질 수 있습니다. 가구원 수와 급지를 먼저 고르고, 그다음 실제 임차료와 자기부담분을 확인하세요. 서울의 금액을 거주지역과 무관한 공통 정액으로 적용하지 않습니다. <a href="https://www.lh.or.kr/menu.es?mid=a10401050100" target="_blank" rel="noopener noreferrer">LH · 가구원 수별 전체 기준임대료 표 ↗</a></p>
<h2>보증금이 있으면 월세만 보고 비교하지 마세요</h2>
<p>공식 안내의 실제 임차료는 계약서의 보증금을 연 4%로 월 환산한 금액과 월차임을 합해 산정합니다. 소득인정액이 생계급여 선정기준을 넘으면 자기부담분을 차감하는 구조도 있습니다. <a href="https://www.myhome.go.kr/hws/portal/cont/selectRentalHouseholdSupView.do" target="_blank" rel="noopener noreferrer">마이홈 · 실제 임차료·자기부담 산정 ↗</a></p>
<p><strong>가상 예시:</strong> 보증금 600만원, 월세 18만원이라면 보증금 월 환산은 6,000,000원 × 4% ÷ 12 = 20,000원, 두 금액의 합은 200,000원입니다. 이는 계약 금액을 읽는 산식 예시이며 실제 지급액 계산 결과가 아닙니다.</p>
<p>이 예시에서 ‘월세가 18만원이니 무조건 18만원’ 또는 ‘지역 상한만큼 받는다’고 결론 내리지 마세요. 임대차관계와 실제 거주, 가구 조사, 소득인정액 및 적용 제한을 함께 확인해야 합니다. 기관이 산정한 소득인정액과 해당 급지를 모르면 지급 예정액 대신 확인할 항목을 기록하세요.</p>
<h2>신청 뒤에는 주택조사도 있습니다</h2>
<p>주민등록 주소지 주민센터나 복지로에서 신청하고, 소득·재산조사와 주택조사를 거쳐 결정합니다. LH 안내에는 신청서·신분증, 소득·재산신고서, 금융정보 제공동의서, 임대차 관련 서류, 통장사본이 있으며 상황에 따라 추가 서류를 요청할 수 있습니다. <a href="https://www.lh.or.kr/menu.es?mid=a10401050100" target="_blank" rel="noopener noreferrer">LH · 신청서류·조사 절차 ↗</a></p>
<div class="guide-table"><table><caption>지원금픽의 상담 준비 사례</caption><thead><tr><th scope="col">내 상황</th><th scope="col">서류 발급 전 확인할 질문</th></tr></thead><tbody>
<tr><th scope="row">계약자와 실제 거주 가구가 다름</th><td>누구의 임대차관계와 가구 구성을 확인해야 하는지 설명합니다. 임의로 계약서를 고치지 않습니다.</td></tr>
<tr><th scope="row">보증금·월세가 변경됨</th><td>어떤 변경 자료와 반영 시점을 확인해야 하는지 문의합니다.</td></tr>
<tr><th scope="row">무상으로 거주함</th><td>월세가 있는 임차가구 예시를 그대로 적용하지 말고, 사용대차와 지급 제한 여부를 확인합니다.</td></tr>
<tr><th scope="row">자가 주택에 보수가 필요함</th><td>월세 금액표 대신 노후도 조사와 수선 지원 절차를 질문합니다.</td></tr>
</tbody></table></div>
<p>위 표는 별도의 필수서류 규정이 아니라 상담을 위한 질문입니다. 주택조사 연락을 받으면 조사기관과 약속을 공식 경로로 확인하고, 신청 접수와 지원 결정을 구분하세요. 이 글의 금액은 2026년 기준이며 다른 연도에는 해당 연도 공고로 다시 확인해야 합니다.</p>
''', [(MYHOME,'마이홈 · 2026 주거급여'), (HOUSING,'LH · 임차가구 기준임대료·신청·조사'), (RENT,'마이홈 · 임차가구 산정 원칙')])
]
