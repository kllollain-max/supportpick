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
    '611000019611': {
        'period': '2025.02.24~2025.11.30',
        'end': '2025-11-30',
        'notice': '이 자료는 2025년 서울엄마아빠택시 접수 일정입니다. 2026년 신청과 이용 안내는 서울시 공식 페이지에서 확인하세요.',
        'body': '''
<h3>2026년 신청은 서울시 공식 페이지에서 확인하세요</h3>
<p>서대문구의 2026년 안내에 따르면 1월 2일부터 연중 신청을 받으며 예산이 소진되면 종료됩니다. 신청하려는 달에 영아가 24개월 이하인지, 양육자와 영아가 주민등록상 함께 등재돼 있는지 확인하고, 탄생육아 몽땅정보통에서 실제 접수 상태를 확인하세요. <a href="https://www.sdm.go.kr/news/news/notice.do?mode=view&amp;sdmBoardSeq=308916" target="_blank" rel="noopener noreferrer">서대문구 2026년 안내 ↗</a></p>
<h3>이미 받은 포인트의 사용기한은 따로 확인하세요</h3>
<p>2026년 안내의 사용기한은 최종 승인일로부터 1년이 되는 달의 말일입니다. 택시를 예약하기 전에 본인 승인일과 포인트 잔액, 이용할 택시 운영사를 확인하세요. <a href="https://umppa.seoul.go.kr/hmpg/sprt/bzin/bzmgComtDetail.do?biz_mng_no=3EF7489ACF614F939FEF8514308797D2" target="_blank" rel="noopener noreferrer">서울시 2026년 신청·이용 안내 ↗</a></p>''',
    },
    '626000000633': {
        'period': '2026.8.18.~8.24.',
        'end': '2026-08-24',
        'notice': '2026년 부산청년 중개보수 및 이사비 지원 접수는 8월 24일 18시에 마감됐습니다.',
        'body': '''
<h3>이미 신청했다면 선정 문자와 마이페이지를 확인하세요</h3>
<p>부산청년플랫폼은 선정·미선정 문자를 보내고, 결과 통지 후 15일 안에 선정자 계좌로 지급한다고 안내합니다. 문자를 받지 못했다면 마이페이지에서 신청 내역을 먼저 확인하세요. 선정 통지를 받았는데 입금이 확인되지 않으면 통지일과 제출한 계좌를 대조한 뒤 부산경제진흥원(051-241-7859)에 문의하세요. <a href="https://young.busan.go.kr/index.nm?menuCd=271" target="_blank" rel="noopener noreferrer">부산청년플랫폼 결과·지급 안내 ↗</a></p>
<h3>다음 모집을 준비한다면 비용 항목과 증빙을 구분하세요</h3>
<p>2026년 공고에선 중개보수와 이사비를 따로 신청할 수 있었습니다. 이삿짐 운송과 함께 청소를 결제했다면 항목별 지출을 확인할 수 있는 영수증을 보관하세요. 2026년 기준으로 청소비와 개인 차량 렌트비는 제외됐습니다. 다음 모집의 전입 기준일과 증빙 요건은 새 공고에서 확인하세요. <a href="https://www.busan.go.kr/nbgosi/view?curPage=1&amp;gosiGbn=A&amp;sno=79008" target="_blank" rel="noopener noreferrer">부산시 2026년 공고 ↗</a></p>''',
    },
    '628000000155': {
        'period': '2026년 3월 30일(월) 09:00 ~ 5월 29일(금) 16:00',
        'end': '2026-05-29',
        'notice': '2026년 인천시 청년월세 지원 신규 접수는 5월 29일 16시에 마감됐습니다. 기존 신청자의 결정 통보와 지급은 별도입니다.',
        'body': '''
<h3>신청했다면 결정 통보와 월세 지급을 확인하세요</h3>
<p>인천시 군·구 사업팀이 지원 여부를 결정해 통보합니다. 인천청년포털은 선정된 신규 신청자의 경우 5월분 월세부터 소급하고, 월세 지원금은 매월 25일에 지급한다고 안내합니다. 토요일이나 공휴일이면 그 전날입니다. 결정 통보를 받지 못했거나 임대차계약이 바뀌었다면 포털 하단의 관할 군·구 연락처에서 본인 결정 상태와 변경 신청 절차를 확인하세요.</p>
<h3>다음 모집에서는 본인의 접수처부터 확인하세요</h3>
<p>2026년 온라인 접수는 19~34세는 복지로, 35~39세는 인천청년포털이었습니다. 다음 모집에서는 해당 연도 출생연도 기준과 본인 접수처를 새로 확인하세요. <a href="https://youth.incheon.go.kr/dwelling/monthly.jsp" target="_blank" rel="noopener noreferrer">인천청년포털 사업안내·군구 연락처 ↗</a></p>''',
    },
    'O00388400004': {
        'period': '연 1회 / 2025.07.15~2025.08.25',
        'end': '2025-08-25',
        'notice': '이 자료는 2025년 강원특별자치도 학자금대출 이자지원 접수 일정입니다. 2026년 접수도 마감됐고 강원인재원이 최종 결과를 공고했습니다.',
        'body': '''
<h3>2026년에 신청했다면 최종 결과 공고를 확인하세요</h3>
<p>강원인재원은 2026년 10월 23일 최종 선발결과를 게시하고 선발자에게 문자를 발송할 예정이라고 안내했습니다. 문자를 찾기 어렵다면 먼저 결과 공고의 첨부파일을 확인하고, 본인 선발 여부나 반영 시점이 불명확하면 강원인재원 인재육성팀(033-254-7777, 내선 201)에 문의하세요. <a href="https://injae.gwd.go.kr/injae/community/notice?seq=2971" target="_blank" rel="noopener noreferrer">강원인재원 2026년 최종 선발결과 ↗</a></p>
<h3>접수 기간과 지원 대상 이자 발생 기간을 따로 보세요</h3>
<p>2026년 접수는 7월 13일 14시부터 8월 24일 18시까지였고, 공고에서 다룬 이자는 2025년 7월 1일부터 2026년 6월 30일까지 발생한 이자였습니다. 다음 모집을 준비한다면 새 공고의 이자 산정 기간과 거주·학적 기준을 확인하세요. <a href="https://injae.gwd.go.kr/injae/community/notice?mode=list&amp;seq=2942" target="_blank" rel="noopener noreferrer">강원인재원 2026년 모집 공고 ↗</a></p>''',
    },
    '419100000007': {
        'period': '2026.05.01~2026.06.19',
        'end': '2026-06-19',
        'notice': '원주시 2026년 전입청년 교통비 모집은 6월 19일에 끝났습니다. 선정된 사람의 지원기간은 2027년 6월까지입니다.',
        'body': '''
<h3>선정된 청년은 교통비 증빙을 분기별로 모아두세요</h3>
<p>원주시는 2026년 7월부터 2027년 6월까지 발생한 관외 출퇴근 교통비를 분기별로 후불 지급한다고 안내합니다. 고속·시외버스, 기차 또는 승용차 유류비 실비를 월 최대 10만 원까지 지원하므로, 예를 들어 기차표를 결제했다면 출퇴근일과 결제 내역을 함께 정리하세요. 분기별 제출기한과 인정 증빙은 선정 안내나 복지정책과(033-737-2307)에서 확인하세요.</p>
<h3>다음 모집을 기다린다면 직장 소재지를 먼저 확인하세요</h3>
<p>2026년 공고는 원주에 거주하면서 원주 밖 직장으로 출퇴근하는 청년을 대상으로 했습니다. 다음 공고에서는 전입 기준일, 직장 소재지 요건, 기존 참여자 제한을 다시 확인하세요. <a href="https://www.wonju.go.kr/wjyouth/contents.do?key=6005" target="_blank" rel="noopener noreferrer">원주시 모집·분기별 지급 안내 ↗</a></p>''',
    },
    '648000001022': {
        'period': '2026. 7. 23.(목) ~ 2026. 9. 6.(일)',
        'end': '2026-09-06',
        'notice': '경상남도 2026년 대학생 학자금대출 이자지원 접수는 9월 6일에 끝났습니다.',
        'body': '''
<h3>지원 대상 이자와 접수 기간을 따로 보세요</h3>
<p>2026년 공고에서 지원 대상으로 본 이자는 2025년 7~12월과 2026년 1~6월에 발생한 이자입니다. 예를 들어 2026년 7월에 발생한 이자는 이 회차의 대상 기간 밖입니다. 경남바로서비스는 예산을 초과하면 소득 구간에 따라 지원 규모가 달라질 수 있다고 안내합니다. 이미 신청했다면 결과나 반영 일정을 교육인재과(055-211-2464)에 확인하세요. <a href="https://baro.gyeongnam.go.kr/baro/policyView.es?mid=a10703000000&amp;policy_no=1637" target="_blank" rel="noopener noreferrer">경남바로서비스 지원 범위·문의처 ↗</a></p>
<h3>다음 공고에서 학적별 증빙을 확인하세요</h3>
<p>2026년 기준 재·휴학생은 재·휴학증명서, 졸업·수료자는 졸업증명서와 건강보험 자격득실확인서를 준비하는 방식이었습니다. 다음 모집에서는 학적 기준일과 서류 발급일을 확인한 뒤 발급받으세요. <a href="https://www.kosaf.go.kr/ko/notice.do?mode=view&amp;page=1&amp;seqNo=21116" target="_blank" rel="noopener noreferrer">한국장학재단 2026년 안내 ↗</a></p>''',
    },
    '641000000180': {
        'period': '2025.11.14.까지',
        'end': '2025-11-14',
        'notice': '이 페이지의 신청기한은 2025년 안내입니다. 2026년에 받은 경기도 생리용품 지원금은 12월 31일까지 사용할 수 있습니다.',
        'body': '''
<h3>2026년 지급분이 있다면 잔액과 가맹점을 확인하세요</h3>
<p>경기도는 2026년 지급분을 12월 31일까지 사용할 수 있다고 안내합니다. 경기지역화폐에서 잔액을 확인하고, 결제 전에 해당 시·군의 경기지역화폐 가맹 편의점인지 확인하세요. 온라인은 배달특급의 여성청소년 생리용품 전용몰을 이용할 수 있습니다. <a href="https://web1.gg.go.kr/contents/contents.do?ciIdx=987253&amp;menuId=1534092" target="_blank" rel="noopener noreferrer">경기도 사용처·사용기한 안내 ↗</a></p>
<h3>새로 신청하려면 거주 시·군의 접수 안내를 확인하세요</h3>
<p>경기민원24에 표시된 2026년 10월 21~30일 온라인 접수는 마감됐습니다. 거주 시·군의 참여 여부, 방문 접수 및 예산 잔여 여부는 관할 행정복지센터에 확인하세요. <a href="https://gg24.gg.go.kr/svcreqst/selectSvcReqst.do?svc_seq=937" target="_blank" rel="noopener noreferrer">경기민원24 접수·시군 안내 ↗</a></p>''',
    },
    '653000000012': {
        'period': '2026-06-01~2026-08-31',
        'end': '2026-08-31',
        'notice': '강원특별자치도 2026년 신혼부부 주거자금 대출이자 지원 접수는 끝났습니다. 11월 19일자 확정 수정 공고에서 결과를 확인할 수 있습니다.',
        'body': '''
<h3>이미 신청했다면 11월 19일 수정 공고를 확인하세요</h3>
<p>강원특별자치도가 지원대상자를 확정한 뒤 수정 공고를 냈습니다. 이전 발표를 확인했더라도 최신 첨부파일에서 본인 신청 건을 확인하고, 지급이나 보완 안내가 불명확하면 공고의 담당 부서로 문의하세요. <a href="https://state.gwd.go.kr/portal/bulletin/notification?articleSeq=273196" target="_blank" rel="noopener noreferrer">강원특별자치도 확정 수정 공고 ↗</a></p>
<h3>지원액을 볼 때는 실제 납부 이자부터 확인하세요</h3>
<p>2026년 사업은 실제 납부한 전·월세 대출 이자를 연 1회 정산하는 방식입니다. 대출잔액 한도와 지원율 상한이 있으므로 실제 납부한 이자와 지원율을 모두 확인해야 합니다. 다음 모집에서는 대출 종류와 혼인·거주 기준도 새 공고에서 확인하세요. <a href="https://www.inje.go.kr/egf/bp/board/article/download?fileSeq=125509" target="_blank" rel="noopener noreferrer">2026년 모집 원문 PDF ↗</a></p>''',
    },
    '628000000748': {
        'period': '2026. 5. 4. ~ 5. 15.',
        'end': '2026-05-15',
        'notice': '인천 2026년 재직청년 드림For청년통장 신규 접수는 5월 15일 18시에 마감됐습니다.',
        'body': '''
<h3>신청 결과와 가입 완료 여부를 확인하세요</h3>
<p>2026년 공고의 선정 발표 예정일은 6월 30일이었으며, 선정 후 오리엔테이션에 불참하면 선정이 취소된다고 안내했습니다. 결과나 가입 여부를 확인하려면 신청 당시 안내를 찾아보고 인천테크노파크 고용안정센터에 문의하세요. <a href="https://youth.incheon.go.kr/bbs/bbsMsgDetail.do?bcd=notice&amp;msg_seq=464" target="_blank" rel="noopener noreferrer">인천청년포털 2026년 모집·선정 안내 ↗</a></p>
<h3>가입했다면 본인 납입과 만기 지원금을 따로 확인하세요</h3>
<p>2026년 안내 기준으로 본인이 매월 15만 원을 36개월 납입하면 540만 원을 모으고, 만기 시 인천시 지원금 540만 원을 일괄 지급하는 구조입니다. 퇴사나 이사를 앞두고 있다면 가입 당시 안내나 담당 기관에서 유지 조건과 필요한 신고를 먼저 확인하세요. <a href="https://www.itp.or.kr/intro.asp?tmid=494" target="_blank" rel="noopener noreferrer">인천테크노파크 사업안내 ↗</a></p>''',
    },
    '154300000012': {
        'period': '2026. 7. 2. ~ 8. 13.',
        'end': '2026-08-13',
        'notice': '2026년 FTA 피해보전직불금 접수는 8월 13일에 끝났습니다. 농림축산식품부는 염소고기 대상 지급을 11월 중순부터 시작한다고 발표했습니다.',
        'body': '''
<h3>신청한 농가는 관할 지자체에서 확정 내역을 확인하세요</h3>
<p>농식품부는 접수 뒤 자격 검증과 현장 조사를 거쳐 지급 대상을 선정했습니다. 11월 중순은 전체 지급 시작 시점이므로 개인별 입금일, 확정된 지급 마릿수와 금액은 관할 시·군·구청 축산 담당 부서나 읍·면·동 행정복지센터에 확인하세요.</p>
<h3>2026년 지급 품목과 대상 기준을 확인하세요</h3>
<p>2026년 지급 대상 품목은 염소고기입니다. 같은 농가에서 다른 축종을 함께 키워도 다른 축종의 사육 마릿수는 이 회차 지급 내역과 구분해 확인하세요. <a href="https://www.mafra.go.kr/bbs/home/792/611367/download.do" target="_blank" rel="noopener noreferrer">농림축산식품부 11월 10일 지급 발표 PDF ↗</a></p>''',
    },
    '370000000129': {
        'period': '2026.03.03~2026.06.30',
        'end': '2026-06-30',
        'notice': '울산청년정책플랫폼은 2026년 울산 남구 청년 자격시험 응시료 지원을 접수 마감으로 표시합니다.',
        'body': '''
<h3>이미 신청했다면 남구 관할 신청 건을 확인하세요</h3>
<p>울산시 전체 사업 일정과 남구의 접수 상태를 따로 확인하세요. 올해 남구로 신청했다면 접수 내역과 보완 요청이 있는지 확인하고 결과가 불명확하면 공식 플랫폼의 남구 담당 창구로 문의하세요.</p>
<h3>다음 사업을 준비한다면 응시일을 기록하세요</h3>
<p>울산청년정책플랫폼은 2027년 2~3월 사업 시행과 2026년 12월 1일 이후 응시 시험부터 지원 가능하다는 계획을 안내합니다. 시험 응시일과 결제 영수증을 보관하고, 남구 공고가 나오면 인정되는 시험과 서류를 다시 확인하세요. <a href="https://www.ulsan.go.kr/s/ulsanyouth/contents.do?contentsId=3771" target="_blank" rel="noopener noreferrer">울산청년정책플랫폼 구·군 상태와 다음 사업 계획 ↗</a></p>''',
    },
    '328000000152': {
        'period': '2026. 3. 18. ~ 4. 30.',
        'end': '2026-04-30',
        'notice': '영도구 2026년 청년동아리활동 지원 모집은 연장된 4월 30일에 끝났습니다. 선정 동아리 활동 일정은 11월 30일까지입니다.',
        'body': '''
<h3>선정된 동아리는 마지막 활동과 정산 일정을 확인하세요</h3>
<p>부산청년플랫폼은 활동 일정을 5월 11일부터 11월 30일까지로 안내합니다. 이 기간은 선정 동아리의 활동 기간입니다. 마지막 활동을 앞두고 있다면 지급 대상 참여자와 활동일, 증빙 제출 일정이 선정 안내와 일치하는지 확인하세요. 정산 서류와 제출일은 영도구청 신성장전략과(051-419-4615)에 확인할 수 있습니다.</p>
<h3>다음 모집을 준비한다면 구성원별 생활권을 점검하세요</h3>
<p>2026년 공고는 영도구 거주 또는 학교·직장·사업장 등 생활권이 영도구인 청년 4~12명으로 구성된 동아리를 대상으로 했습니다. 다음 회차에서는 인원과 생활권을 확인하는 기준일을 새 공고에서 확인하세요. <a href="https://young.busan.go.kr/policySupport/view.nm?bizSid=SUP0000003093&amp;menuCd=13" target="_blank" rel="noopener noreferrer">부산청년플랫폼 모집·활동 일정 ↗</a></p>''',
    },
    '129000000008': {
        'period': '2025. 4. 1. ~ 2026. 3. 31.',
        'end': '2026-03-31',
        'notice': '이 자료에 적힌 특수임무수행자 보상 신청 기간은 2026년 3월 31일까지였습니다.',
        'body': '''
<h3>마감일에 등기로 보냈다면 접수와 심의 상태를 구분해 확인하세요</h3>
<p>기한 연장 안내에서는 마감일 우체국 소인분까지 유효하다고 안내했습니다. 등기번호와 발송일을 준비해 보상심의위원회 민원실(02-3476-8010)에 접수 여부를 확인하세요. 접수 여부와 심의 결과는 각각 확인해야 합니다. <a href="https://www.yd.go.kr/DownLoad/etc/%EB%B0%98%EC%83%81%ED%9A%8C%EB%B3%B4%282025%EB%85%84%205%EC%9B%94%ED%98%B8%29.pdf" target="_blank" rel="noopener noreferrer">국방부 제공 접수 안내 PDF ↗</a></p>
<p>이미 통지를 받았다면 통지서에 기재된 결정과 후속 문의 경로를 확인하세요. 새 신청을 준비 중이라면 위원회에서 추가 접수 공지가 있는지 확인하세요. <a href="https://dep.mnd.go.kr/smc/278/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGc21jJTJGMzUwNzExJTJGT180MTE5MjMlMkZhcnRjbFZpZXcuZG8lM0Y%3D" target="_blank" rel="noopener noreferrer">국방부 보상심의위원회 심의결과 안내 ↗</a></p>''',
    },
    '305000000167': {
        'period': '2025.08.06~2025.09.05',
        'end': '2025-09-05',
        'notice': '이 자료는 2025년 동대문구 반려동물 전문인력 양성 2기 모집입니다. 해당 회차 접수는 9월 5일에 끝났습니다.',
        'body': '''
<h3>취업 교육을 찾는다면 공고 제목과 대상부터 확인하세요</h3>
<p>2025년 2기는 반려동물 관련 취업을 희망하는 동대문구민 대상이었습니다. 당시 신청서 링크보다 구청 청년정책고용과(02-2127-4974)에서 후속 전문인력 과정과 일정을 확인하세요. <a href="https://www.ddm.go.kr/www/selectBbsNttView.do?bbsNo=38&amp;key=198&amp;nttNo=174763" target="_blank" rel="noopener noreferrer">동대문구 2025년 2기 원문 ↗</a></p>
<p>키우는 반려견의 행동 교육이 목적이라면 구청의 우리동네 반려동물 교육 안내를 확인하세요. 이 공고는 보호자 대상 교육이며, 일정과 신청 상태는 해당 공고에서 확인할 수 있습니다. <a href="https://www.ddm.go.kr/www/selectBbsNttView.do?bbsNo=38&amp;key=198&amp;nttNo=195456" target="_blank" rel="noopener noreferrer">동대문구 2026년 보호자 교육 안내 ↗</a></p>''',
    },
    '318000000132': {
        'period': '2026.03.03. ~ 2026.03.13.',
        'end': '2026-03-13',
        'notice': '이 기록의 영등포 평생교육 바우처 접수 기간은 2026년 3월 13일까지였습니다.',
        'body': '''
<h3>이미 받은 바우처를 쓴다면 결제 전에 세 가지를 확인하세요</h3>
<p>본인 선정 안내에서 해당 연도 사용기한과 남은 금액을 확인하고, 수강 기관에 본인이 선정된 분야의 등록 강좌인지 문의하세요. 교재나 재료가 필요하면 수강료에 포함된 항목과 별도 구매 항목을 나눠 결제 전에 확인하세요.</p>
<p>선정 안내를 찾기 어렵거나 후속 모집을 기다린다면 YDP미래평생학습관에 올해 사용기한 또는 새 공고를 확인하세요. <a href="https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl?svcSeq=2109816&amp;bnefType=all&amp;svcId=318000000132" target="_blank" rel="noopener noreferrer">정부24 영등포구 자료·문의처 ↗</a></p>''',
    },
    '328000000143': {
        'period': '2026.04.20~2026.05.10',
        'end': '2026-05-10',
        'notice': '영도구 2026년 청년 창업자 임차료 지원 접수는 5월 10일 18시에 마감됐습니다.',
        'body': '''
<h3>이미 신청했다면 선정 안내와 정산 상태를 확인하세요</h3>
<p>부산청년플랫폼의 모집 공고는 5월 20일까지 구청 공지와 개별 연락으로 선정을 안내할 예정이라고 밝혔습니다. 결과나 정산이 불명확하다면 신청한 사업장과 접수 정보를 준비해 영도구 인구청년팀(051-419-4616)에 문의하세요.</p>
<p>다음 모집을 준비할 때는 대표자 주소와 사업장 주소, 사업자등록일, 실제 월 임차료를 나눠 확인하세요. 새 공고의 대상 요건과 대조하면 어느 서류가 필요한지 판단할 수 있습니다. <a href="https://young.busan.go.kr/policySupport/view.nm?bizSid=SUP0000003060&amp;lang=ko&amp;menuCd=13&amp;url=policySupport" target="_blank" rel="noopener noreferrer">부산청년플랫폼 2026년 공고·영도구 문의처 ↗</a></p>''',
    },
    '398000000296': {
        'period': '2023.02.13~2023.12.20',
        'end': '2023-12-20',
        'notice': '이 페이지의 구리시 신입생 체육복 지원 일정은 2023년 자료입니다. 현재 입학연도의 지원 여부는 학교나 구리시에 확인하세요.',
        'body': '''
<h3>올해 체육복을 사기 전에 학교에 지원 여부를 확인하세요</h3>
<p>학교에 입학연도, 입학 당시 주소, 체육복을 학교에서 지급하는지 또는 별도로 구입하는지를 함께 알려주면 확인에 도움이 됩니다. 타 지역 학교나 대안교육기관 입학생은 구리시 교육 담당 부서에 관할과 필요 서류도 확인하세요.</p>
<p>구리시는 과거 체육복 구입비를 지원했고, 2026년에는 별도로 대안교육기관 등 입학생 교복 지원을 안내했습니다. 2026년 교복 안내를 근거로 체육복까지 지원된다고 판단하지 말고, 구입할 품목이 지원 범위에 포함되는지 문의하세요. <a href="https://www.guri.go.kr/www/selectBbsNttView.do?bbsNo=42&amp;integrDeptCode=&amp;key=393&amp;nttNo=139639&amp;pageIndex=128&amp;searchCnd=all&amp;searchCtgry=&amp;searchKrwd=" target="_blank" rel="noopener noreferrer">구리시 2026년 교복 지원 보도자료 ↗</a></p>''',
    },
    '419100000009': {
        'period': '2026.03.03~2026.03.27',
        'end': '2026-03-27',
        'notice': '이 자료는 원주시 2026년 상반기 청년 동아리 활동비 모집입니다. 하반기 모집도 마감됐고 선정 결과가 공개됐습니다.',
        'body': '''
<h3>신청한 회차의 결과 공고를 열어보세요</h3>
<p>3월에 신청한 팀은 4월 2일 상반기 선정 결과를, 하반기에 신청한 팀은 9월 3일 하반기 선정 결과를 확인하세요. 같은 사업명으로 두 공고가 올라왔으므로 신청 회차와 공고 제목을 먼저 대조하면 됩니다. <a href="https://www.wonju.go.kr/www/selectBbsNttList.do?bbsNo=140&amp;integrDeptCode=&amp;key=216&amp;pageUnit=50&amp;searchCnd=SJ&amp;searchCtgry=&amp;searchKrwd=%EB%8F%99%EC%95%84%EB%A6%AC+%ED%99%9C%EB%8F%99%EB%B9%84" target="_blank" rel="noopener noreferrer">원주시 상·하반기 공고 목록 ↗</a></p>
<p>선정된 팀은 집행 전에 활동비 인정 항목과 증빙 제출 기한을 해당 회차의 안내에서 확인하세요. <a href="https://www.wonju.go.kr/www/selectBbsNttView.do?bbsNo=140&amp;integrDeptCode=&amp;key=216&amp;nttNo=491113&amp;pageIndex=11&amp;searchCnd=all&amp;searchCtgry=&amp;searchKrwd=" target="_blank" rel="noopener noreferrer">원주시 하반기 선정 결과 ↗</a></p>''',
    },
    '559000000439': {
        'period': '2025.02.01~2025.11.30',
        'end': '2025-11-30',
        'notice': '이 자료는 양주시 청춘사진관 2025년 일정입니다. 2026년 신청은 양주시청년센터의 해당 연도 안내에서 확인하세요.',
        'body': '''
<h3>2026년 접수 기간과 실제 촬영 일정을 따로 확인하세요</h3>
<p>양주시 통합예약의 2026년 모집 안내에 적힌 신청 기간은 2월 24일부터 11월 30일까지입니다. 촬영일은 별도 협의이므로, 이력서를 보낼 날짜가 정해져 있다면 접수 가능 여부와 촬영·사진 수령 일정을 각각 확인하세요. <a href="https://www.yangju.go.kr/yeyak/eduLctreWebView.do?eduLctreNo=12621&amp;key=2148" target="_blank" rel="noopener noreferrer">양주시 통합예약 2026년 모집 ↗</a></p>
<p>예약 화면의 정원과 신청 서류 안내를 읽고, 신청 승인이 확인되기 전에 사진관으로 바로 방문해야 하는지 불명확하다면 양주시청년센터(031-8082-6075)에 문의하세요.</p>''',
    },
    '628000000129': {
        'period': '2026.  3. 3. ~ 3. 18.',
        'end': '2026-03-18',
        'notice': '2026년 인천 구직청년 드림체크카드 접수는 3월 18일에 끝났으며 4월 13일 선정 결과가 게시됐습니다.',
        'body': '''
<h3>선정과 예비선정은 첨부파일을 따로 확인하세요</h3>
<p>인천청년포털의 4월 13일 공고에는 선정자와 예비선정자 명단이 별도 첨부돼 있습니다. 본인 결과와 마이페이지 상태를 확인하세요. 선정 뒤 지급 수단에 따라 계좌·카드 등록 절차가 달랐으므로, 아직 지급이 확인되지 않았다면 당시 선택한 방식과 처리 상태를 담당 기관에 문의하세요.</p>
<p>참여 중 취업·창업 또는 전출 등으로 자격 변동이 생기면 공고에 안내된 인천테크노파크 연락처(032-725-3072~3)에 확인하세요. <a href="https://youth.incheon.go.kr/bbs/bbsMsgDetail.do?bcd=notice&amp;msg_seq=454&amp;pgdiv=card" target="_blank" rel="noopener noreferrer">인천청년포털 선정·예비선정 및 후속 절차 ↗</a></p>''',
    },
    '641000000111': {
        'period': '2026.8.18. ~ 2026.9.18.',
        'end': '2026-09-18',
        'notice': '2026년 경기 가정보육 어린이 건강과일 일반 접수는 9월 18일에 끝났습니다. 선정 가정에는 11~12월 순차 배송됩니다.',
        'body': '''
<h3>배송이 아직 안 왔다면 선정과 배송 주소부터 확인하세요</h3>
<p>경기민원24의 일반 일정은 11~12월 중 과일 꾸러미를 한 번 배송하는 방식입니다. 선정 안내와 등록된 주소를 확인하세요. 선정 후 이사했거나 배송 문자를 받지 못했다면 관할 시·군에 배송지 수정 및 확인 방법을 문의하세요. 순차 배송이므로 같은 지역이라도 수령일은 다를 수 있습니다.</p>
<p>신청을 놓쳤다면 본인 시·군의 예외 접수 조건을 확인하세요. 예를 들어 용인시 공고는 8~9월 출생아의 부모급여 소급지원에 별도 조건을 안내합니다. 다른 시·군은 관할 공고를 확인하세요. <a href="https://gg24.gg.go.kr/svcreqst/selectSvcReqst.do?svc_seq=953" target="_blank" rel="noopener noreferrer">경기민원24 일정·문의처 ↗</a> · <a href="https://www.yongin.go.kr/user/bbs/BD_selectBbs.do?q_bbsCode=1001&amp;q_bbscttSn=20260805134331199&amp;q_clCode=1" target="_blank" rel="noopener noreferrer">용인시 추가 신청 안내 ↗</a></p>''',
    },
    '648000001117': {
        'period': '2025.11.05~2025.12.11',
        'end': '2025-12-11',
        'notice': '이 자료의 날짜는 2025년에 접수한 2026년 청년농업인 영농정착지원 1차 모집입니다.',
        'body': '''
<h3>모집 공고의 사업연도와 접수연도를 함께 확인하세요</h3>
<p>농식품부는 2026년 지원사업의 1차 선발을 2025년 11월에 시작했습니다. 접수가 열린 해와 실제 사업연도가 다를 수 있고, 같은 사업연도에도 추가 차수가 있을 수 있습니다. 거제시도 2026년 2차 모집을 별도로 공고했습니다. 다음 신청은 영농 예정지 시·군의 최신 공고에서 사업연도, 차수, 접수기간을 한꺼번에 확인하세요. <a href="https://mafra.go.kr/home/5109/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGaG9tZSUyRjc5MiUyRjU3NTgxMCUyRmFydGNsVmlldy5kbyUzRg%3D%3D" target="_blank" rel="noopener noreferrer">농식품부 2026년 1차 안내 ↗</a> · <a href="https://geoje.go.kr/board/view.geoje?boardId=BBS_0000008&amp;dataSid=306417779&amp;paging=ok&amp;startPage=7" target="_blank" rel="noopener noreferrer">거제시 2026년 2차 공고 ↗</a></p>
<p>이미 선정됐다면 본인 회차 지침에서 바우처 사용과 의무교육, 경영장부 기록 요건을 확인하세요. 정착지원금과 별도로 융자 자금이 필요한 경우 시·군의 연계 절차도 확인하세요. <a href="https://baro.gyeongnam.go.kr/baro/policyView.es?mid=a10703000000&amp;policy_no=258" target="_blank" rel="noopener noreferrer">경남바로서비스 사업·준수사항 ↗</a></p>''',
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
