"""Authored application and use checklists for two distinct living benefits."""
from html import escape
FOREST_NOTICE = 'https://fowi.or.kr/user/bbs/bbsView.do?bbsId=8574&bbsManageId=12'
FOREST_HOME = 'https://forestcard.or.kr/main/main.do'
FOREST_FACILITIES = 'https://www.forestcard.or.kr/mobile/useInfo/mobileUseUtilizeList.do?menuId=1110100'
FOREST_EXCEPTIONS = 'https://forestcard.or.kr/board/selectBoardArticle.do?bbsId=BBSMSTR_000000000001&menuId=1060100&nttId=319&pageIndex=1&pageSize=10'
TRANSPORT = 'https://web1.gg.go.kr/contents/contents.do?ciIdx=987119&menuId=266082'


def source_advisory(row):
    if (row.get('id') == '140000000176'
            and ''.join(str(row.get('period', '')).split()) == '매년12월신청시기알림'):
        return ('<p class="context-note source-advisory"><strong>신청과 사용기한 구분:</strong> '
                '원본의 매년 12월 알림은 현재 접수 공고가 아닙니다. '
                '2026년 공고의 온라인 신청 마감은 1월 30일 14시, 우편 도착 마감은 같은 날 18시이며, '
                '이용권 사용기한 11월 30일과 다릅니다. '
                '<a href="' + escape(FOREST_NOTICE, quote=True) + '" target="_blank" rel="noopener noreferrer">'
                '해당 연도 공식 모집공고 ↗</a>에서 연도와 차수를 확인하세요. 원본은 보존했습니다.</p>')
    return ''


