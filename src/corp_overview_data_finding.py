import requests

from private_data import DART_API_KEY

def load_data(**kwargs):
    crtfc_key = DART_API_KEY
    corp_code = kwargs['corp_code']

    # 기업개황 요청 url
    url = 'https://opendart.fss.or.kr/api/company.json?crtfc_key='+crtfc_key+'&corp_code='+corp_code

    # HTTP 요청
    return requests.get(url, timeout=5).json()
    
print(load_data(request='company', corp_code='00126380'))