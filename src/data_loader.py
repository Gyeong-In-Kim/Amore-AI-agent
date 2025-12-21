import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'products.csv')

def load_product_data():
    print(f"📂 데이터 로딩 중... 경로: {DATA_PATH}")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ 파일이 없습니다: {DATA_PATH}")
        return []

    try:
        # 🔥 핵심 수정: 문제 있는 줄(쉼표 개수 안 맞는 줄)은 쿨하게 건너뛰기!
        df = pd.read_csv(DATA_PATH, on_bad_lines='skip') 
        print(f"✅ 총 {len(df)}개의 제품 데이터를 정상적으로 불러왔습니다.")
        
        products = []
        for _, row in df.iterrows():
            # 검색에 쓰일 텍스트
            search_text = f"[{row['brand']}] {row['product_name']} \n특징: {row['features']} \n리뷰: {row['reviews']} \n추천타입: {row['skin_type']}"
            
            product_info = {
                "search_text": search_text,
                "metadata": {
                    "brand": row['brand'],
                    "name": row['product_name'],
                    "price": row['price'],
                    "skin_type": row['skin_type'],
                    "description": row['features']
                }
            }
            products.append(product_info)
            
        return products

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

if __name__ == "__main__":
    load_product_data()