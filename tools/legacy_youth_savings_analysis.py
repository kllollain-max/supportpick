"""Separate closed new enrollment from existing subscribers' maturity claims."""
WORK24 = 'https://www.work24.go.kr/cm/c/f/1100/selecSystInfo.do?systClId=SC00000213&systCnntId=CI00001092&systId=SI00000325'
SBC = 'https://www.sbcplan.or.kr/page.do?mCode=B120020000'
FAQ = 'https://www.sbcplan.or.kr/faq.do?mCode=F050000000&page=6'
OLD_FAQ = 'https://1350.moel.go.kr/home/hp/data/faqView.do?faq_idx=1000000780'

LEGACY_YOUTH_SAVINGS_ARTICLES = [
('youth-mutual-aid-closed-enrollment-maturity-2026',
 '청년내일채움공제: 신규지원 중단·기존 가입자 만기 준비',
 '가입연도와 계약, 세 주체의 적립, 만기 신청과 입금을 나누어 확인하는 기존 가입자용 준비 안내입니다.', '''
<h2>먼저 기존 계약이 있는지 확인하세요</h2>
<p>공식 고용24 안내에서2024년부터 신규지원 중단을 확인했습니다. 이 글은 현재 새로 가입할 수 있는 지원금 모집 안내가 아닙니다. 지원금픽의 수집 원문도 신규지원 중단을 명시하지만 짧은 목록 설명에는1,200만원만 보일 수 있어, 해당 상세는 보류를 유지하고 이 안내로 연결합니다.</p>
<p>가입 이력이 없다면 이 글의 과거 금액을 신규 신청 가능액으로 사용하지 마세요. 기존 가입자는 본인 청약번호·계약성립일·가입연도부터 확인합니다. 이름이 비슷한 청년재직자 내일채움공제나 청년내일저축계좌는 별도 사업입니다. <a href="youth-savings-contribution-2026.html">청년내일저축계좌의 적립·만기 조건 안내</a>를 읽을 때에도 제도명을 먼저 대조하세요.</p>
<h2>1,200만원은2023년 가입 유형의 합계입니다</h2>
<p><a href="https://www.work24.go.kr/cm/c/f/1100/selecSystInfo.do?systClId=SC00000213&amp;systCnntId=CI00001092&amp;systId=SI00000325" target="_blank" rel="noopener noreferrer">고용24의2023년 기준 설명</a>은 청년400만원·기업400만원·정부400만원의 공동 적립을 구분합니다. 합계1,200만원 전부를 정부가 따로 지급하는 돈으로 계산하면 본인 납입금을 중복 계산하게 됩니다. 이전 가입연도의 부담 구조와 금액까지 이 숫자로 바꾸지 마세요.</p>
<div class="guide-table"><table><caption>기존 가입자가 구분할 세 단계 · 개인 지급 판정 아님</caption><thead><tr><th scope="col">단계</th><th scope="col">확인할 기록</th><th scope="col">아직 확정되지 않은 것</th></tr></thead><tbody>
<tr><th scope="row">계약·기간</th><td>가입연도, 계약성립일, 본인 유형의 가입기간과 재직 기록</td><td>달력상 기간 경과만으로 적립 완료·만기금 자동 입금이 확정되지 않음</td></tr>
<tr><th scope="row">적립 완료</th><td>청년 납입금, 기업 부담분, 정부 지원금의 실제 반영 내역</td><td>본인 자동이체가 끝났어도 나머지 적립과 기업의 지원금 신청 확인 필요</td></tr>
<tr><th scope="row">만기 청구</th><td>본인 만기 신청, 재직 증빙, 접수·보완 요청·승인과 지급 상태</td><td>만기 안내 문자나 신청 버튼 노출만으로 계좌 입금 완료가 아님</td></tr>
</tbody></table></div>
<p><a href="https://www.sbcplan.or.kr/page.do?mCode=B120020000" target="_blank" rel="noopener noreferrer">중소벤처기업진흥공단 사업 안내</a>는 가입 유형별 적립 주체와 만기 요건을 나누고, 부담금·지원금이 모두 적립된 뒤 신청하도록 설명합니다. 만기일·미납·지원금 미반영을 각각 표시해 두면 확인할 담당자를 찾기 쉽습니다. 이자도 상품의 실제 적용 기준을 확인하며 임의의 확정액을 더하지 않습니다.</p>
<h2>처리일수는 적용 약관과 실제 접수 상태를 확인합니다</h2>
<div class="guide-table"><table><caption>공식 페이지의 서로 다른 만기금 처리 안내 · 입금일 보장 아님</caption><thead><tr><th scope="col">자료</th><th scope="col">읽은 문구의 기준</th><th scope="col">준비할 질문</th></tr></thead><tbody>
<tr><th scope="row">고용24 제도 안내</th><td>접수일로부터7일 이내</td><td>제 가입 유형과 실제 청구 건에 이 안내가 적용되나요?</td></tr>
<tr><th scope="row">고용노동부2021.9.17. FAQ</th><td>지급청구서 접수 다음날부터7영업일 이내</td><td>과거 안내의 작성일과 지금 계약의 적용 약관이 같은가요?</td></tr>
<tr><th scope="row">공단 FAQ</th><td>접수일 기준15영업일 이내(신청일·공휴일 제외)</td><td>접수 기준일과 서류 보완 여부, 현재 처리 상태는 무엇인가요?</td></tr>
</tbody></table></div>
<p><a href="https://1350.moel.go.kr/home/hp/data/faqView.do?faq_idx=1000000780" target="_blank" rel="noopener noreferrer">2021년 작성 상담센터 FAQ</a>와 <a href="https://www.sbcplan.or.kr/faq.do?mCode=F050000000&amp;page=6" target="_blank" rel="noopener noreferrer">공단 FAQ</a>를 함께 대조했습니다. 서로 다른 일수를 더하거나 가장 짧은 수치를 확정 지급기한으로 선택하지 않았습니다. 본인의 계약·가입연도·접수 상태를 밝히고 적용 약관과 예정 일정을 공단에 확인하세요.</p>
<h2>미납과 변동 사항은 임의 처리 전에 상담하세요</h2>
<p>공단 FAQ는 미납 조회·납부 신청을 공식 홈페이지에서 안내하고 다른 계좌나 가상계좌로 임의 입금하지 않도록 설명합니다. 납입내역에서 빠진 회차를 찾은 뒤 공식 절차를 확인하세요. 휴직·퇴사·근로조건 변동이 있다면 납입중지·해지에 미치는 영향을 담당기관에 먼저 문의하며, 이 글만으로 해지나 환급액을 결정하지 마세요.</p>
<ol><li>계약 확인: 제도명·가입연도·청약번호와 재직기간을 정리합니다.</li><li>적립 대조: 본인·기업·정부 내역을 나누고 미반영된 회차와 담당 주체를 확인합니다.</li><li>공식 신청: 만기 안내와 본인 유형의 재직 증빙을 확인해 공단 공식 창구에서 청구합니다.</li><li>처리 확인: 접수일·보완 요청·결정·실제 입금을 따로 기록합니다.</li></ol>
<p>고용24는2023년 가입자는 고용센터·1350,2022년 이전 가입자는 가입 당시 운영기관을 통한 상담 경로를 구분합니다. 필요한 서류와 담당 창구는 본인 가입연도 기준으로 확인하세요. 청약번호·재직 증빙·계좌 자료는 공식 접수처에만 제출하고 지원금픽에 올리지 않습니다.</p>
''', [(WORK24,'고용24 · 신규지원 중단·2023년 적립 구조·가입연도별 상담'),
      (SBC,'중소벤처기업진흥공단 · 유형별 만기 요건·신청'),
      (FAQ,'중소벤처기업진흥공단 FAQ · 적립 완료·청구·처리·미납'),
      (OLD_FAQ,'고용노동부 ·2021.9.17. 작성 만기 FAQ·과거 처리일수')])
]
