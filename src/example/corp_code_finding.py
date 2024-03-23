import sys
sys.path.append('/Users/dean/Desktop/programming/tele-stock/src')

from private_data import DART_API_KEY
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET





url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={DART_API_KEY}"

# url을 통해 기업 고유 번호 받아옴. zip -> xml 형태로 저장
with urlopen(url) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall('corp_num')

# 압축파일 안에 xml 파일 읽기
tree = ET.parse('../corp_code/CORPCODE.xml')
root = tree.getroot()

# 회사 이름으로 회사 고유 번호 찾기
def find_corp_num(find_name):
    for country in root.iter("list"):
        if country.findtext("corp_name") == find_name:
            return country.findtext("corp_code")
        
print(find_corp_num('삼성전자'))