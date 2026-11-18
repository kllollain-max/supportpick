"""Birth-year and payment-path checks for one local benefit."""
CURRENT = 'https://www.incheon.go.kr/earlychild/EC060102'
BENEFIT = 'https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&srvcId=628000000739'
WELFARE = 'https://www.incheon.go.kr/welfare/WE020480'
OLD = 'https://www.incheon.go.kr/IC010101/view?cntPerPage=50&curPage=43&nttNo=2043922&srchKey=srchSj&srchSiteRealmCode=&srchWord='

CHILD_ARTICLES = [
('incheon-child-dream-birth-year-2026',
 '2026 인천 아이 꿈 수당: 출생연도·신청월·포인트 지급 확인',
 '현재 2016년생 안내와 과거 확대 계획을 구분하고, 전입 재신청·명의 일치·보호아동 지급 예외를 확인하는 준비표입니다.', '''
<h2>과거의 확대 계획을 올해 대상자로 읽지 마세요</h2>
<p>아이 꿈 수당을 찾을 때는 안내의 작성연도와 아동의 출생연도를 함께 확인해야 합니다. 지원금픽은 현재 시청 안내와 보존된 수집 원문을 대조하고, 과거 공지의 확대 계획을 현재 신청 자격으로 옮겨 적지 않았습니다.</p>
<div class="guide-table"><table><caption>같은 사업의 시점이 다른 공식 자료 읽기</caption><thead><tr><th scope="col">자료</th><th scope="col">기재된 범위</th><th scope="col">신청 전에 할 일</th></tr></thead><tbody>
<tr><th scope="row">2024년 신청 공지</th><td>2024년 2016년생부터 시작, 이후 출생연도별 확대 예정</td><td>당시 계획을 2026년 확정 대상이라고 사용하지 않습니다.</td></tr>
<tr><th scope="row">현재 인천시 안내</th><td>2026년 기준 2016년생, 월 5만원</td><td>실제 출생연도와 인천 주민등록·거주 및 보호자 조건을 대조합니다.</td></tr>
<tr><th scope="row">2017년 이후 출생 아동</th><td>시청 안내는 아동수당 적용과 이후 아이 꿈 수당 재신청을 별도 설명</td><td>옛 확대 계획으로 두 수당을 합산하지 말고 주소지 행정복지센터에 현재 적용을 확인합니다.</td></tr>
</tbody></table></div>
<p>현재 기준은 <a href="https://www.incheon.go.kr/earlychild/EC060102" target="_blank" rel="noopener noreferrer">인천시 영유아 안내(최종 업데이트 2026.10.16.)</a>와 <a href="https://www.incheon.go.kr/welfare/WE020480" target="_blank" rel="noopener noreferrer">시청 복지 안내</a>에서 대조했습니다. <a href="https://www.incheon.go.kr/IC010101/view?cntPerPage=50&amp;curPage=43&amp;nttNo=2043922&amp;srchKey=srchSj&amp;srchSiteRealmCode=&amp;srchWord=" target="_blank" rel="noopener noreferrer">2024.7.31. 공지</a>는 과거 자료 비교용입니다. 현재 시청 안내의 2030년 지원계획도 지금 받을 수 있는 확정 지원액으로 계산하지 마세요.</p>
<h2>월 5만원을 현금 입금이나 연간 확정액으로 바꾸지 마세요</h2>
<p>기본 지급은 매월 25일 신청 보호자의 인천e음 카드 포인트입니다. 보호자 본인 명의의 신청·휴대폰·인천e음 앱·카드가 맞는지 확인하세요. 현재 안내는 가정위탁·아동복지시설 등 보호아동의 경우 본인 명의 디딤씨앗통장 현금 지급을 별도로 설명합니다. 이 예외를 모든 신청 가구의 계좌 현금 지급으로 확대하지 않습니다.</p>
<p>예를 들어 가계부에 월 5만원을 기록하더라도 ‘5만원×12개월=60만원’을 올해 실제 확정 수령액으로 미리 적으면 신청월·전입·전출 상황을 빠뜨릴 수 있습니다. 실제 결정된 시작 월과 지급 내역을 기준으로 기록하고, 포인트 사용제한 업종도 확인하세요. <a href="https://www.incheon.go.kr/earlychild/EC060102" target="_blank" rel="noopener noreferrer">지급방식·보호아동 예외·사용제한 공식 안내</a></p>
<h2>전입과 재전입은 신청 순서를 다시 확인할 때입니다</h2>
<div class="guide-table"><table><caption>상황별 준비 질문 · 개인 자격 판정 아님</caption><thead><tr><th scope="col">내 상황</th><th scope="col">준비할 확인 사항</th></tr></thead><tbody>
<tr><th scope="row">인천으로 새로 전입</th><td>전입일과 신청일을 적습니다. 시청은 전입 후30일 이내 신청 시 전입월 소급 지원을 안내하므로 기한·접수 완료를 확인합니다.</td></tr>
<tr><th scope="row">타시도로 이사했다 인천에 다시 전입</th><td>이전 지급 이력만 믿지 말고 재신청 여부를 확인합니다. 현재 혜택 안내는 재전입 시 재신청을 명시합니다.</td></tr>
<tr><th scope="row">부모 외 보호자가 신청</th><td>부모 사망·친권상실·장기부재 등 해당 사유와 후견·보호 증빙을 확인하고 행정복지센터 방문 경로를 문의합니다.</td></tr>
</tbody></table></div>
<p>신청월 기준 지원과 전입월 소급 예외를 구분하세요. 과거2024년 시행 당시의 60일 소급 특례를 현재 모든 신규 신청에 적용하지 않습니다. <a href="https://www.incheon.go.kr/welfare/WE020480" target="_blank" rel="noopener noreferrer">현재 신청시기·전입 예외 안내</a></p>
<h2>접수·심사·지급을 나누어 기록하세요</h2>
<ol><li>2016년생 여부와 주소·거주·보호자 항목을 확인하고 정부24 공식 신청 화면을 엽니다.</li><li>본인 온라인 신청을 원칙으로 하되 방문이 필요한 경우 실제 제출 목록을 확인합니다. 수집 원문의 방문 기본 서류는 신분증·주민등록등본, 대리 신청 해당 시 위임장입니다.</li><li>신청 완료, 자격 확인·결정 통지, 카드 포인트 또는 해당 보호아동의 통장 지급을 별도 확인합니다. 지원금픽 기록을 기관 접수나 수급 결정으로 취급하지 않습니다.</li></ol>
<p><a href="https://www.incheon.go.kr/icbenefit/ICB020201/view?curPage=1&amp;srvcId=628000000739" target="_blank" rel="noopener noreferrer">현재 혜택의 신청·재전입·구비서류 안내</a>를 대조하세요. 지원금픽에 신분증·주민등록등본·통장 사본을 제출할 필요는 없습니다.</p>
''', [(CURRENT,'인천광역시 · 2026 대상·월 지급·보호아동 지급 예외'),
      (WELFARE,'인천광역시 · 신청월·전입30일·지원 절차'),
      (BENEFIT,'인천광역시 · 수집 원문과 대조한 대상·재전입·서류'),
      (OLD,'인천광역시 · 2024년 과거 공지(현재 자격 근거 아님)')])
]
