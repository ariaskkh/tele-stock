from datetime import datetime, timedelta
import pandas as pd
import requests

from private_data import DART_API_KEY

class TreasuryStock:
    DEFAULT_TIMEOUT = 5000
    NO_DATA_STATUS = '013'
    REQEUST_SUCCESS_MESSAGE = '정상'

    def __init__(self):
        self.overview_data = self.__get_stock_overview()
        if(self.overview_data is None or not len(self.overview_data)):
            self.total_data =  None
            return
        self.detail_data = self.__get_stock_details(self.overview_data)
        self.total_data = pd.concat([self.overview_data, self.detail_data], axis = 1, join = 'inner')

    def get_stock_data(self):
        if(self.total_data ==0):
            return None
        return self.total_data
    
    def get_stock_tele_messages(self):
        return self.__get_tele_message_form()
        
    def __get_stock_overview(self):
        page_no = 1 # 페이지 번호
        page_count = 100 # 페이지 별 건수
        start_date = self.__get_date() # 검색 시작일
        end_date = self.__get_date() # 검색 종료일
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
                results = requests.get(url, params=params, timeout = self.DEFAULT_TIMEOUT).json()
            except requests.exceptions.HTTPError as e:
                print("GET - Http Error occurred ", e)
            except requests.exceptions.Timeout as e:
                print("GET - Timeout error occurred ", e)
            except requests.exceptions.RequestException as e: # 모든 exception의 기본 class
                print("GET - Error occurred ", e)

            if(results['status'] == self.NO_DATA_STATUS):
                print("해당 기간에 자기주식취득결정 공시가 존재하지 않습니다.")
                return None
            if(results['message'] != self.REQEUST_SUCCESS_MESSAGE):
                print("비정상적 데이터를 받았습니다. 전달 인자 등을 확인하세요", results['message'])
                return None

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
    
    def __get_date(self):
        today = datetime.today()
        if(today.weekday() == 5):
            today -= timedelta(1)
        if(today.weekday() == 6):
            today -= timedelta(2)
        return today.strftime("%Y%m%d")
        
        
    def __get_stock_details(self, treasury_stock_summary):
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
                details_results = requests.get(url, params = params, timeout = self.DEFAULT_TIMEOUT).json()
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
    
    """ [텔레 노출 form ex]
    휠라홀딩스(081660)
    자식주식 <취득> 결정(신탁)

    금액(원): 100 억
    유동시총대비(%): 0.66 // 아직 없음
    취득목적: 주식가격의 안정을 통한 주주가치 제고
    시작일 : 2024-03-21
    종료일 : 2024-09-20
    http:~~~
    """
    def __get_tele_message_form(self):
        if (self.total_data is None):
            print("메세지가 없습니다")
            return None
        result = []
        for index, stock in self.total_data.iterrows():
            result_str = ""
            corp_name = stock['corp_name']
            stock_code = stock['stock_code']
            report_name = stock['report_nm']
            expected_achieve_money = int(int(stock['aqpln_prc_ostk'].replace(',', '')) / 100000000)
            acquisition_purpose = stock['aq_pp']
            acquisition_method = stock['aq_mth']
            start_date = stock['aqexpd_bgd']
            end_date = stock['aqexpd_edd']
            report_number = index

            # 텔레 노출 form
            result_str += f"{corp_name}({stock_code})\n"
            result_str += f"{report_name}\n\n"
            result_str += f"금액(원)): {expected_achieve_money} 억\n"
            result_str += f"취득목적: {acquisition_purpose}\n"
            result_str += f"취득방법: {acquisition_method}\n"
            result_str += f"시작일: {start_date}\n"
            result_str += f"종료일: {end_date}\n"
            result_str += f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={report_number}\n"
            result.append(result_str)
        return result
