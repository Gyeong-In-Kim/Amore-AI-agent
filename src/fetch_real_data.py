import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
from urllib.parse import quote  # 👈 핵심: 주소창처럼 만들어주는 도구

# 1. 환경변수 로드
load_dotenv()

# .env 파일에서 키 가져오기 (Decoding Key)
API_KEY = os.getenv("DATA_GO_KR_API_KEY")

if not API_KEY:
    print("🚨 에러: .env 파일에서 'DATA_GO_KR_API_KEY'를 찾을 수 없습니다.")
    exit()

def fetch_amore_products(page_limit=3):
    """
    아모레퍼시픽 화장품 데이터를 API에서 가져오는 함수
    (해결책: params를 쓰지 않고 URL을 직접 조립해서 보냅니다)
    """
    base_url = "http://apis.data.go.kr/1471000/FtnltCosmRptPrdlstInfoService/getRptPrdlstInq"
    
    all_products = []
    
    print(f"🚀 아모레퍼시픽 제품 데이터 수집을 시작합니다... (키 확인: {API_KEY[:5]}***)")

    for page in range(1, page_limit + 1):
        # -----------------------------------------------------------
        # [핵심 변경점] 브라우저 주소창 입력하듯이 URL을 직접 만듭니다.
        # requests가 키를 멋대로 변형하지 못하게 하기 위함입니다.
        # -----------------------------------------------------------
        encoded_key = quote(API_KEY) # 키를 인터넷용으로 변환
        query_params = f"&pageNo={page}&numOfRows=20&type=json&entp_name=아모레퍼시픽"
        full_url = f"{base_url}?serviceKey={encoded_key}{query_params}"

        try:
            # params=... 옵션을 뺐습니다. 이미 full_url에 다 들어있으니까요!
            response = requests.get(full_url)
            
            if response.status_code != 200:
                print(f"❌ 접속 실패 (Page {page}): {response.status_code}")
                continue

            try:
                data = response.json()
            except ValueError:
                print(f"⚠️ JSON 변환 실패. 응답 내용: {response.text[:100]}")
                break

            # 데이터 구조 체크
            if 'body' not in data or 'items' not in data['body']:
                 # 데이터가 없거나 구조가 다른 경우
                 if 'header' in data and data['header']['resultCode'] == '00':
                     print(f"👋 데이터 수집 끝! (Page {page} - 데이터 없음)")
                 else:
                     print(f"👋 응답은 받았으나 데이터가 없습니다. (Page {page})")
                 break

            items = data['body']['items']
            if not items:
                print(f"👋 더 이상 데이터가 없습니다. (Page {page})")
                break

            print(f"✅ {page}페이지 수집 성공! ({len(items)}개 발견)")

            for item in items:
                product = {
                    "brand": "아모레퍼시픽", 
                    "product_name": item.get("ITEM_NAME"), 
                    "features": item.get("MAIN_ITEM_INGR", "성분 정보 없음"),
                    "reviews": "AI 가상 리뷰", 
                    "skin_type": "모든피부", # 추후 AI로 채울 예정
                    "price": "35000",      # 추후 AI로 채울 예정
                    "category": "기능성 화장품"
                }
                all_products.append(product)
            
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
            break
    
    return pd.DataFrame(all_products)

if __name__ == "__main__":
    df = fetch_amore_products(page_limit=5)
    
    if not df.empty:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        save_path = os.path.join(project_root, 'data', 'products_new.csv')
        
        # 폴더 없으면 생성
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"\n🎉 대성공! 총 {len(df)}개의 진짜 데이터를 가져왔습니다.")
        print(f"📂 저장된 위치: {save_path}")
    else:
        print("\n❌ 데이터를 가져오지 못했습니다.")