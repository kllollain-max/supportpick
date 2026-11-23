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
}


def archived_round(row, current):
    edition = ROUNDS.get(row.get('id'))
    if edition is None or row.get('endDate') != edition['end']:
        return None
    if ''.join((row.get('period') or '').split()) != ''.join(edition['period'].split()):
        return None
    if current.astimezone(ZoneInfo('Asia/Seoul')).date().isoformat() <= edition['end']:
        return None
    return edition
