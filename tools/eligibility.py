"""Conservative navigation fields derived only from explicit official conditions.
These fields never determine a person's entitlement or confirm actual intake.
"""
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
KST=ZoneInfo('Asia/Seoul')
DATE=r'(20\d{2})[.년/\-]\s*(\d{1,2})[.월/\-]\s*(\d{1,2})\s*일?\.?'
TAIL=r'\s*(?:\([월화수목금토일]\))?\s*(?:(\d{1,2}):([0-5]\d))?'
RANGE=re.compile(DATE+TAIL+r'\s*(?:~|～|∼|부터|–)\s*(?:(20\d{2})[.년/\-]\s*)?(\d{1,2})[.월/\-]\s*(\d{1,2})\s*일?\.?'+TAIL)
ALIASES={'서울':'서울특별시','부산':'부산광역시','대구':'대구광역시','인천':'인천광역시','광주':'광주광역시','대전':'대전광역시','울산':'울산광역시','세종':'세종특별자치시','경기':'경기도','강원':'강원특별자치도','충북':'충청북도','충남':'충청남도','전북':'전북특별자치도','전남':'전라남도','경북':'경상북도','경남':'경상남도','제주':'제주특별자치도'}
TARGETS={'청년':r'청년','부모':r'부모|보호자','학생':r'학생|재학','구직자':r'구직자|실업자|미취업','근로자':r'근로자|재직자','소상공인':r'소상공인|자영업자'}
def application_period(raw):
 raw=str(raw or '').strip();periods=[]
 result={'applicationPeriodKind':'needs_check','applicationPeriods':periods,'applicationPeriodEvidence':raw}
 if not raw:return result
 # Budget, discretionary rounds and incomplete dates require the official window.
 if re.search(r'예산|소진|별도\s*공고|추후|미정|수시|예정',raw):return result
 for m in RANGE.finditer(raw):
  y,mo,d,hh,mm,ey,em,ed,eh,emin=m.groups()
  try:
   start=date(int(y),int(mo),int(d));end=date(int(ey or y),int(em),int(ed))
   if end<start:raise ValueError()
   p={'start':start.isoformat(),'end':end.isoformat(),'text':m.group(0).strip()}
   if hh:p['startAt']=datetime(start.year,start.month,start.day,int(hh),int(mm),tzinfo=KST).isoformat()
   if eh:p['endAt']=datetime(end.year,end.month,end.day,int(eh),int(emin),tzinfo=KST).isoformat()
   if p.get('startAt','') and p.get('endAt','') and p['startAt']>p['endAt']:raise ValueError()
   periods.append(p)
  except ValueError:return {**result,'applicationPeriods':[]}
 remainder=RANGE.sub('',raw)
 if periods and not re.search(r'20\d{2}|\d{1,2}[월/]\s*\d{1,2}|\d+\s*시|\d{1,2}:\d{2}|마감.*변경|별도',remainder):result['applicationPeriodKind']='fixed'
 elif not periods and not re.search(r'20\d{2}|\d+[월/.]',raw) and re.search(r'상시|연중',raw):result['applicationPeriodKind']='ongoing'
 return result

def application_status(row,current):
 kind=row.get('applicationPeriodKind');periods=row.get('applicationPeriods') or []
 if kind=='ongoing':return '상시 신청'
 if kind!='fixed' or not periods:return '확인 필요'
 now=current.astimezone(KST);today=now.date().isoformat();states=[]
 for p in periods:
  if (p.get('endAt') and now>datetime.fromisoformat(p['endAt'])) or p['end']<today:states.append('접수 종료')
  elif (p.get('startAt') and now<datetime.fromisoformat(p['startAt'])) or p['start']>today:states.append('접수 예정')
  else:states.append('접수 중')
 return '접수 중' if '접수 중' in states else '접수 예정' if '접수 예정' in states else '접수 종료'

def navigation(row):
 text='\n'.join(str(row.get(k) or '') for k in ('target','selection'))
 conditions=[];tags=[]
 for clause in re.split(r'[\n;]',text):
  if not re.search(r'거주|주민등록|주소를?\s*두|사업장.*소재|소재.*사업장',clause):continue
  # Ambiguous exclusions / alternative conditions stay visible without exclusion.
  if re.search(r'제외|관계없이|무관|또는|이거나',clause):continue
  provinces=[short for short,long in ALIASES.items() if re.search(re.escape(long)+r'|'+re.escape(short)+r'(?=도|시|\s|에|내)',clause)]
  cities=re.findall(r'(?<![가-힣])([가-힣]{2,8}[시군구])(?=\s|에|내|민|거주|[.,])',clause)
  cities=[c for c in cities if c not in ALIASES.values() and c not in ('거주시','신청시','등록시','접수시','해당시')]
  nationwide=bool(re.search(r'전국\s*(?:거주|주민|대상)|지역\s*제한\s*없',clause))
  if provinces or cities or nationwide:conditions.append({'scope':'nationwide' if nationwide else 'local','regions':provinces,'cities':cities,'basis':'business' if '사업장' in clause else 'residence','evidence':clause.strip()[:600]})
 unique={}
 for c in conditions:
  key=(c['scope'],tuple(c['regions']),tuple(c['cities']),c['basis'])
  unique.setdefault(key,c)
 conditions=list(unique.values())
 for label,pattern in TARGETS.items():
  m=re.search(pattern,text)
  if m:tags.append({'label':label,'evidence':text[max(0,m.start()-50):m.end()+120].strip()})
 return {**application_period(row.get('period')),'agencyRegion':row.get('region') if row.get('regionBasis')=='agency_jurisdiction' else None,'eligibilityRegions':conditions,'eligibilityRegionStatus':'explicit' if len(conditions)==1 else 'needs_check','targetGroups':tags}
