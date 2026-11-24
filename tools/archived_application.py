"""Follow-up guidance for explicitly reviewed, closed application rounds."""
from zoneinfo import ZoneInfo

REVIEWED = '2026-11-24'

# Match both the service and the published edition. Never attach an old
# application notice when the provider updates the record to a new round.
ROUNDS = {
    '142100000062': {
        'period': '2025.09.15~2025.12.31',
        'end': '2025-12-31',
        'notice': '2025년 상생페이백 신규 신청은 12월 31일에 종료됐습니다.',
        'body': '''
<h3>이미 받은 금액을 확인하려는 경우</h3>
<p>디지털 온누리상품권 앱에서 잔액과 사용내역을 각각 확인하세요. 잔액은 현재 쓸 수 있는 금액이고, 사용내역은 이미 결제에 쓴 금액을 확인하는 곳입니다. 결제할 곳을 찾는다면 앱의 가맹점 찾기를 이용하세요. <a href="https://play.google.com/store/apps/details?hl=ko&amp;id=com.komsco.kpay" target="_blank" rel="noopener noreferrer">한국조폐공사 앱 기능 안내 ↗</a></p>
<h3>2025년 12월분을 다시 확인하려는 경우</h3>
<p>2025년 12월 소비 증가분의 환급 상한은 3만 원이었으며, 공식 안내의 지급 예정일은 2026년 1월 15일이었습니다. 앞선 달의 월 최대 10만 원 안내를 12월분에 그대로 적용하면 예상액을 잘못 계산하게 됩니다. 지급 예정일은 개인별 입금 확인을 대신하지 않으므로 실제 지급과 사용 내역은 앱에서 확인하세요. <a href="https://www.korea.kr/news/policyNewsView.do?newsId=148955442" target="_blank" rel="noopener noreferrer">2025년 12월 연장 공식 안내 ↗</a></p>
<p>새로운 환급 사업을 찾는다면 <a href="https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310" target="_blank" rel="noopener noreferrer">중소벤처기업부 최신 발표 ↗</a>에서 모집 기간이 명시된 공고를 확인하세요.</p>''',
    },
    '611000000127': {
        'period': '2025.6.11.(수) 10:00 ~ 6. 24.(화)18:00',
        'end': '2025-06-24',
        'notice': '이 자료는 2025년 서울시 청년월세지원 모집입니다. 2025년과 2026년 서울시 신규 접수는 모두 종료됐습니다.',
        'body': '''
<h3>이미 선정됐다면 마이페이지에서 청구 상태를 확인하세요</h3>
<p>서울주거포털에 로그인한 뒤 마이페이지에서 청년월세지원 신청 건을 열어 진행 상태와 지급 내역을 확인하세요. 선정된 회차의 청구 안내에서 제출 기간과 이체 증빙을 확인합니다. 예를 들어 2026년 모집에서 선정됐다면 2025년 공고의 일정을 적용하지 말고 2026년 선정 안내를 기준으로 확인하세요. <a href="https://housing.seoul.go.kr/site/main/content/sh01_060513" target="_blank" rel="noopener noreferrer">서울주거포털 청년월세지원 안내 ↗</a></p>
<h3>처음 신청하려면 다음 모집 공고를 확인하세요</h3>
<p>2025년 모집은 6월 24일 18시에, 2026년 모집은 5월 19일 18시에 마감됐습니다. 서울시는 2026년 11월 12일 안내에서 2027년 모집을 공고할 예정이라고 밝혔습니다. 해당 안내에는 접수일이 없으므로 새 공고에서 접수 기간과 임대차·소득 기준을 다시 확인하세요.</p>
<p><a href="https://housing.seoul.go.kr/site/main/board/notice/12478" target="_blank" rel="noopener noreferrer">2025년 서울시 모집 공고 ↗</a> · <a href="https://housing.seoul.go.kr/site/main/board/notice/12667" target="_blank" rel="noopener noreferrer">2026년 서울시 모집 공고 ↗</a> · <a href="https://soco.seoul.go.kr/youth/bbs/BMSR00174/view.do?boardId=6734&amp;menuNo=400043&amp;pageIndex=1" target="_blank" rel="noopener noreferrer">서울시 다음 모집 안내 ↗</a></p>''',
    },
    '135200005013': {
        'period': '2026.05.04~2026.05.20',
        'end': '2026-05-20',
        'notice': '2026년 청년내일저축계좌 신규 신청은 5월 20일에 종료됐습니다. 신청 결과와 가입 후 관리 방법은 아래에서 확인할 수 있습니다.',
        'body': '''
<h3>5월에 신청했다면 선정 결과와 계좌 개설을 각각 확인하세요</h3>
<p>복지부는 2026년 모집의 선정 결과를 8월 중 개별 문자와 자산형성포털로 안내한다고 공지했습니다. 문자를 찾기 어렵다면 자산형성포털에서 선정 결과를 먼저 확인하세요. 선정 안내를 받았는데 계좌 개설을 놓쳤다면, 지금 개설이 가능한지 관할 행정복지센터나 자산형성지원콜센터(1522-3690)에 문의하세요. <a href="https://m.bokjiro.go.kr/ssis-tem/cms/mob/news/news/1309724_1122.html" target="_blank" rel="noopener noreferrer">복지부 2026년 모집·선정 안내 ↗</a></p>
<h3>가입 중이라면 납입 내역과 교육 이수 시간을 챙기세요</h3>
<p>만기 지급을 준비한다면 본인 저축이 실제 입금됐는지 확인하고, 자립역량교육 이수 시간을 따로 확인하세요. 자산형성포털은 근로·사업활동 지속, 3년간 본인 적립, 교육 10시간, 자금사용계획서 제출을 만기 지급 기준으로 안내합니다. 소득이 끊겨 납입이 어려워졌다면 자동이체를 끊기 전에 담당 기관에 적립중지 가능 여부를 문의하세요. <a href="https://hope.welfareinfo.or.kr/bsns/bsnsIntrcnAcc.do" target="_blank" rel="noopener noreferrer">자산형성포털 가입 유지·만기 기준 ↗</a></p>
<p>다음 신규 모집을 기다린다면 <a href="https://hope.welfareinfo.or.kr/" target="_blank" rel="noopener noreferrer">자산형성포털 공지 ↗</a>에서 모집연도와 접수 기간을 확인하세요.</p>''',
    },
    'GES000000110': {
        'period': '2026-2학기 신청기간 : 2026.7.1.~2026.11.17.',
        'end': '2026-11-17',
        'executionEnd': '2026-11-19',
        'notice': '2026년 2학기 취업 후 상환 학자금대출의 등록금·생활비 신청과 실행 기간은 모두 종료됐습니다.',
        'body': '''
<h3>신청만 했는지, 실제로 대출이 실행됐는지 확인하세요</h3>
<p>등록금·생활비 대출은 11월 17일 18시까지 신청하고 11월 18일 17시까지 실행하는 일정이었습니다. 한국장학재단에 로그인해 신청현황과 실행 여부를 확인하세요. 두 항목을 신청했다면 각각 확인합니다. 예를 들어 생활비만 실행했다면 등록금은 별도로 처리 여부를 확인해야 합니다. 실행 여부나 학교 수납 처리가 불명확하면 한국장학재단(1599-2000)과 학교 등록 담당 부서에 확인하세요. <a href="https://www.kosaf.go.kr/ko/notice.do?mode=view&amp;seqNo=20994" target="_blank" rel="noopener noreferrer">한국장학재단 신청·실행 매뉴얼 ↗</a></p>
<h3>전환대출의 마감은 별도였습니다</h3>
<p>2026년 2학기 전환대출은 11월 18일 18시에 신청, 11월 19일 17시에 실행이 마감됐습니다. 해당 학기에 실행한 일반 상환 대출을 조건 충족 시 취업 후 상환으로 바꾸는 절차입니다. <a href="https://www.kosaf.go.kr/ko/tuition.do?pg=tuition04_05_01" target="_blank" rel="noopener noreferrer">전환대출 공식 안내 ↗</a></p>
<p>다음 학기를 준비한다면 <a href="https://www.kosaf.go.kr/ko/tuition.do?pg=tuition01" target="_blank" rel="noopener noreferrer">한국장학재단 학자금대출 일정표 ↗</a>에서 학기, 신청 마감, 실행 마감을 각각 확인하고 학교 등록금 납부 기간과 대조하세요.</p>''',
    },
}


def archived_round(row, current):
    edition = ROUNDS.get(row.get('id'))
    if edition is None or row.get('endDate') != edition['end']:
        return None
    if ''.join((row.get('period') or '').split()) != ''.join(edition['period'].split()):
        return None
    if current.astimezone(ZoneInfo('Asia/Seoul')).date().isoformat() <= edition.get('executionEnd', edition['end']):
        return None
    return edition
