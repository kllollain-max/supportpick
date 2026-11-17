"""A small authored reference desk, separate from copied API benefit facts."""
from html import escape
from detail_pages import shell
from benefit_analysis import ARTICLES, BENEFIT_ARTICLES, ARTICLE_REVIEW_DATES

MODIFIED = '2026-11-17'
API = 'https://www.data.go.kr/data/15113968/openapi.do'
GOV = 'https://plus.gov.kr/portal/benefitV2/'
BIZ = 'https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do'

GUIDES = [
('find-and-verify', '내 조건으로 지원금을 찾고 공식 공고와 대조하는 방법',
 '연령·가구·지역 필터가 알려주는 범위와 공식 자격 확인의 차이를 정리합니다.', '''
<h2>처음에는 넓게 찾고, 상세 조건으로 좁히세요</h2>
<p>목록에서 지역과 지원 분야를 먼저 선택하세요. 연령이나 가구 특성을 알고 있다면 상세 필터를 추가할 수 있습니다. ‘연령·가구 조건 미표기 자료 포함’을 켜면 분류값이 없는 자료도 함께 볼 수 있습니다. 결과가 너무 많으면 이 선택을 끄고, 결과가 없으면 다시 켜서 놓친 자료가 있는지 확인하세요.</p>
<p>필터에 걸리지 않았다고 지원 대상에서 제외된다는 뜻은 아닙니다. 기관이 제공한 분류와 상세 설명의 범위가 다르거나 분류 자체가 비어 있을 수 있습니다. 반대로 필터에 표시되었다고 모든 조건을 충족한 것도 아닙니다.</p>
<h2>같은 지역 표기라도 확인할 내용이 다릅니다</h2>
<div class="guide-table"><table><caption>지역 조건을 읽는 질문</caption><thead><tr><th scope="col">표시</th><th scope="col">추가로 확인할 것</th></tr></thead><tbody>
<tr><th scope="row">기관 지역</th><td>기관의 관할 지역인지, 신청인의 주민등록지 조건인지 구분합니다. 전입일·거주기간·사업장 소재지 기준은 지원대상 원문에서 찾습니다.</td></tr>
<tr><th scope="row">전국 안내</th><td>전국 기관에서 안내하더라도 특정 자격이나 지역별 접수 창구가 있는지 확인합니다.</td></tr>
<tr><th scope="row">확인 필요</th><td>전국 대상이라고 해석하지 말고 공식 상세의 대상 조건을 읽습니다.</td></tr></tbody></table></div>
<h2>연령·가구 조건은 이렇게 대조하세요</h2>
<p>연령 필터는 공식 API의 대상연령 시작·종료 분류를 사용합니다. 공고가 요구하는 나이의 기준일, 출생연도, 신청일 기준 여부는 별도로 읽어야 합니다. 자녀 지원사업을 부모가 찾아본다면 지원받는 자녀의 조건과 신청하는 보호자의 조건을 나누어 확인하세요.</p>
<p>‘한부모·조손가정’, ‘1인가구’, ‘다자녀가구’ 등은 공식 API의 해당 분류값이 있는 자료를 찾는 도구입니다. 가족관계가 같아도 소득·재산·세대 구성·거주기간 요건은 사업마다 다를 수 있으므로 지급액을 미리 확정하지 마세요.</p>
<h2>공식 안내를 찾았을 때의 확인 순서</h2>
<ol><li>사업명과 운영기관이 같은지 확인합니다. 비슷한 이름의 타 지역 사업을 혼동하지 않습니다.</li><li>대상·선정기준에서 나에게 적용되는 예외와 제외 조항을 찾습니다.</li><li>기간과 차수를 대조한 뒤 공식 신청 창구를 확인합니다.</li><li>지원금픽의 관심 저장이나 신청 메모에는 확인할 질문만 적고, 주민등록번호·계좌번호·증명서 원문은 입력하지 않습니다.</li></ol>
<p>정부24의 혜택알리미에는 나의 혜택·간편찾기·전체 혜택 메뉴가 있습니다. 기관이 보유한 정보를 이용하는 공식 맞춤 안내와, 지원금픽에서 선택한 관심 분류 검색은 범위가 다릅니다.</p>''', [(API,'공식 지원조건·상세정보 항목'), (GOV,'정부24 혜택알리미')]),
('compare-benefits', '비슷한 지원금 비교: 현금·융자·이용권과 중복지원 조건',
 '지급액만 비교하지 않고 지원방식·대상·기간·신청 경로를 나란히 확인하는 순서입니다.', '''
<h2>먼저 지원방식이 같은지 확인하세요</h2>
<p>이름에 ‘지원’이 들어간다는 이유로 모두 현금을 받는 사업으로 비교하면 혼동하기 쉽습니다. 목록의 지원방식과 상세의 지원내용·금액을 함께 읽으세요. 아래 표는 개별 사업의 지급 조건을 대신하는 표가 아니라, 공식 안내에서 확인할 질문을 정리한 도구입니다.</p>
<div class="guide-table"><table><caption>지원방식별 비교 질문</caption><thead><tr><th scope="col">방식</th><th scope="col">확인할 내용</th></tr></thead><tbody>
<tr><th scope="row">현금·감면</th><td>지급인지 비용 감면인지, 정액인지 실비인지, 개인·가구·월·연 단위인지 구분합니다.</td></tr>
<tr><th scope="row">융자·대출</th><td>빌리는 자금인지 확인하고 금리·상환기간·보증·심사 조건을 공식 안내에서 확인합니다. 대출 한도를 소득이나 무상 지원금처럼 합산하지 않습니다.</td></tr>
<tr><th scope="row">이용권·현물·서비스</th><td>사용처·사용기한·본인부담·제공 횟수와 실제 이용 가능한 서비스를 확인합니다.</td></tr></tbody></table></div>
<h2>지원금픽에서 두세 개를 나란히 보는 방법</h2>
<ol><li>목록의 ‘비교 선택’으로 최대 3개를 고릅니다. 이름이 비슷해도 운영기관과 지역을 먼저 살펴보세요.</li><li>‘선택한 지원금 비교’를 열면 공식 API의 대상·지원내용·기간·방법·서류와 조회일을 나란히 볼 수 있습니다.</li><li>차이가 있는 칸에서 각각 공식 안내를 열어 최신 공고와 대조합니다. 표가 길면 옆으로 이동해 모든 사업을 확인하세요.</li></ol>
<h2>중복 수혜는 합산하기 전에 확인합니다</h2>
<p>비교표에 두 사업이 함께 나온다는 사실은 동시 수혜 가능 근거가 아닙니다. 공고의 ‘중복지원’, ‘타 사업’, ‘지원 제외’, ‘동일 목적’ 문구를 찾아 각 사업의 담당기관에 확인하세요. 중복 관련 정보가 제공되지 않았다면 ‘가능’으로 해석하지 않고 확인할 질문으로 남깁니다.</p>
<p>예를 들어 주거비와 교육비 지원을 비교한다면 지원 목적뿐 아니라 지원받는 사람·대상 비용·지원 기간이 겹치는지 각각 적어보세요. 이는 문의를 준비하는 예시이며 어느 조합이 허용된다는 판정이 아닙니다.</p>
<h2>소상공인·사업자 지원을 비교할 때</h2>
<p>기업마당의 지원사업 공고에서도 지역·분야·신청기간을 함께 확인할 수 있습니다. 사업자 대상인지 개인 대상인지, 사업장 주소와 업종·업력 조건이 있는지 먼저 읽으세요. 사업별 지원 자격·지원내용·신청 순서를 확인한 뒤 비교하세요.</p>''', [(API,'공공서비스의 지원유형·지원내용·신청방법'), (BIZ,'기업마당 지원사업 공고')]),
('application-checklist', '지원금 신청 서류를 발급하기 전 확인할 준비 체크리스트',
 '공식 구비서류와 접수 방식을 기준으로 불필요한 발급과 접수 누락을 줄이는 준비 순서입니다.', '''
<h2>서류 목록보다 먼저 공식 신청 경로를 확인하세요</h2>
<p>지원금픽 상세의 관심 저장과 ‘내 신청에 기록’은 개인 메모 기능입니다. 공식 신청서가 제출되지 않습니다. 상세의 공식 안내를 열어 온라인·방문·우편 등 신청방법을 확인하고 실제 접수기관이 어디인지 찾으세요. 공식 온라인 신청 주소가 제공되지 않으면 임의 주소를 추정하지 않고 안내문이나 문의처를 이용합니다.</p>
<h2>구비서류를 읽는 네 가지 질문</h2>
<ul><li><strong>누구의 서류인가요?</strong> 신청인·지원대상자·가구원·사업자 중 누구를 증명하는지 확인합니다.</li><li><strong>언제 발급한 서류인가요?</strong> 공고의 발급일·기준일·유효기간을 확인한 뒤 발급합니다. 모든 사업에 공통인 유효기간이 있다고 단정하지 않습니다.</li><li><strong>내 경우에도 필요한가요?</strong> 필수와 해당자 제출을 나누고, 담당기관이 직접 확인하는 정보와 직접 내야 하는 증빙을 구분합니다.</li><li><strong>어떻게 내나요?</strong> 온라인 파일 형식·크기, 방문 원본 지참, 우편 도착 기준 등 공고에 적힌 제출 방식을 확인합니다.</li></ul>
<h2>개인정보를 적지 않는 준비표</h2>
<p>아래 체크는 화면에서만 사용하며 저장·제출되지 않습니다. 신청 관련 민감한 서류는 해당 기관의 공식 접수 화면에서만 제출하세요.</p>
<div class="preparation-checks"><label><input type="checkbox">현재 연도·신청 차수·지역이 맞는 공고를 찾았습니다.</label><label><input type="checkbox">필수 서류와 해당자 추가 서류를 나누었습니다.</label><label><input type="checkbox">발급 기준일·제출 형식·신청 마감 시각을 확인했습니다.</label><label><input type="checkbox">접수번호·신청내역 등 공식 완료 확인 방법을 확인했습니다.</label></div>
<h2>접수 후에도 기록할 것이 있습니다</h2>
<p>공식 창구의 접수 완료 화면이나 신청내역을 확인한 뒤, 내 신청에는 ‘접수 여부 확인함’처럼 상태만 기록하세요. 보완 요청이 오면 요청 기관·요청 내용·기한을 공식 화면에서 확인합니다. 지원금픽에 기록한 단계나 결과는 이용자가 직접 입력한 것이며 기관의 실제 심사 결과와 연동되지 않습니다.</p>
<h2>정보가 없거나 서로 다를 때</h2>
<p>구비서류가 빈칸이거나 목록·상세가 다르면 일반적인 증빙을 임의의 필수서류로 만들어 제출하지 마세요. ‘사업명, 신청 차수, 내 경우에 필요한 서류와 발급 기준일’을 담당기관에 문의하는 편이 정확합니다. 사이트 정정 문의에는 사업 ID와 공식 공고 주소만 남기고 성명·연락처·신청서·소득자료를 공개하지 마세요.</p>''', [(API,'구비서류·본인확인필요구비서류·공무원확인구비서류'), (GOV,'정부24 공식 서비스 탐색')]),
('deadlines-and-updates', '마감일·신청 차수·자료 조회일을 구분해서 읽는 방법',
 '상시·예산 소진·종료된 날짜 안내와 출처 수정일·조회일의 차이를 설명합니다.', '''
<h2>날짜가 있다는 것과 지금 접수 중이라는 것은 다릅니다</h2>
<p>지원금픽은 공식 API의 신청기한 원문을 보존합니다. 연도가 분명한 단일 시작·종료 기간만 날짜로 해석하며, 여러 차수나 해석이 불명확한 문장은 확인 필요로 표시합니다. 한국시간 날짜를 기준으로 기한 경과와 안내 기간 전을 구분하지만, 이는 실제 예산이나 기관의 접수 상황을 조회한 결과가 아닙니다.</p>
<div class="guide-table"><table><caption>기간 표시별 다음 행동</caption><thead><tr><th scope="col">표시</th><th scope="col">확인할 것</th></tr></thead><tbody>
<tr><th scope="row">기한 내 날짜 안내</th><td>공식 공고에서 차수·마감 시각·조기 종료 공지를 확인합니다.</td></tr><tr><th scope="row">상시 안내</th><td>현재 예산·대상·기관별 접수 요일이나 예약 필요 여부를 확인합니다.</td></tr><tr><th scope="row">예산 소진 여부 확인</th><td>최신 접수 종료 공지가 있는지 확인한 뒤 서류를 준비합니다.</td></tr><tr><th scope="row">기한 경과·기간 전</th><td>새 차수나 추가 모집 공고가 있는지 확인합니다. 이전 자료가 남아 있다는 이유로 현재 모집으로 해석하지 않습니다.</td></tr><tr><th scope="row">기간 확인 필요</th><td>원문과 담당기관에서 확인합니다. 연도가 없는 날짜에 올해를 자동으로 붙이지 않습니다.</td></tr></tbody></table></div>
<h2>시각은 날짜 필터보다 한 번 더 확인하세요</h2>
<p>예시로 ‘2026.11.17. 18:00 마감’인 공고라면 그 날짜가 목록에 남아 있어도 18시 이후에는 접수할 수 없을 수 있습니다. 이 예시는 실제 모집을 안내하는 것이 아닙니다. 날짜 필터는 시간 단위 접수를 확정하지 않으므로 마감 당일에는 기관 공고와 접수 화면을 직접 확인하세요.</p>
<h2>출처 수정일·API 조회일·해설 확인일</h2>
<ul><li><strong>출처 수정일:</strong> 기관이 자료에 제공한 수정 시점입니다. 목록과 상세의 수정일이 다를 수 있습니다.</li><li><strong>API 조회일:</strong> 지원금픽이 자료를 읽은 시점입니다. 같은 내용을 다시 조회했다고 새로운 모집이 생긴 것은 아닙니다.</li><li><strong>해설 확인일:</strong> 준비 해설을 공식 자료와 대조한 시점입니다. 개인 자격이나 접수 가능 여부를 심사한 시점은 아닙니다.</li></ul>
<h2>지난 자료를 발견했을 때</h2>
<p>지원금픽은 기존 원본과 공유 주소, 이용자의 저장·신청 기록을 보존합니다. 종료 여부가 명확한 날짜 안내는 경과 상태를 표시하고 최신 공식 공고로 확인하도록 안내합니다. 내용에 오류가 있다면 사업 ID·달라진 항목·공식 공고 주소를 문의·정정 게시판에 알려주세요.</p>''', [(API,'신청기한·목록 및 상세 수정일시'), (BIZ,'기간별 지원사업 공고 탐색')])
]


