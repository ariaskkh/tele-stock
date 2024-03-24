import sys
sys.path.append('/Users/dean/Desktop/programming/tele-stock/src')
import requests
import pandas as pd
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from private_data import DART_API_KEY # pylint: disable=import-error



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

# print(details)


###############################################################

# 취득 예정 주식 수 및 주가 확인

# axis = 1은 데이터 좌우로 병합, join = 'inner'은 교집합 병합 <-> 'outer'는 합집합 병합
df_all = pd.concat([df, details], axis = 1, join='inner')

cols=['aqpln_stk_ostk','aqpln_stk_estk',
     'aqpln_prc_ostk','aqpln_prc_estk','aq_wtn_div_ostk','aq_wtn_div_estk','eaq_ostk','eaq_estk']

#object -> int 변환
for col in cols:
    df_all[col] = df_all[col].str.replace(',', '').replace('-','0').replace('','0')

df_all[cols]=df_all[cols].astype('int64')
df_all['rcept_date'] = pd.to_datetime(df_all['rcept_dt'], format='%Y%m%d') # 20220115 -> 2022-01-15
df_all['aqexpd_bgd'] = pd.to_datetime(df_all['aqexpd_bgd'], format='%Y년 %m월 %d일')
df_all['aqexpd_edd'] = pd.to_datetime(df_all['aqexpd_edd'], format='%Y년 %m월 %d일')


colsForResult=['corp_name','stock_code','rcept_dt','rcept_date','aqpln_stk_ostk','aqpln_stk_estk',
     'aqpln_prc_ostk','aqpln_prc_estk', 'aqexpd_bgd']
for index, r in df_all[colsForResult].iterrows():
    corp_name = r['corp_name']
    stock_code = r['stock_code']
    rcept_date = r['rcept_date'] # 공시 접수 일자

    aqpln_stk_ostk = r['aqpln_stk_ostk'] # 취득예정주식(주)(보통주식)
    aqpln_stk_estk = r['aqpln_stk_estk'] # 취득예정주식(주)(기타주식)
    aqpln_prc_ostk = r['aqpln_prc_ostk'] # 취득예정금액(원)(보통주식)
    aqpln_prc_estk = r['aqpln_prc_estk'] # 취득예정금액(원)(기타주식)
    aqexpd_bgd = r['aqexpd_bgd'] # 취득 예상 기간(시작일)
    
    print('corp_name: ' + corp_name)
    print('접수일자 : ' + rcept_date.strftime('%Y-%m-%d')) # strftime: obt(Timestamp) -> str
    print('취득예정주식(주)보통주식 : ' + str(aqpln_stk_ostk))
    print('취득예정주식(주)보통주식 : ' + str(aqpln_stk_ostk))
    print('취득예정금액(원)(보통주식) : ' + str(aqpln_prc_ostk))
    print('취득예정금액(원)(기타주식) : ' + str(aqpln_prc_estk))
    print('취득예상기간(시작일) : ' + aqexpd_bgd.strftime('%Y-%m-%d')) 


    # 주가정보
    code = stock_code
    startdate = '2023-12-01'
    enddate = '2024-03-24'
    # Close(종가), Open, High, Low, Volume, Change
    df_stock = fdr.DataReader(code, startdate, enddate)[['Close']]

    plt.rc('font', family='AppleGothic')
    plt.figure(figsize=(6,2))
    plt.plot(df_stock.index, df_stock['Close']) # x, y축
    plt.title(corp_name)
    plt.xticks(rotation = 90) # x축 라벨
    
    plt.axvline(x = rcept_date, color = 'red') #공시 접수일자
    if aqexpd_bgd in df_stock.index:
        plt.axvline(x = aqexpd_bgd, color = 'green') #취득예상기간(시작일)
    plt.show()