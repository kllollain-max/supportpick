"""Two authored explanations and narrowly observed source-reading cautions."""
MNURI = 'https://www.mnuri.kr/munhwa/introduceNuri.do'
ISSUE = 'https://www.mnuri.kr/munhwa/cardIssueGuide.do'
NPS = 'https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do'
NPS_DETAIL = 'https://www.nps.or.kr/comm/pop/getOHAH0015P1.do'


def source_advisory(row):
    """Do not repeat a warning after its observed source condition changes."""
    if row.get('id') == '648000001107' and 'mnurri.kr' in str(row.get('method', '')).lower():
        return ('<p class="context-note source-advisory"><strong>신청 주소 확인:</strong> '
                '수집 원문의 신청 주소에 공식 도메인과 다른 표기가 있습니다. '
                '<a href="' + ISSUE + '" target="_blank" rel="noopener noreferrer">'
                '확인한 문화누리 공식 발급 안내(mnuri.kr) ↗</a>에서 신청 경로를 선택하세요. 원문은 보존했습니다.</p>')
    if row.get('id') == 'B55151000066' and ''.join(str(row.get('period', '')).split()) == '2025.02.03~2025.11.28':
        return ('<p class="context-note source-advisory"><strong>지난 연도 자료:</strong> '
                '이 원본의 신청기간은 2025년입니다. 2026년 발급기간·지원액은 아래 해설과 '
                '<a href="' + ISSUE + '" target="_blank" rel="noopener noreferrer">'
                '2026 문화누리 공식 발급 안내 ↗</a>를 구분해 확인하세요. 이전 자료를 삭제하거나 새 연도로 바꾸지 않았습니다.</p>')
    return ''


