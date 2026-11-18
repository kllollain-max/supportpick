"""A checked local comparison; do not infer eligibility or combine awards."""

TRANSPORT = 'https://www.incheon.go.kr/earlychild/EC060103'
POSTPARTUM = 'https://www.incheon.go.kr/earlychild/EC060104'
TRANSPORT_CURRENT = 'https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&srvcId=628000000735'
POSTPARTUM_CURRENT = 'https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&srvcId=628000000744'

MATERNITY_ARTICLES = [
('incheon-pregnancy-transport-vs-postpartum-2026',
 '인천 임산부 교통비와 산후조리비: 거주기간·신청시점·서류 비교',
 '6개월과 1년의 거주 조건, 임신 12주와 32주의 신청 시작, 포인트 사용기한과 준비서류를 구분합니다.', '''
<h2>같은 인천e음 지원이어도 신청 조건은 따로 확인합니다</h2>
<p>‘인천에 거주하는 임산부’라는 공통점만으로 두 지원의 대상이라고 판단하면 산후조리비의 추가 조건을 놓칠 수 있습니다. 아래는 지원금픽이 공식 안내를 대조해 만든 신청 준비표입니다. 두 금액을 합산한 수급액이나 동시 수급 가능 여부를 확정하는 표가 아닙니다.</p>
<div class="guide-table"><table><caption>신청일 기준 조건과 신청 가능한 시점</caption><thead><tr><th scope="col">구분</th><th scope="col">임산부 교통비</th><th scope="col">맘편한 산후조리비</th></tr></thead><tbody>
<tr><th scope="row">지원 내용</th><td>1인당 50만원, 기본은 인천e음 포인트</td><td>취약계층 산모 1인당 150만원, 인천e음 포인트</td></tr>
<tr><th scope="row">거주 조건</th><td>인천 주민등록·실거주 6개월(180일) 이상</td><td>인천 주민등록·실거주 1년 이상, 연속 거주 확인</td></tr>
<tr><th scope="row">신청 시점</th><td>임신 12주부터 출산 후 90일 이내</td><td>임신 32주부터 출산 후 90일 이내</td></tr>
<tr><th scope="row">추가 확인</th><td>출산 후 신청은 인천시 출생등록, 지급 전 타시도 전출입 여부</td><td>취약계층 해당 여부, 지정 부모교육 수료, 지급 전 타시도 전출입 여부</td></tr>
<tr><th scope="row">방문 접수</th><td>주소지 행정복지센터</td><td>주소지 보건소</td></tr>
</tbody></table></div>
<p>근거: <a href="https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&amp;srvcId=628000000735" target="_blank" rel="noopener noreferrer">인천시 교통비 혜택 안내</a>와 <a href="https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&amp;srvcId=628000000744" target="_blank" rel="noopener noreferrer">산후조리비 혜택 안내</a>. ‘연중 신청’은 개인별 90일 기한이 없다는 뜻이 아닙니다. 거주기간을 채우는 날과 출산일 기준 마감일을 각각 적고, 신청일에 조건을 갖추는지 확인하세요.</p>
<h2>임신 주수와 전입일을 함께 적으면 다음 질문이 보입니다</h2>
<div class="guide-table"><table><caption>신청 준비 사례 · 자격 판정이 아닌 확인 순서</caption><thead><tr><th scope="col">상황</th><th scope="col">먼저 확인할 일</th></tr></thead><tbody>
<tr><th scope="row">임신 20주, 인천 거주 8개월</th><td>교통비의 주수·거주 조건부터 확인합니다. 산후조리비는 32주와 1년 거주, 취약계층·교육 조건을 따로 확인해야 합니다.</td></tr>
<tr><th scope="row">출산 후 신청을 준비하는 가구</th><td>90일 마감, 출생등록, 거주기간 충족일을 확인합니다. 앱·카드 준비 때문에 접수를 늦추지 않도록 담당 창구에 절차를 먼저 문의하세요.</td></tr>
<tr><th scope="row">산후조리비 소득 조건이 헷갈리는 가구</th><td>공식 안내는 다문화 가정의 중위소득 65% 이하 조건과 별도 항목인 중위소득 60% 이하 출산 가정을 구분합니다. 모든 취약계층에 65%를 일괄 적용하지 마세요.</td></tr>
</tbody></table></div>
<h2>신청 마감일과 포인트 만료일은 다른 일정입니다</h2>
<p>두 사업의 기본 포인트는 사용기간 1년이며 미사용분은 소멸합니다. 출산 후 90일은 신청 기한이고, 지급된 포인트의 사용기한과는 다릅니다. 교통비 포인트는 인천e음 앱 호출 택시·자가용 유류비·등록한 교통카드를 이용한 대중교통 등으로 용도가 정해져 있습니다. 일반 포인트로 전기차 충전비를 결제할 수 있는 것으로 읽지 마세요.</p>
<p>전기차 사용자의 교통비는 별도 현금 지원 경로가 있으며 렌트차량은 제외됩니다. 자동차등록증·본인 명의 통장 사본과 차량 인정 범위를 확인해야 합니다. 이는 모든 신청자에게 현금 지급한다는 뜻이 아닙니다. <a href="https://www.incheon.go.kr/earlychild/EC060103" target="_blank" rel="noopener noreferrer">전기차·교통카드·서류 공식 안내</a>의 표제는 2025년으로 남아 있어, 위의 현재 혜택 안내와 함께 대조했습니다.</p>
<p>산후조리비는 공식 가맹점과 산후 건강관리 용도 여부를 결제 전에 확인하세요. 인천시 안내는 산모·신생아 건강관리 제공기관에서 이 포인트를 사용할 수 없다고 명시합니다. 이를 모든 출산 지원의 동시 수급 금지로 확대 해석하지 말고, 이미 이용 중인 서비스의 정확한 이름과 결제 항목을 보건소에 알려 확인하세요. <a href="https://www.incheon.go.kr/earlychild/EC060104" target="_blank" rel="noopener noreferrer">산후조리비 사용처·제한 안내</a></p>
<h2>서류를 모두 발급하기 전에 확인할 세 가지</h2>
<ol><li>본인 온라인 신청과 대리·외국인 방문 신청을 구분합니다. 맘편한 임신 등록, 신청자 명의 휴대폰·인천e음 가입 및 주소지에 맞는 카드부터 확인하세요.</li>
<li>전자 확인이 안 되는 임신·취약계층·소득 정보의 추가 증빙을 확인합니다. 산후조리비는 부모교육 수료증, 다태아 임신 중 신청은 32주 이후 다태아 임신 유지 확인자료를 확인하세요.</li>
<li>접수 완료·보완 요청·지급·포인트 만료를 따로 기록합니다. 신청 완료를 승인 또는 지급 완료로 기록하지 마세요.</li></ol>
<p>지원금픽에 신분증이나 통장 사본을 제출할 필요는 없습니다. 증빙 제출과 최종 심사는 공식 신청기관에서 진행합니다.</p>
''', [(TRANSPORT_CURRENT, '인천광역시 · 교통비 현재 혜택·신청 안내'),
      (POSTPARTUM_CURRENT, '인천광역시 · 산후조리비 대상·서류·1년 사용기간'),
      (TRANSPORT, '인천광역시 · 교통카드·전기차·방문 서류'),
      (POSTPARTUM, '인천광역시 · 산후조리비 거주·교육·사용 제한')])
]
