import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
API_KEY = os.getenv("DATA_GO_KR_API_KEY")

def check_raw_response():
    # 주소와 키 조립
    encoded_key = quote(API_KEY)
    url = f"http://apis.data.go.kr/1471000/FtnltCosmRptPrdlstInfoService/getRptPrdlstInq?serviceKey={encoded_key}&pageNo=1&numOfRows=1&type=json&entp_name=아모레퍼시픽"
    
    print("🔍 API 원본 응답을 조회합니다...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        items = data['body']['items']
        if items:
            print("\n📦 [첫 번째 아이템의 모든 데이터 필드]")
            print("--------------------------------------------------")
            item = items[0]
            for key, value in item.items():
                print(f"키: {key} \t 값: {value}")
            print("--------------------------------------------------")
            print("위 목록에서 '성분'이나 '효능'과 관련된 영어 키(Key) 이름을 찾아보세요!")
        else:
            print("데이터가 없습니다.")
    else:
        print("API 호출 실패:", response.status_code)

if __name__ == "__main__":
    check_raw_response()