def write_guides(output, base, rows=None):
    entries=[]
    articles = ARTICLES + GUIDES
    for slug, title, description, body, sources in articles:
        modified = ARTICLE_REVIEW_DATES.get(slug, MODIFIED)
        path='guides/'+slug+'.html'
        refs=''.join('<li><a target="_blank" rel="noopener noreferrer" href="'+escape(url,quote=True)+'">'+escape(label)+' ↗</a></li>' for url,label in sources)
        links=''.join('<li><a href="'+other+'.html">'+escape(label)+'</a></li>' for other,label,*_ in articles if other!=slug)
        related_rows=sorted((sid,row) for sid,row in (rows or {}).items() if BENEFIT_ARTICLES.get(sid)==slug and (output/'benefits'/sid/'index.html').is_file())
        titles=[row['title'] for _,row in related_rows]
        def label(sid,row):
            title=row['title']
            if titles.count(title)>1:
                contact=str(row.get('contact') or '').split('||')[0].split('/')[0].strip()
                title+=' · '+(contact or '자료 '+sid)
            return title
        related=''.join('<li><a href="../benefits/'+sid+'/">'+escape(label(sid,row))+'</a></li>' for sid,row in related_rows)
        related='<h2>공식 API 자료와 대조하기</h2><ul>'+related+'</ul>' if related else ''
        html=('<nav class="breadcrumbs" aria-label="현재 위치"><a href="../">홈</a><span>›</span><span>신청 준비 안내</span></nav>'
              '<article class="detail-block"><h1>'+escape(title)+'</h1><p>'+escape(description)+'</p>'
              '<p class="source-meta">작성: 지원금픽 · 공식 자료 대조: '+modified+' · AI 보조로 작성한 신청 준비 안내입니다. 개인의 자격·선정 결과를 판정하지 않습니다.</p>'
              +body+related+'<h2>확인한 공식 자료</h2><ul>'+refs+'</ul><h2>이어서 확인하기</h2><ul>'+links+'</ul>'
              '<p><a href="../contact.html">오류·변경 사항 알려주기</a> · <a href="../">지원금 검색·비교하기</a></p></article>')
        (output/'guides').mkdir(exist_ok=True)
        (output/path).write_text(shell(title+' | 지원금픽',description,html,path,'../',base))
        if base:entries.append((path,modified))
    return entries
