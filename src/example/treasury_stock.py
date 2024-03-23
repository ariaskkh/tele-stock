import sys
sys.path.append('/Users/dean/Desktop/programming/tele-stock/src')
from private_data import DART_API_KEY
import pandas as pd
import requests

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
print(df.shape) # (행 개수, 열 개수)
print(df)