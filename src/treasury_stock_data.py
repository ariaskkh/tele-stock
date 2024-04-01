from datetime import datetime, timedelta
import pandas as pd
import requests

from private_data import DART_API_KEY

DEFAULT_TIMEOUT = 5000

## 자기주식취득 공시 summary 데이터 가져오기
def get_treasury_stock_summary():
    page_no = 1 # 페이지 번호
    page_count = 100 # 페이지 별 건수
    start_date = get_date() # 검색 시작일
    end_date = get_date() # 검색 종료일
    major_info_report ='B001' # 주요사항 보고서
    
    # TODO: 데이터 프레임을 굳이 사용할 필요 없을 경우 삭제
    results_all = pd.DataFrame()
    
    while(True):
        url = "https://opendart.fss.or.kr/api/list.json"
        params = {
            'crtfc_key': DART_API_KEY,
            'page_no': str(page_no),
            'page_count': str(page_count),
            'bgn_de': start_date,
            'end_de': end_date,
            'pblntf_detail_ty': major_info_report
        }

        try:
            # 결과를 json 형태로 저장
            results = requests.get(url, params=params, timeout = DEFAULT_TIMEOUT).json()
        except requests.exceptions.HTTPError as e:
            print("GET - Http Error occurred ", e)
        except requests.exceptions.Timeout as e:
            print("GET - Timeout error occurred ", e)
        except requests.exceptions.RequestException as e: # 모든 exception의 기본 class
            print("GET - Error occurred ", e)


        # 결과 중 실제 공시 정보가 있는 부분만 DataFrame으로 저장
        results_df = pd.DataFrame(results['list'])
        # 하나의 DataFrame으로 만듦
        results_all = pd.concat([results_all, results_df])

        total_page = results['total_page']

        if page_no == total_page:
            break
        page_no += 1
    
    keyword = '주요사항보고서(자기주식취득결정)'
    # 법인 Y(코스피), K(코스닥) // (거래정지, 비상장 회사 제외)
    summary_results = results_all.loc[(results_all['report_nm'] == keyword) & ((results_all['corp_cls'] == 'K') | (results_all['corp_cls'] == 'Y'))]
    # rcept_no를 index로 변경
    return summary_results.set_index('rcept_no')
    
    
# 주말일 경우 금요일 데이터 받아오게 처리
def get_date():
    today = datetime.today()
    if(today.weekday() == 5):
        return (today - timedelta(1)).strftime("%Y%m%d")
    if(today.weekday() == 6):
        return (today - timedelta(2)).strftime("%Y%m%d")

def get_treasury_stock_details(treasury_stock_summary):
    if len(treasury_stock_summary) == 0:
        print("자기주식취득결정 공시가 존재하지 않습니다.")
        return None
    
    details_results_all = pd.DataFrame()
    company_list = [] # 회사별 중복 실행 방지
    
    for _, row in treasury_stock_summary.iterrows():
        corp_code = row['corp_code']
        bgn_de = row['rcept_dt']
        end_de = row['rcept_dt']

        if corp_code in company_list:
            continue
        company_list.append(corp_code)

        url = 'https://opendart.fss.or.kr/api/tsstkAqDecsn.json'
        params = {
            'crtfc_key': DART_API_KEY,
            'corp_code': corp_code,
            'bgn_de': bgn_de,
            'end_de': end_de
        }

        try:
            details_results = requests.get(url, params = params, timeout = DEFAULT_TIMEOUT).json()
        except requests.exceptions.HTTPError as e:
            print("GET - Http Error occurred ", e)
        except requests.exceptions.Timeout as e:
            print("GET - Timeout error occurred ", e)
        except requests.exceptions.RequestException as e:
            print("GET - Error occurred ", e)

        details_results_df = pd.DataFrame(details_results['list'])
        details_results_all = pd.concat([details_results_all, details_results_df])
    """
    추출이 필요한 데이터 열 종류 선택
    - recept_no: 리포트 넘버
    - aqpln_prc_ostk: 취득예정 금액
    - aq_pp: 취득 목적
    - aq_mth: 취득 방식
    - aqexpd_bgd: 시작일
    - aqexpd_edd: 종료일
    """
    filtered_details = details_results_all[['rcept_no', 'aqpln_prc_ostk', 'aq_pp', 'aq_mth', 'aqexpd_bgd', 'aqexpd_edd']]
    return filtered_details.set_index('rcept_no')

treasury_stock_summary = get_treasury_stock_summary()
treasury_stock_details = get_treasury_stock_details(treasury_stock_summary)
# axis = 1은 데이터 좌우로 병합, join = 'inner'은 교집합 병합 <-> 'outer'는 합집합 병합
treasury_stock_total_data = pd.concat([treasury_stock_summary, treasury_stock_details], axis = 1, join = 'inner') if len(treasury_stock_summary) else None
# 엑셀 추출 필요할 경우 사용
# treasury_stock_data.to_excel("/Users/dean/Desktop/programming/tele-stock/src/자기주식데이터.xlsx")