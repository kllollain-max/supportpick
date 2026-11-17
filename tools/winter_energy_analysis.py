"""Housing-work and fuel-bill support have different preparation decisions."""

EFFICIENCY = ('https://www.e-policy.or.kr/web/lay1/program/S1T9C14/curation/view.do'
              '?cr_seq=109')
LOCAL_NOTICE = ('https://bucheon.go.kr/site/program/board/basicboard/view'
                '?boardtypeid=26736&currentpage=23&encid=bACNXtqSxaft0ySlKLxqLw%3D%3D&menuid=148002001001&pagesize=20')
ENERGY = 'https://www.energyv.or.kr/info/support_info.do'

WINTER_ARTICLES = [
('winter-bills-vs-home-improvement-2026', '겨울 난방 지원: 요금 이용권과 단열·보일러 공사, 무엇부터 확인할까요?',
 '고지서 부담과 주택 성능 문제를 나누고, 지역 접수·소유주 동의·과거 공사·다른 연료비 지원을 확인하는 준비표입니다.', '''
<h2>같은 ‘난방 지원’이어도 해결하려는 문제가 다릅니다</h2>
<p>이번 달 난방 요금을 내기 어려운 상황과 창문 틈으로 열이 빠져나가는 상황을 한 신청으로 해결할 수 있다고 생각하면 준비가 어긋납니다. 지원금픽은 먼저 필요한 도움을 요금 결제와 주택 공사로 나누고, 담당 창구에서 물을 질문을 정리했습니다. 아래 표는 상담 준비용이며 지원 대상 판정이나 두 사업의 동시 수혜 확인서가 아닙니다.</p>
<div class="guide-table"><table><caption>2026년 난방 관련 지원의 서로 다른 준비</caption><thead><tr><th scope="col">비교할 점</th><th scope="col">일반 에너지바우처</th><th scope="col">저소득층 에너지효율개선 · 난방</th></tr></thead><tbody>
<tr><th scope="row">도움의 형태</th><td>에너지 비용에 사용하는 이용권</td><td>단열·창호·보일러 등 주택의 에너지 사용환경 개선</td></tr>
<tr><th scope="row">자격 확인의 시작</th><td>기초생활보장 수급 요건과 세대원 특성 요건을 함께 확인</td><td>수급·차상위 또는 지자체 추천 여부와 해당 주택의 공사 가능 조건 확인</td></tr>
<tr><th scope="row">준비 질문</th><td>어떤 고지서·결제 방식을 쓸 것인가요?</td><td>어떤 공사가 필요하고 소유주 동의를 받을 수 있나요?</td></tr>
<tr><th scope="row">기간 확인</th><td>2026년 신청은 12월 31일까지, 사용은 2027년 5월 31일까지로 구분</td><td>2026년 국가 안내는 예산 소진 시까지. 지역 모집 마감·잔여 예산은 접수기관에 확인</td></tr>
</tbody></table></div>
<p>요금 이용권의 세대별 총액을 보일러 교체비나 매달 현금으로 옮겨 계산하지 마세요. 공사 지원도 가구별 현금 지급액을 뜻하지 않습니다. 금액과 결제 방식은 <a href="energy-voucher-2026.html">에너지바우처 상세 해설</a>, 공사 신청은 아래의 주택 상담 메모를 나누어 준비하세요. 해당 사업의 수집 자료가 있으면 이 글 아래 ‘공식 API 자료와 대조하기’에 연결됩니다.</p>
<h2>전국 안내의 ‘예산 소진 시’와 우리 동네 접수 마감은 다를 수 있습니다</h2>
<p><a href="https://www.e-policy.or.kr/web/lay1/program/S1T9C14/curation/view.do?cr_seq=109" target="_blank" rel="noopener noreferrer">에너지정책소통센터의 2026년 안내</a>는 난방 공사 접수를 3월 3일부터 예산 소진 시까지로 설명합니다. 페이지 상단의 연말 날짜만 보고 접수 가능하다고 판단하지 말고 본문의 냉방·난방 구분을 읽으세요.</p>
<p>실제로 <a href="https://bucheon.go.kr/site/program/board/basicboard/view?boardtypeid=26736&amp;currentpage=23&amp;encid=bACNXtqSxaft0ySlKLxqLw%3D%3D&amp;menuid=148002001001&amp;pagesize=20" target="_blank" rel="noopener noreferrer">부천시의 2026년 2월 24일 공고</a>는 난방 접수 마감을 9월 11일 18시로 안내합니다. 이는 부천의 해당 공고 사례입니다. 다른 지역의 마감으로 일반화하거나, 이후 추가 모집이 없었다고 단정하지 않습니다. 거주지 읍·면·동에 올해 잔여 접수·추가 모집 여부를 물어보세요.</p>
<h2>임차 가구는 공사 계약보다 주택 조건 확인을 먼저 하세요</h2>
<div class="guide-table"><table><caption>방문 전에 적어갈 주택 상담 메모 · 일괄 필수서류 목록 아님</caption><thead><tr><th scope="col">메모할 내용</th><th scope="col">창구에 물을 질문</th></tr></thead><tbody>
<tr><th scope="row">자가·임차·공공임대 여부</th><td>제 주택 유형이 제외 기준이나 예외에 해당하나요?</td></tr>
<tr><th scope="row">수선유지급여 대상 여부</th><td>자가 주택의 수선 지원과 이번 공사의 관계를 어떻게 확인하나요?</td></tr>
<tr><th scope="row">소유주 동의 가능 여부</th><td>필요한 동의 양식과 제출 시점은 언제인가요?</td></tr>
<tr><th scope="row">이전에 지원받은 공사와 시기</th><td>지난 지원 이력 때문에 이번 공사가 제한되나요?</td></tr>
<tr><th scope="row">불편한 방·창호·설비</th><td>방문 조사와 지원 범위 결정은 어떤 순서인가요?</td></tr>
</tbody></table></div>
<p>공공임대나 수선유지급여 대상 등은 제외 기준을 따로 확인해야 합니다. ‘세입자는 모두 제외’ 또는 ‘집이 낡았으면 모두 가능’으로 단순화하지 마세요. 임의로 보일러를 구매·시공한 뒤 환급을 전제로 신청하지 말고, 접수기관에서 해당 주택의 조사·시공 절차부터 안내받으세요. 소유주 연락처·임대차계약서·증명서는 지원금픽에 제출하지 않습니다.</p>
<h2>기존 지원은 이름을 끝까지 적어야 중복 여부를 물을 수 있습니다</h2>
<p><a href="https://www.energyv.or.kr/info/support_info.do" target="_blank" rel="noopener noreferrer">에너지바우처 공식 기준</a>은 동절기 연료비·연탄쿠폰·연탄전환 에너지바우처와의 동절기 중복 제한을 안내합니다. 여기서 긴급복지의 <strong>동절기 연료비</strong>와 <strong>생계지원</strong>은 같은 이름이 아닙니다. 생계지원을 받는다는 이유만으로 이 제한에 곧바로 대입하거나, 반대로 아무 조정 없이 모두 받을 수 있다고 결론 내리지 마세요.</p>
<ol><li>받고 있거나 신청 중인 사업의 정확한 이름과 지원 연도를 적습니다.</li><li>현금·요금차감·이용권·공사 중 어떤 도움인지 나눕니다.</li><li>담당자에게 기존 사업을 알리고 중지·변경·선택 절차가 필요한지 묻습니다.</li><li>결정 통지와 사용·시공 안내를 받은 뒤 개인 일정에 기록합니다.</li></ol>
<p>당장 생활이 어려워진 위기가 있다면 공사 접수를 기다리는 문제와 구분해 <a href="emergency-vs-livelihood-2026.html">긴급복지 생계지원·생계급여 상담 준비</a>도 살펴보세요. 이 연결은 수급을 보장하는 추천이 아닙니다. 본문은 2026년 공식 공개 안내를 2026년 11월 17일 대조한 것이며, 각 창구의 당일 접수·예산은 별도 확인이 필요합니다.</p>
''', [(ENERGY, '한국에너지공단 · 에너지바우처 지원·중복 기준'),
      (EFFICIENCY, '한국에너지정보문화재단 · 2026년 에너지효율개선 안내'),
      (LOCAL_NOTICE, '부천시 · 2026년 난방 공사 모집 사례 · 전국 공통 마감 아님')])
]