FOREST_TRANSPORT_ARTICLES = [
('forest-voucher-application-vs-use-2026', '2026 산림복지이용권: 신규 신청과 11월 30일 사용기한 구분',
 '선정 전·선정 후의 준비를 나누고, 예약 가능 시설과 이용권 결제 가능 시설을 별도로 확인하는 안내입니다.', '''
<h2>먼저 올해 선정된 이용자인지 확인하세요</h2>
<p>산림복지서비스이용권을 처음 찾은 사람과 이미 선정돼 잔액이 남은 사람은 확인할 달력이 다릅니다. 수집 원문의 ‘매년 12월 신청시기 알림’을 오늘의 신청기간으로 읽지 않도록, 2026년 모집공고와 사용 안내를 나누었습니다. 내년 신청기간을 올해 일정으로 추정하지 않습니다.</p>
<div class="guide-table"><table><caption>2026년 공고 · 신청과 이용의 서로 다른 기한</caption><thead><tr><th scope="col">단계</th><th scope="col">공식 공고의 일정</th><th scope="col">준비할 일</th></tr></thead><tbody>
<tr><th scope="row">온라인 신청</th><td>1월 2일 10시~1월 30일 14시</td><td>사용기한까지 새 신청이 가능하다고 읽지 않기</td></tr>
<tr><th scope="row">우편 신청</th><td>1월 30일 18시 도착분까지</td><td>발송일과 도착일, 온라인 마감 시각을 구분하기</td></tr>
<tr><th scope="row">선정 후 사용</th><td>카드 발급 이후~11월 30일</td><td>본인의 선정·충전 결과와 실제 잔액을 확인하기</td></tr>
</tbody></table></div>
<p>이는 <a href="https://fowi.or.kr/user/bbs/bbsView.do?bbsId=8574&amp;bbsManageId=12" target="_blank" rel="noopener noreferrer">2026년 모집공고</a>의 일정입니다. 공고상 지원은 1인당 10만원의 이용권이며 대상에는 기초생활수급자·장애(아동)수당 및 장애인연금 수급자·차상위계층·한부모가족 등이 안내돼 있습니다. 대상 자격, 실제 선정, 충전 결과를 각각 확인해야 합니다. 지원금픽이 발급이나 선정을 판정하지 않습니다.</p>
<h2>11월에 발견했다면 할 일을 두 갈래로 나누세요</h2>
<div class="guide-table"><table><caption>지원금픽의 상황별 확인 순서</caption><thead><tr><th scope="col">상황</th><th scope="col">먼저 확인</th><th scope="col">남길 질문</th></tr></thead><tbody>
<tr><th scope="row">2026년 선정 여부를 모름</th><td>공식 누리집의 발급내용·선정 결과</td><td>사용기한과 새 모집공고 중 어느 안내가 필요한가요?</td></tr>
<tr><th scope="row">선정됐고 잔액이 남음</th><td>잔액, 방문할 시설, 이용일과 결제 방법</td><td>이 비용을 이용권으로 결제할 수 있나요?</td></tr>
<tr><th scope="row">예약을 취소하거나 바꿀 예정</th><td>시설의 취소 조건과 카드사의 포인트 반환 안내</td><td>사용 종료 전에 반환·재사용을 확인할 수 있나요?</td></tr>
</tbody></table></div>
<p><a href="https://forestcard.or.kr/main/main.do" target="_blank" rel="noopener noreferrer">공식 누리집</a>은 2026년 선정 완료와 11월 30일 사용기한을 안내합니다. 새 신청이 필요한 사람은 해당 연도·차수의 모집 여부를 확인하고, 이미 선정된 사람은 잔액과 이용 준비를 확인하세요. ‘사용기간이 남음’만으로 새로 발급받을 수 있다고 판단하지 않습니다.</p>
<h2>예약 가능한 시설과 이용권 결제 가능한 시설을 따로 찾으세요</h2>
<p>시설 이름이 예약 사이트에 있다는 사실만으로 이용권 결제가 되는 것은 아닙니다. 먼저 <a href="https://www.forestcard.or.kr/mobile/useInfo/mobileUseUtilizeList.do?menuId=1110100" target="_blank" rel="noopener noreferrer">공식 사용가능 기관 목록</a>에서 시설을 찾고, 예약하려는 상품·비용의 결제 방법을 해당 시설에 확인하세요. 숙박·체험·식비를 한 번에 예약하더라도 각각 같은 결제 조건이라고 가정하지 않습니다.</p>
<p><a href="https://forestcard.or.kr/board/selectBoardArticle.do?bbsId=BBSMSTR_000000000001&amp;menuId=1060100&amp;nttId=319&amp;pageIndex=1&amp;pageSize=10" target="_blank" rel="noopener noreferrer">2026년 7월 7일 기준 사용불가 시설 공지</a>에는 강원숲체험장(춘천)·하추자연휴양림(인제) 등의 이름이 포함돼 있습니다. 이 목록은 해당 공지의 기준일 자료입니다. 방문일의 운영·결제 가능 여부는 공식 목록과 시설에 다시 확인하세요. 예약 취소에 따른 포인트 반환과 사업 종료 시 사용 제한도 같은 공지에서 따로 안내하므로, 마감 직전 취소·재예약 계획은 먼저 문의하는 편이 좋습니다.</p>
<h2>시설에 문의할 때 쓸 메모</h2>
<ol><li>시설명, 이용일, 숙박·체험 등 이용할 항목을 나누어 적습니다.</li><li>산림복지서비스이용권 결제가 가능한 비용과 결제 경로를 묻습니다.</li><li>취소·기상 상황으로 일정이 바뀌면 반환과 재사용을 누구에게 확인할지 묻습니다.</li><li>답변을 확인한 날짜만 개인 메모에 남깁니다. 카드번호나 수급 증명서는 지원금픽에 입력하지 않습니다.</li></ol>
<h2>문화누리카드와 이름·기한을 섞지 마세요</h2>
<p>문화누리카드는 별도의 제도입니다. 2026년 문화누리카드 안내는 발급·재충전과 사용을 구분하고 있으므로, 산림복지이용권의 11월 30일 사용기한을 다른 카드의 기한으로 옮겨 적지 마세요. <a href="culture-card-deadlines-2026.html">문화누리카드 금액·발급·사용 안내</a>에서 따로 확인할 수 있습니다. 두 제도를 함께 표시했다는 사실은 중복 수혜나 한 결제에서의 병용을 보장하지 않습니다.</p>
''', [(FOREST_NOTICE, '한국산림복지진흥원 · 2026 모집공고'),
      (FOREST_HOME, '산림복지서비스이용권 · 선정·사용 안내'),
      (FOREST_FACILITIES, '산림복지서비스이용권 · 사용가능 기관'),
      (FOREST_EXCEPTIONS, '산림복지서비스이용권 · 사용불가 시설·취소 주의사항')]),
('gyeonggi-child-transport-cap-2026', '경기도 어린이·청소년 교통비: 분기 6만원 한도와 실제 환급액 읽기',
 '경기도 거주·연령·이용 교통수단을 나누고, 연간 한도와 실제 사용액을 혼동하지 않도록 준비합니다.', '''
<h2>연 24만원을 가입 즉시 받는 금액으로 적지 마세요</h2>
<p>교통비 안내에서 먼저 볼 것은 연간 최대액보다 ‘어느 분기에 어떤 교통수단을 이용했는가’입니다. 지원금픽은 거주 조건, 교통 이용 내역, 정산 한도를 서로 다른 칸에 적어 확인하도록 정리했습니다. 개인의 등록 상태·교통 이용내역·최종 지급액을 조회하는 서비스는 아닙니다.</p>
<div class="guide-table"><table><caption>공식 경기도 안내에서 확인할 네 가지</caption><thead><tr><th scope="col">항목</th><th scope="col">안내 내용</th><th scope="col">확인할 질문</th></tr></thead><tbody>
<tr><th scope="row">거주·연령</th><td>신청일 기준 경기도 주민등록의 6~18세 어린이·청소년, 대리인 신청 가능</td><td>학교 소재지가 아니라 신청하는 사람의 주민등록·연령을 확인했나요?</td></tr>
<tr><th scope="row">한도</th><td>분기별 6만원, 연 24만원 한도</td><td>실제 이용액과 최대 한도를 구분했나요?</td></tr>
<tr><th scope="row">대중교통</th><td>수도권 버스·지하철·신분당선·광역버스·GTX 등</td><td>따로 발권하는 KTX·SRT·시외·고속버스 비용을 합치지 않았나요?</td></tr>
<tr><th scope="row">공유자전거</th><td>똑타 앱을 통한 요금 결제 시 1천원 즉시할인 안내</td><td>대중교통 환급과 다른 앱의 자전거 결제를 같은 방식으로 계산하지 않았나요?</td></tr>
</tbody></table></div>
<p>위 기준은 <a href="https://web1.gg.go.kr/contents/contents.do?ciIdx=987119&amp;menuId=266082" target="_blank" rel="noopener noreferrer">경기도청의 어린이·청소년 교통비 안내</a>를 대조했습니다. 같은 화면의 성인 경기패스 안내와 대상 연령·지원방식을 섞지 않도록 어린이·청소년 항목을 먼저 선택하세요.</p>
<h2>두 개의 가상 이용 내역으로 한도를 읽어보세요</h2>
<p><strong>신청·등록 등 필요한 조건이 충족됐고 전액이 지원 대상 이용액으로 인정된다고 가정</strong>합니다. 아래 숫자는 ‘실사용액에 한도를 적용하는 원리’를 설명하는 예시이며 개인별 환급 예상액을 판정하지 않습니다.</p>
<div class="guide-table"><table><caption>가상 분기 이용액 · 다른 지급 조건은 충족했다고 가정</caption><thead><tr><th scope="col">인정 이용액 가정</th><th scope="col">6만원 한도와 비교</th><th scope="col">예시에서 확인할 점</th></tr></thead><tbody>
<tr><th scope="row">35,000원</th><td>35,000원</td><td>6만원 한도라는 이유만으로 사용액보다 많은 금액을 받는 계산이 아님</td></tr>
<tr><th scope="row">82,000원</th><td>60,000원</td><td>한도를 넘는 22,000원까지 전부 환급된다고 적지 않기</td></tr>
</tbody></table></div>
<p>실사용액과 분기 한도는 <a href="https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00004473" target="_blank" rel="noopener noreferrer">복지로의 경기도 사업 안내(2026.7.23. 수정)</a>에서도 확인됩니다. 네 분기 한도를 더한 연간 최대액과, 본인이 신청·인증을 마친 분기의 실제 정산액을 같은 숫자로 두지 마세요. 이전 분기 소급 여부·등록 정보 정정·지급일은 현재 공식 포털에서 확인할 항목입니다.</p>
<h2>교통카드와 환급 수단을 두 칸으로 나누세요</h2>
<p>수집 원문에는 어린이·청소년 본인의 교통카드와 환급받을 지역화폐 정보를 각각 등록하도록 안내돼 있습니다. 대리인이 신청하더라도 대리인의 교통 이용액을 자녀의 실적으로 넣는 절차로 이해하면 안 됩니다. 누가 타는 카드인지와 누구의 지급수단을 등록할 수 있는지를 분리해 공식 기준을 확인하세요.</p>
<div class="guide-table"><table><caption>개인정보를 입력하지 않는 등록 준비표</caption><thead><tr><th scope="col">준비 항목</th><th scope="col">공식 창구에서 확인할 내용</th></tr></thead><tbody>
<tr><th scope="row">거주지 확인</th><td>대상 어린이·청소년 또는 대리인에게 적용되는 인증 방법</td></tr>
<tr><th scope="row">이용내역 확인</th><td>실제로 쓰는 본인 교통카드, 분실·교체가 있었다면 등록 상태</td></tr>
<tr><th scope="row">환급 준비</th><td>지역화폐 명의·등록 가능 여부와 수령 수단</td></tr>
<tr><th scope="row">분기 점검</th><td>신청·인증 완료 상태, 정보 수정 기한과 지급 안내</td></tr>
</tbody></table></div>
<p>이 표에 카드번호·인증서·주소를 입력할 필요는 없습니다. 실제 등록과 인증은 <a href="https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1002200&amp;bnefType=all&amp;svcId=641000000139" target="_blank" rel="noopener noreferrer">정부24 원본의 공식 신청 경로</a>에서 진행합니다. 지원금픽의 저장·내 신청 기록만으로 교통비 신청이나 지급 등록이 완료되지 않습니다.</p>
<h2>공식 자료와 실제 접수 화면을 나누어 확인합니다</h2>
<p>2026.11.17. 대조에서 경기도청의 제도 안내와 복지로 검색 자료의 기본 기준, 현재 수집된 API의 대상·금액·준비 항목을 확인했습니다. 이 글은 제도 설명과 수집 원문을 대조한 안내이며, 개인별 등록 완료나 당일 접수·지급 상태를 확인한 결과가 아닙니다. 포털의 현재 공지와 문의처에서 분기별 운영 일정을 다시 확인하세요.</p>
''', [(TRANSPORT, '경기도청 · 어린이·청소년 대상·한도·교통수단'),
      ('https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId=WLF00004473', '복지로 · 경기도 어린이·청소년 교통비 지원'),
      ('https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=1002200&bnefType=all&svcId=641000000139', '정부24 · 수집 원문과 신청 경로')])
]
