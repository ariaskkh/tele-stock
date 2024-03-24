import sys
sys.path.append('/Users/dean/Desktop/programming/tele-stock/src')
import requests
import pandas as pd
from private_data import DART_API_KEY


## 자기주식취득 공시 데이터 가져오기
page_no=1
page_count=100
bgn_de='20240320' # 추후 필요 시 오늘 날짜로 수정
end_de='20240322'
pblntf_detail_ty='B001' # 주요사항 보고서

results_all=pd.DataFrame()

while(True):
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        'crtfc_key': DART_API_KEY,
        'page_no' : str(page_no),
        'page_count' : str(page_count),
        'bgn_de' : bgn_de,
        'end_de' : end_de,
        'pblntf_detail_ty' : pblntf_detail_ty,
    }
    
    # 결과를 json형태로 저장
    results = requests.get(url, params=params).json()
    # 결과 중 실제 공시 정보가 있는 부분만 DataFrame으로 저장
    results_df = pd.DataFrame(results['list'])
    # 하나의 DataFrame으로 만듦
    results_all = pd.concat([results_all, results_df])
    
    total_page = results['total_page']

    if page_no == total_page:
        break

    page_no += 1

# 자기주식 관련된 다른 것들도 처리해야함
keyword = '주요사항보고서(자기주식취득결정)' 
# 법인 Y(코스피), K(코스닥). 거래정지, 비상장 회사 제외
df = results_all.loc[(results_all['report_nm'] == keyword) & ((results_all['corp_cls'] == 'K') | (results_all['corp_cls'] == 'Y'))]

# rcept_no를 index로
df=df.set_index('rcept_no')
# print(df.shape) # (행 개수, 열 개수)
# print(df)


###############################################################


## 자기주식취득 상세 데이터 가져오기
details = pd.DataFrame()
exec_check = [] #회사별 중복실행 방지
for idx, row in df.iterrows():
    # 주요사항보고서 자기주식 취득결정 상세 요청인자
    crtfc_key = DART_API_KEY
    corp_code = row['corp_code'] # 이것만 수정

    if corp_code in exec_check:
        continue

    exec_check.append(corp_code)

    url = 'https://opendart.fss.or.kr/api/tsstkAqDecsn.json'
    params = {
        'crtfc_key': crtfc_key,
        'corp_code': corp_code,
        'bgn_de': bgn_de,
        'end_de': end_de
    }

    # 결과 데이터를 json으로 저장
    results = requests.get(url, params=params).json()
    results_df_details = pd.DataFrame(results['list'])
    details = pd.concat([details, results_df_details])

# 데이터 종류 확인 - https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020038
"""
'rcept_no': 접수번호
'aqpln_stk_ostk' - 취득예정주식(주)(보통주식)
'aqpln_stk_estk' - 취득예정주식(주)(기타주식)
'aqpln_prc_ostk' - 취득예정금액(원)(보통주식)
'aqpln_prc_estk' - 취득예정금액(원)(기타주식)
'aqexpd_bgd' - 취득예상기간(시작일)
'aqexpd_edd' - 취득예상기간(종료일)
'hdexpd_bgd' - 보유예상기간(시작일)
'hdexpd_edd' - 보유예상기간(종료일)
'aq_wtn_div_ostk' - 취득 전 자기주식 보유현황(배당 가능 범위 내 취득)(보통주식)
'aq_wtn_div_estk' - 취득 전 자기주식 보유현황(배당 가능 범위 내 취득)(기타주식)
'eaq_ostk' - 취득 전 자기주식 보유현황(기타취득)(보통주식)
'eaq_estk' - 취득 전 자기주식 보유현황(기타취득)(기타주식)
"""

details=details[['rcept_no','aqpln_stk_ostk','aqpln_stk_estk',
     'aqpln_prc_ostk','aqpln_prc_estk','aqexpd_bgd','aqexpd_edd',
     'hdexpd_bgd','hdexpd_edd','aq_wtn_div_ostk','aq_wtn_div_estk',
      'eaq_ostk','eaq_estk']]

details=details.set_index('rcept_no')

print(details)


###############################################################