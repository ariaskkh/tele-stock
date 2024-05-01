from datetime import datetime, timedelta
import pandas as pd
import requests
import os

from private_data import DART_API_KEY
from enum import Enum

class BusinessReportKind(Enum):
    FIRST_QUARTER = "11013" # 분기보고서
    SECOND_QUARTER = "11012" # 반기보고서
    THIRD_QUARTER = "11014" # 분기보고서
    FOURTH_QUARTER = "11011" # 사업보고서

class ResponseStatus(Enum):
    SUCCESS = '000'
    FAIL_NO_DATA = '013'

class TreasuryStock:
    DEFAULT_TIMEOUT = 5000
    file_name = '자기주식데이터.xlsx'

    def __init__(self):
        self.__get_data()
        self.__save_data()

    def get_stock_data(self):
        if(self.total_data ==0):
            return None
        return self.total_data
    
    def get_stock_tele_messages(self) -> list:
        return self.__get_tele_message_form()
    
    def __get_data(self):
        self.overview_data = self.__get_stock_overview()
        if(self.overview_data is None or not len(self.overview_data)):
            self.total_data =  None
            print("해당 조건의 공시 데이터가 존재하지 않습니다.")
            return
        self.detail_data = self.__get_stock_details(self.overview_data)
        # axis = 1 좌우 합치기, = 0 위아래 합치기 // inner = 교집합, outer = 합집합
        self.total_data = pd.concat([self.overview_data, self.detail_data], axis = 1, join = 'inner')
        self.floating_stock_data = self.__get_floating_stock_rate(self.overview_data)
        self.__add_floating_stock_rate()

    def __get_stock_overview(self):
        page_no = 1 # 페이지 번호
        page_count = 100 # 페이지 별 건수
        start_date = self.__get_date() # 검색 시작일
        # start_date = 20240427
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

            if(results['status'] == ResponseStatus.FAIL_NO_DATA.value):
                print("해당 기간에 공시가 존재하지 않습니다.")
                return None
            elif(results['status'] != ResponseStatus.SUCCESS.value):
                print("비정상적 데이터를 받았습니다. 전달 인자 등을 확인하세요. message: ", results['message'])
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
        new_summary_results = self.__filter_saved_data(summary_results.set_index('rcept_no'))
        return new_summary_results
    
    def __get_date(self):
        today = datetime.today()
        if(today.weekday() == 5):
            return (today - timedelta(1)).strftime("%Y%m%d")
        if(today.weekday() == 6):
            return (today - timedelta(2)).strftime("%Y%m%d")
        return today.strftime("%Y%m%d")
        
        
    def __get_stock_details(self, overview_data: pd.DataFrame) -> pd.DataFrame:
        if len(overview_data) == 0:
            print("자기주식취득결정 공시가 존재하지 않습니다.")
            return None
    
        details_results_all = pd.DataFrame()
        company_list = [] # 회사별 중복 실행 방지
    
        for _, row in overview_data.iterrows():
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

            details_results = pd.DataFrame(details_results['list'])
            self.__check_corrected_data(overview_data, row.name, details_results.loc[0, 'rcept_no'])
            details_results_all = pd.concat([details_results_all, details_results])
        """
        추출이 필요한 데이터 열 종류 선택
        - recept_no: 접수 번호
        - aqpln_stk_ostk: 취득예정 주식 수(보통주식)
        - aqpln_stk_estk: 취득예정 주식 수(기타주식)
        - aqpln_prc_ostk: 취득예정 금액(보통주식)
        - aqpln_prc_estk: 취득예정 금액(기타주식)
        - aq_pp: 취득 목적
        - aq_mth: 취득 방식
        - aqexpd_bgd: 시작일
        - aqexpd_edd: 종료일
        """
        filtered_details = details_results_all[['rcept_no', 'aqpln_stk_ostk', 'aqpln_prc_ostk', 'aqpln_stk_estk', 'aqpln_prc_estk', 'aq_pp', 'aq_mth', 'aqexpd_bgd', 'aqexpd_edd']]
        return filtered_details.set_index('rcept_no')
    
    def __add_floating_stock_rate(self):
        total_data = self.total_data.reset_index()
        total_data['acquisition_stock_rate_of_floating'] = None # column 추가
        for _, total_data_of_company in total_data.iterrows():
            for _, floating_data_of_company in self.floating_stock_data.iterrows():
                if total_data_of_company['corp_code'] == floating_data_of_company['corp_code']:
                    # 유동주식 비율 구해야 함 = 취득 주식 수  / 유통주식 수
                    acquisition_stock_number = 0
                    if total_data_of_company['aqpln_stk_ostk'] == '-':
                        acquisition_stock_number = total_data_of_company['aqpln_stk_estk'] # 기타주식
                    else:
                        acquisition_stock_number = total_data_of_company['aqpln_stk_ostk'] # 보통주식
                    acquisition_stock_number = int(acquisition_stock_number.replace(',',''))
                    floating_stock_number = int(floating_data_of_company['hold_stock_co'].replace(',',''))
                    acquisition_stock_rate_of_floating = round(acquisition_stock_number / floating_stock_number * 100, 2)
                    total_data.loc[total_data['corp_code'] == floating_data_of_company['corp_code'], 'acquisition_stock_rate_of_floating'] = acquisition_stock_rate_of_floating
        self.total_data = total_data.set_index('rcept_no')
    
    """ [텔레 노출 form ex]
    휠라홀딩스(081660)
    자식주식 <취득> 결정(신탁)

    금액(원): 100 억
    유동주식대비(소액주주 기준): 0.66 %
    취득방법: 유가증권시장을 통한 장내 매수
    취득목적: 주식가격의 안정을 통한 주주가치 제고
    시작일 : 2024-03-21
    종료일 : 2024-09-20
    http://dart.fss.or.kr/dsaf001/main.do?rcpNo=report_number
    """
    def __get_tele_message_form(self) -> list:
        if (self.total_data is None):
            print("메세지가 없습니다")
            return None
        result = []
        for index, stock in self.total_data.iterrows():
            result_str = ""
            corp_name = stock['corp_name']
            stock_code = stock['stock_code']
            report_name = stock['report_nm']
            if stock['aqpln_prc_ostk'] != '-': # 보통주식
                expected_achieve_money = round(int(stock['aqpln_prc_ostk'].replace(',', '')) / 100000000)
            elif (stock['aqpln_prc_estk'] != '-'): # 기타주식
                expected_achieve_money = round(int(stock['aqpln_prc_estk'].replace(',', '')) / 100000000)
            else:
                expected_achieve_money = '-'
            acquisition_stock_rate_of_floating = stock['acquisition_stock_rate_of_floating']
            acquisition_method = stock['aq_mth']
            acquisition_purpose = stock['aq_pp']
            start_date = stock['aqexpd_bgd']
            end_date = stock['aqexpd_edd']
            report_number = index

            # 텔레 노출 form
            result_str += f"{corp_name}({stock_code})\n"
            result_str += f"{report_name}\n\n"
            # TODO: 금액 없는 경우 주식 수로 보여주기
            if (stock['aqpln_prc_ostk'] != '-'):
                result_str += f"금액(원)): {expected_achieve_money} 억 (보통주식)\n"
            elif (stock['aqpln_prc_estk'] != '-'):
                result_str += f"금액(원)): {expected_achieve_money} 억 (기타주식)\n"
            else:
                result_str += f"금액(원)): - (공시 미기재)\n"
            result_str += f"유동주식수대비(소액주주 기준): {acquisition_stock_rate_of_floating} %\n"
            result_str += f"취득방법: {acquisition_method}\n"
            result_str += f"취득목적: {acquisition_purpose}\n"
            result_str += f"시작일: {start_date}\n"
            result_str += f"종료일: {end_date}\n"
            result_str += f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={report_number}\n"
            result.append(result_str)
        return result

    def __save_data(self):
        if (self.total_data is None):
            print("저장할 데이터가 존재하지 않습니다.")
            return
        # 파일이 존재하지 않을 때
        if not os.path.exists(self.file_name):
            print(f"'{self.file_name}' 파일이 존재하지 않습니다.")
            self.total_data.to_excel(f"/Users/dean/Desktop/programming/tele-stock/src/{self.file_name}")
            return
        # 파일이 존재 시
        self.__update_data_at_excel()

    def __update_data_at_excel(self):
        total_data_saved = pd.read_excel(self.file_name).set_index('rcept_no')
        report_number_array_saved = total_data_saved.index.values
        for new_report_number in self.total_data.index:
            # 파일에 새로 받은 데이터가 존재할 때
            if int(new_report_number) in report_number_array_saved:
                # message로 보여줄 total_data에서 데이터 제거
                self.total_data = self.total_data.drop([new_report_number])
                continue
            # 파일에 새로 받은 데이터가 존재하지 않을 때 total_data_saved에 데이터 추가
            new_report_data = self.total_data.loc[new_report_number]
            total_data_saved.loc[new_report_number] = new_report_data
        # 엑셀로 저장
        if (self.total_data.empty):
            print("이미 저장된 데이터입니다.")
            return
        total_data_saved.to_excel(f"/Users/dean/Desktop/programming/tele-stock/src/{self.file_name}")

    # TODO: 위 로직과 중복 로직 합칠 수 있는지 확인..
    def __filter_saved_data(self, overview_data_received: pd.DataFrame):
        if os.path.exists(self.file_name):
            total_data_saved = pd.read_excel(self.file_name).set_index('rcept_no')
            report_number_array_saved = total_data_saved.index.values
            for new_report_number in overview_data_received.index.values:
                if new_report_number in report_number_array_saved:
                    overview_data_received = overview_data_received.drop([new_report_number])
            return overview_data_received
        return overview_data_received
    
    # 정정 공시의 경우 처음 받은 overview_recept_number와 이어 받은 detail_recept_number가 달라 예외처리. 정정된 값인 detail_recept_number로 같게 만듦.
    # 정정 시 최초 한 번만 실행됨
    def __check_corrected_data(self, overview_data: pd.DataFrame, overview_recept_number, detail_recept_number) -> pd.DataFrame:
        if(overview_recept_number != detail_recept_number):
            overview_data = overview_data.reset_index()
            index_to_change = overview_data.index[overview_data['rcept_no'] == overview_recept_number].tolist()[0]
            overview_data.at[index_to_change, 'rcept_no'] = detail_recept_number
            # 바뀐 데이터 할당
            self.overview_data = overview_data.set_index('rcept_no')

    def __get_floating_stock_rate(self, overview_data: pd.DataFrame):
        latest_report_code_list = self.__get_latest_report_code()
        isSettlementMonth: bool = len(latest_report_code_list) >= 2 # 결산월 3,6,9,12월에 2개 보고서 확인
        floating_stock_data_all = pd.DataFrame()
        
        for _, company_overview_data in overview_data.iterrows():
            floating_stock_data = self.__fetch_data(company_overview_data, latest_report_code_list[0])
            # 3, 6, 9, 12월 예외처리
            if floating_stock_data["status"] == ResponseStatus.FAIL_NO_DATA.value and isSettlementMonth:
                floating_stock_data = self.__fetch_data(company_overview_data, latest_report_code_list[1])
            
            if floating_stock_data["status"] != ResponseStatus.SUCCESS.value:
                print('소액주주 현황 데이터가 존재하지 않습니다. message:', floating_stock_data["message"])
                return None

            floating_stock_data = pd.DataFrame(floating_stock_data['list'])
            floating_stock_data_all = pd.concat([floating_stock_data_all, floating_stock_data])
        """
        - corp_code: 고유번호
        - corp_name: 법인명
        - se: 구분 (ex. 소액주주)
        - hold_stock_co: 보유 주식 수
        - stock_tot_co: 총발행 주식수
        - hold_stock_rate: 보유 주식 비율
        """
        return floating_stock_data_all[['rcept_no', 'corp_code', 'corp_name', 'se', 'hold_stock_co','hold_stock_rate']]

    def __fetch_data(self, company_overview_data, latest_report_code: BusinessReportKind) -> dict:
        new_floating_stock_data: dict
        url = "https://opendart.fss.or.kr/api/mrhlSttus.json"
        params =  {
            'crtfc_key': DART_API_KEY,
            'corp_code': company_overview_data['corp_code'],
            'bsns_year': self.get_latest_report_business_year(latest_report_code), # 사업 연도
            'reprt_code': latest_report_code.value, # 보고서 코드 
        }
        try:
            new_floating_stock_data = requests.get(url, params = params, timeout = self.DEFAULT_TIMEOUT).json()
        except requests.exceptions.HTTPError as e:
            print("GET - Http Error occurred ", e)
        except requests.exceptions.Timeout as e:
            print("GET - Timeout error occurred ", e)
        except requests.exceptions.RequestException as e:
            print("GET - Error occurred ", e)
        return new_floating_stock_data

    # TODO: 리팩토링
    # 정기 보고서의 종류를 결정하기 위한 함수
    def __get_latest_report_code(self) -> list:
        report_code = []
        month = datetime.now().month
        if month <= 3:
            if month == 3:
                report_code.append(BusinessReportKind.FOURTH_QUARTER)
            report_code.append(BusinessReportKind.THIRD_QUARTER)
        elif month <= 6:
            if month == 6:
                report_code.append(BusinessReportKind.FIRST_QUARTER)
            report_code.append(BusinessReportKind.FOURTH_QUARTER)
        elif month <= 9:
            if month == 9:
                report_code.append(BusinessReportKind.SECOND_QUARTER)
            report_code.append(BusinessReportKind.FIRST_QUARTER)
        else:
            if month == 12:
                report_code.append(BusinessReportKind.THIRD_QUARTER)
            report_code.append(BusinessReportKind.SECOND_QUARTER)
        return report_code
    
    def get_latest_report_business_year(self, report_code) -> int:
        if not isinstance(report_code, BusinessReportKind):
            print("리포트 코드를 확인하세요")
            return -1
        month = datetime.now().month
        if month < 6 or (month == 6 and report_code == BusinessReportKind.FOURTH_QUARTER):
            return datetime.now().year - 1
        else:
            return datetime.now().year