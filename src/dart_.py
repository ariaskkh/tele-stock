import dart_fss as dart
from private_data import DART_API_KEY

# Open DART API KEY 설정
api_key=DART_API_KEY
dart.set_api_key(api_key=api_key)

# DART 에 공시된 회사 리스트 불러오기
corp_list = dart.corp.CorpList()
