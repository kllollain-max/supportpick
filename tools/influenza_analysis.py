"""One reviewed seasonal support guide; no medical or eligibility decision."""
from html import escape

NIP = 'https://nip.kdca.go.kr/irhp/infm/goVcntInfo.do?menuCd=134&menuLv=1'
PRESS = 'https://www.kdca.go.kr/kdca/2848/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGa2RjYSUyRjQyJTJGMzEyNjQyJTJGYXJ0Y2xWaWV3LmRvJTNG'

def influenza_advisory(row):
    if row.get('id') != '135200000115' or '2025.6.30' not in str(row.get('support') or ''):
        return ''
    return ('<p class="context-note influenza-source-advisory"><strong>2026-11-19 출처 대조:</strong> '
            '수집 상세의 접종력 기준일2025.6.30.과 이번 절기 공식 안내의2026.6.30.이 다릅니다. '
            '원본을 보존했으며 개인의 지원 횟수·접종 일정은 기록을 가지고 의료기관에 확인하세요. '
            '<a href="' + escape(NIP, quote=True) + '" target="_blank" rel="noopener noreferrer">대조한 공식 안내 ↗</a></p>')

INFLUENZA_ARTICLES = [(
'influenza-season-vs-dose-history-2026',
'2026–2027 독감 접종 지원: 절기·접종 이력·방문 준비 구분',
'1회 요약과 어린이 예외, 서로 다른 접종력 기준일, 변경된 시작일과 지정기관 확인을 구분합니다.',
'\n<h2>‘1회 지원’ 요약보다 접종 이력과 절기를 먼저 확인하세요</h2>\n<p>수집 요약은 ‘1회’로 안내하지만 어린이에게는 2회 지원 예외가 있습니다. 수집 상세의 과거 접종력 기준일은 <strong>2025.6.30.</strong>, 이번에 대조한 예방접종도우미는 <strong>2026.6.30.</strong>로 서로 다릅니다. 원본을 임의 교정하지 않고 차이를 표시했습니다. 생후6개월~9세 미만 중 첫 접종·이력 불명 또는 해당 기준일까지 총1회 접종한 경우에 대한 지원 안내이며, 개인의 횟수와 일정은 접종 기록을 가지고 예진의사에게 확인하세요. 이 페이지에서 추가 접종을 결정하지 않습니다.</p>\n<h2>출생 범위·최소 월령·시작일을 함께 읽으세요</h2>\n<div class="guide-table"><table><caption>2026–2027절기 국가 지원 일정 · 기관 방문 가능 여부는 별도 확인</caption><thead><tr><th scope="col">대상 구분</th><th scope="col">공식 안내의 범위</th><th scope="col">지원기간</th></tr></thead><tbody>\n<tr><th scope="row">어린이</th><td>생후6개월~14세 · 2012.1.1.~2026.8.31. 출생 범위</td><td>2026.9.21.~2027.4.30.</td></tr>\n<tr><th scope="row">임신부</th><td>임신 확인 자료 제시 · 주수 무관</td><td>2026.9.21.~2027.4.30.</td></tr>\n<tr><th scope="row">75세 이상</th><td>1951.12.31. 이전 출생</td><td>2026.10.6.~2027.4.30.</td></tr>\n<tr><th scope="row">70~74세</th><td>1952.1.1.~1956.12.31. 출생</td><td>2026.10.12.~2027.4.30.</td></tr>\n<tr><th scope="row">65~69세</th><td>1957.1.1.~1961.12.31. 출생</td><td>2026.10.15.~2027.4.30.</td></tr>\n</tbody></table></div>\n<p>출생 범위에 포함된다는 사실만으로 오늘 접종 가능한 것은 아닙니다. 예를 들어2026년8월생은 11월 방문 때 최소 생후6개월 조건을 충족하지 않을 수 있습니다. 범위와 월령을 함께 확인하세요. 국가 지원은 접종 비용 지원으로, 개인에게 현금을 입금하는 신청이 아닙니다. <a href="https://nip.kdca.go.kr/irhp/infm/goVcntInfo.do?menuCd=134&amp;menuLv=1" target="_blank" rel="noopener noreferrer">대상·횟수·기간 공식 안내 ↗</a></p>\n<h2>예전 시작일과 지난 절기의 대상을 섞지 마세요</h2>\n<p>질병관리청은2026.9.16. 일정 조정을 발표했습니다. 어린이1회 대상의 종전9월28일은9월21일로 바뀌었고 어르신 시작일도 앞당겨졌습니다. 현재 안내 페이지에는2020~2021절기 한시 확대 내용도 남아 있습니다. 그 부분의 의료급여·장애인 조건을 이번 절기의 전국 지원 대상으로 옮기지 마세요. 별도 지역 지원은 관할 보건소에서 확인합니다. <a href="https://www.kdca.go.kr/kdca/2848/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGa2RjYSUyRjQyJTJGMzEyNjQyJTJGYXJ0Y2xWaWV3LmRvJTNG" target="_blank" rel="noopener noreferrer">9월16일 일정 조정 발표 ↗</a></p>\n<h2>대상 확인·기관 확인·예진을 나누어 준비하세요</h2>\n<div class="guide-table"><table><caption>지원금픽의 방문 준비표 · 자격이나 의학적 적합성 판정 아님</caption><thead><tr><th scope="col">상황</th><th scope="col">준비할 정보</th><th scope="col">문의할 질문</th></tr></thead><tbody>\n<tr><th scope="row">어린이 접종 이력을 모름</th><td>생년월일과 확인 가능한 이전 접종 기록</td><td>이번 절기 지원 횟수와 다음 일정은 어떻게 확인하나요?</td></tr>\n<tr><th scope="row">임신부 또는 어르신</th><td>신분 확인 자료, 임신부는 산모수첩·임신확인서 등</td><td>대상 확인에 필요한 자료와 방문 시간이 맞나요?</td></tr>\n<tr><th scope="row">대상과 기간을 확인함</th><td>방문할 위탁의료기관·보건소와 희망 날짜</td><td>해당 대상 접종과 백신 준비가 가능한가요?</td></tr>\n</tbody></table></div>\n<p>전국 위탁기관에서 주소지와 관계없이 지원받을 수 있다는 설명은 아무 병원에서나 즉시 접종된다는 뜻이 아닙니다. 예방접종도우미의 지정의료기관 찾기에서 대상 구분을 선택한 뒤 기관에 방문 가능 여부를 확인하세요. 진료·추가 검사 비용까지 모두 무료라고 확장하지 않습니다. 공식 문의는 질병관리청1339 또는 관할 보건소입니다. 건강·임신·접종 이력 자료를 지원금픽에 제출하지 마세요.</p>\n',
[(NIP,'질병관리청 예방접종도우미 · 2026–2027절기 대상·기간·횟수'),
 (PRESS,'질병관리청 · 2026-09-16 일정 조정 발표')])]