CULTURE_PENSION_ARTICLES = [
('culture-card-deadlines-2026', '2026 문화누리카드: 발급 마감·사용기한·15만원과 추가지원 구분',
 '신규·재충전·자동재충전을 나누고, 같은 카드의 여러 안내를 중복 합산하지 않도록 금액과 기한을 비교합니다.', '''
<h2>카드가 있는지, 올해 지원금이 들어왔는지부터 나누어 확인하세요</h2>
<p>작년에 쓰던 카드를 갖고 있다는 사실만으로 올해 발급이나 재충전이 끝난 것은 아닙니다. 지원금픽에서는 ‘신규 카드가 필요한가’, ‘보유 카드에 올해 지원금이 들어왔는가’, ‘남은 지원금을 언제까지 쓸 수 있는가’를 순서대로 확인하도록 정리했습니다. 2026년 안내이며 개인의 발급 자격이나 예산 잔여를 확정하지 않습니다.</p>
<div class="guide-table"><table><caption>2026년 문화누리카드 · 서로 다른 숫자와 기한</caption><thead><tr><th scope="col">항목</th><th scope="col">공식 안내</th><th scope="col">확인할 질문</th></tr></thead><tbody>
<tr><th scope="row">기본지원</th><td>1인당 연 15만원</td><td>매달 받는 현금이 아니라 올해 카드 지원금으로 구분했나요?</td></tr>
<tr><th scope="row">생애주기 추가지원</th><td>해당 대상자에게 1만원 추가. 추가지원 예산 소진 시 기본지원만 지급</td><td>출생연도와 추가지원 예산을 함께 확인했나요?</td></tr>
<tr><th scope="row">발급·재충전</th><td>2026.2.2.~11.30. · 예산 소진 시 조기 마감 가능</td><td>거주지의 발급 예산과 접수 시간을 확인했나요?</td></tr>
<tr><th scope="row">카드 사용</th><td>2026.12.31.까지</td><td>발급 마감일까지 신청하는 일과 남은 지원금을 사용하는 일을 구분했나요?</td></tr>
</tbody></table></div>
<p>금액·추가지원·예산 조건은 <a href="https://www.mnuri.kr/munhwa/introduceNuri.do" target="_blank" rel="noopener noreferrer">문화누리 사업 안내</a>, 발급과 사용 일정은 <a href="https://www.mnuri.kr/munhwa/cardIssueGuide.do" target="_blank" rel="noopener noreferrer">2026 공식 발급 안내</a>를 대조했습니다. 발급 마감이 지나도 새로 신청할 수 있다는 뜻으로 사용기한을 읽지 마세요.</p>
<h2>15만원과 16만원 중 어느 숫자를 봐야 하나요?</h2>
<p>2026년 추가지원 대상은 청소년기 2008~2013년생, 준고령기 1962~1966년생입니다. 해당 출생연도여도 기본 수급 자격과 예산 조건을 따로 확인합니다. 따라서 ‘모두 16만원’ 또는 ‘아무 조건 없이 1만원 추가’라고 정리하면 안 됩니다. <a href="https://www.mnuri.kr/munhwa/introduceNuri.do" target="_blank" rel="noopener noreferrer">대상 출생연도·추가지원 예산 조건 ↗</a></p>
<p>예를 들어 추가지원 대상 출생연도의 가족이 카드를 가지고 있다면, 먼저 올해 자격과 충전 결과를 확인하고 그다음 실제 잔액을 확인하세요. 가족의 나이만 보고 예정 금액을 사용 가능한 잔액으로 먼저 기록하지 않는 방법입니다. 카드 잔액이나 개인 식별정보를 지원금픽에 입력할 필요는 없습니다.</p>
<h2>‘카드 보유’와 ‘자동재충전 완료’는 다릅니다</h2>
<p>공식 발급 안내는 2025년 카드 사용액 3만원 이상과 수급 자격 유지 등을 자동재충전 조건으로 설명하고, 상세 대상 요건은 별도 공지를 확인하도록 안내합니다. 자동재충전 대상이라고 추정하기보다 실제 완료 여부를 확인하세요. 조건을 모두 설명하지 않은 이 글만으로 자동재충전을 확정하지 마세요. <a href="https://www.mnuri.kr/munhwa/cardIssueGuide.do" target="_blank" rel="noopener noreferrer">자동재충전 및 신청 경로 안내 ↗</a></p>
<div class="guide-table"><table><caption>현재 상태에 따라 먼저 할 일</caption><thead><tr><th scope="col">상태</th><th scope="col">먼저 확인</th><th scope="col">그다음 단계</th></tr></thead><tbody>
<tr><th scope="row">문화누리카드가 없음</th><td>올해 대상과 거주지 발급 예산</td><td>신규 발급 경로·수령 방법·신청자별 서류 확인</td></tr>
<tr><th scope="row">작년 카드가 있음</th><td>올해 자동재충전 결과와 카드 유효기간</td><td>미충전이면 재충전 가능 경로와 마감 확인</td></tr>
<tr><th scope="row">지원금은 들어왔으나 사용하지 못함</th><td>수령등록 등 사용 준비와 잔액</td><td>공식 가맹점과 결제·취소 반영 일정을 확인</td></tr>
</tbody></table></div>
<h2>같은 문화누리카드 안내 3개를 합산하지 마세요</h2>
<p>지원금픽에는 문체부의 중앙 안내, 경남의 발급 안내, 한국문화예술위원회의 자료가 함께 있습니다. 이들은 기관별 안내 경로이며 제목이 다르다는 이유로 연간 지원금을 세 번 더할 수 없습니다. 특히 예술위원회 연결자료에는 2025년 기간과 14만원이 명시돼 있습니다. 원본을 남겨 과거 연도를 확인하게 하고, 현재 안내와 구분했습니다.</p>
<p>경남 수집 원문에는 신청 웹주소의 철자가 공식 도메인과 다른 표기도 있습니다. 주소를 그대로 옮겨 적기보다 이 글에서 대조한 <a href="https://www.mnuri.kr/munhwa/cardIssueGuide.do" target="_blank" rel="noopener noreferrer">문화누리 공식 안내(mnuri.kr)</a>에서 신청 메뉴를 선택하세요. 이 경고는 해당 표기가 있는 원본에만 표시합니다.</p>
<h2>신청 전에 준비할 항목</h2>
<ol><li>신청받을 사람의 출생연도와 기초생활수급·차상위 자격을 공식 창구에서 확인합니다. 2026년 발급 안내의 연령 기준은 2020.12.31. 이전 출생입니다.</li><li>본인·대리인·미성년자·시설 거주 신청 중 어떤 경로인지 구분하고 필요한 신분 확인과 위임·가족관계 서류를 확인합니다.</li><li>주민센터, 공식 누리집·앱 등에서 가능한 신청 방법과 카드 수령·등록 절차를 확인합니다. 전화는 보유 카드의 재충전 조건을 따로 확인합니다.</li><li>실제 발급·충전 완료와 잔액을 확인한 뒤 사용할 가맹점과 연말 사용 계획을 정합니다.</li></ol>
<p>발급 대상·신청 절차의 기준은 <a href="https://www.mnuri.kr/munhwa/cardIssueGuide.do" target="_blank" rel="noopener noreferrer">문화누리 공식 발급 안내</a>입니다. 서류가 필요한지 확인하기 전에 가족의 증명서를 일괄 발급하거나 이 사이트에 올리지 마세요. 발급 마감 직전에는 지역 예산과 운영 시간을 먼저 확인하는 것이 좋습니다.</p>
''', [(MNURI, '문화누리 · 2026 금액·추가지원·예산 조건'), (ISSUE, '문화누리 · 대상·신청·발급과 사용기한')]),
('basic-pension-amounts-2026', '2026 기초연금: 선정기준액 247만원과 실제 월 지급액 구분',
 '소득인정액 기준과 지급액, 부부 감액을 구분하고 신청 전에 정리할 자료와 상담 질문을 안내합니다.', '''
<h2>247만원은 매달 받는 기초연금이 아닙니다</h2>
<p>기초연금 안내에서 큰 금액이 보이면 ‘내가 받는 월 금액’인지 ‘신청자를 가르는 기준’인지 먼저 구분해야 합니다. 지원금픽은 소득인정액과 기준연금액을 서로 다른 칸에 놓고 읽도록 정리했습니다. 국민연금 노령연금의 개인 가입 이력이나 예상 연금액을 계산하는 안내는 아닙니다.</p>
<div class="guide-table"><table><caption>2026년 기초연금의 숫자 · 기준과 지급액 구분</caption><thead><tr><th scope="col">숫자</th><th scope="col">무엇을 뜻하나요?</th><th scope="col">어떻게 확인하나요?</th></tr></thead><tbody>
<tr><th scope="row">단독가구 월 247만원</th><td>2026년 소득인정액 선정기준액</td><td>내 소득인정액 산정 결과와 비교할 숫자</td></tr>
<tr><th scope="row">부부가구 월 395만2천원</th><td>배우자가 있는 가구의 선정기준액</td><td>배우자 유무와 가구의 소득·재산 조사 범위를 확인</td></tr>
<tr><th scope="row">월 최대 349,700원</th><td>단독가구의 2026년 최대 기초연금 안내</td><td>감액과 개인 산정 결과를 별도로 확인할 숫자</td></tr>
</tbody></table></div>
<p>만 65세 이상과 소득인정액 기준, 최대 지급액 및 감액 안내는 <a href="https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do" target="_blank" rel="noopener noreferrer">국민연금공단의 2026년 기초연금 수급 요건</a>을 대조했습니다. 2025년 선정기준액 228만원과 2026년 기준을 섞지 않도록 연도도 함께 적어두세요. <a href="https://m.korea.kr/briefing/pressReleaseView.do?newsId=156737807&amp;pWise=mSub&amp;pWiseSub=C8" target="_blank" rel="noopener noreferrer">보건복지부 2026.1.1. 선정기준 발표 ↗</a></p>
<h2>월급이나 통장 입금액만 대입하면 안 되는 이유</h2>
<p>소득인정액은 소득평가액과 재산의 소득환산액을 합한 값입니다. 따라서 월급이 기준보다 작다는 이유만으로 선정을 확정하거나, 월급이 기준보다 크다는 이유만으로 스스로 신청을 포기할 수 없습니다. 공제·재산·부채 등의 적용은 공식 산정으로 확인해야 합니다. <a href="https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do" target="_blank" rel="noopener noreferrer">소득인정액의 뜻 ↗</a></p>
<p>상담 메모에는 ‘급여·연금 등 소득 종류’, ‘부동산·금융재산·부채의 보유 여부’, ‘배우자 유무’를 나누어 적어보세요. 계좌 잔액을 이 사이트의 계산기에 입력해 자격을 확정하는 절차는 제공하지 않습니다. 자료를 정리하는 목적은 조사에서 확인할 항목을 놓치지 않기 위해서입니다.</p>
<h2>부부가 모두 받으면 최대액 두 배인가요?</h2>
<p>공단 안내는 부부가 동시에 수급하면 각각 20% 감액하며, 국민연금 수급액이나 소득·재산 등에 따라 일부 감액될 수 있다고 설명합니다. <a href="https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do" target="_blank" rel="noopener noreferrer">부부 감액·기타 감액 안내 ↗</a></p>
<p>두 사람 모두 다른 감액 전 기준액이 349,700원이라고 <strong>가정</strong>하고 부부 감액만 적용하면, 1인당 <strong>349,700원 × 80% = 279,760원</strong>, 두 사람 합계는 <strong>559,520원</strong>입니다. 이 예시는 ‘최대액을 단순히 두 배로 더하지 않는 이유’를 보여주는 산식입니다. 실제 부부의 선정·최종 지급액은 계산하지 않습니다.</p>
<h2>국민연금이나 직역연금이 있다면 이름부터 구분하세요</h2>
<p>국민연금 노령연금과 기초연금은 다른 제도입니다. 공단은 조건에 따라 국민연금과 기초연금을 함께 받을 수 있으나 기초연금액이 감액될 수 있다고 설명합니다. ‘국민연금을 받으니 기초연금은 무조건 안 된다’고 결론 내리지 말고 해당 연금의 정확한 명칭과 수급 상태를 알리고 확인하세요. <a href="https://www.nps.or.kr/comm/pop/getOHAH0015P1.do" target="_blank" rel="noopener noreferrer">공단의 두 연금 수급 안내 ↗</a></p>
<p>공무원·군인·사학·별정우체국 등의 직역연금은 별도 제외 원칙과 예외 확인이 필요합니다. 국민연금과 같은 조건으로 처리된다고 추정하지 마세요. 수급권자 본인뿐 아니라 배우자 관련 조건도 확인합니다. <a href="https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do" target="_blank" rel="noopener noreferrer">직역연금 관련 안내 ↗</a></p>
<h2>신청 준비는 ‘접수 경로·필요 자료·산정 결과’로 나누세요</h2>
<ol><li>주민센터·행정복지센터, 국민연금공단 지사 또는 복지로에서 신청 경로를 확인합니다.</li><li>정부24 수집 원문에 안내된 신분증, 신청서, 소득·재산 신고서, 본인·배우자 금융정보 제공 동의서, 통장 사본을 출발점으로 실제 가구와 신청 방식의 제출 목록을 담당기관에 확인합니다.</li><li>접수 후 소득·재산 조사와 지자체의 결정·통지 내용을 확인하고, 선정기준액과 실제 결정액을 서로 다른 칸에 기록합니다.</li><li>결과에 관해 질문할 때는 ‘적용한 가구 유형’, ‘산정된 소득인정액’, ‘어떤 감액이 적용됐는지’를 나누어 묻습니다.</li></ol>
<p>신청 창구는 <a href="https://www.nps.or.kr/pbcpgdnc/mainbiz/getOHAG0059M0.do" target="_blank" rel="noopener noreferrer">공단 공식 안내</a>, 제출 자료의 출발점은 <a href="https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=72548&amp;bnefType=all&amp;svcId=SSE000000170" target="_blank" rel="noopener noreferrer">정부24 기초연금 원본</a>입니다. 모든 가구의 필수서류를 확정한 목록은 아닙니다. 원본 서류와 금융정보는 공식 접수 창구에 제출하세요.</p>
''', [(NPS, '국민연금공단 · 2026 기초연금 기준·감액·신청'),
      (NPS_DETAIL, '국민연금공단 · 노령연금과 기초연금·지자체 결정'),
      ('https://m.korea.kr/briefing/pressReleaseView.do?newsId=156737807&pWise=mSub&pWiseSub=C8', '보건복지부 · 2026.1.1. 선정기준액 발표')])
]
