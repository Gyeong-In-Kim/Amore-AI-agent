import pandas as pd
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 1. 설정 로드
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 파일 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'products_new.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'products_final.csv')

def enrich_product_data():
    if not os.path.exists(INPUT_PATH):
        print("❌ products_new.csv 파일이 없습니다. 먼저 수집부터 해주세요!")
        return

    df = pd.read_csv(INPUT_PATH)
    print(f"📋 총 {len(df)}개의 제품 정보를 보완합니다...")
    
    enriched_data = []

    # 모델 설정 (가볍고 빠른 모델 추천)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    for index, row in df.iterrows():
        product_name = row['product_name']
        print(f"[{index+1}/{len(df)}] 분석 중: {product_name}")
        
        # 2. Gemini에게 물어보기
        prompt = f"""
        제품명: '{product_name}' (브랜드: 아모레퍼시픽)
        
        이 화장품에 대해 다음 정보를 JSON 형식으로 추론해서 알려줘.
        모르면 일반적인 해당 카테고리 제품의 특성을 적어.
        
        1. features: 주요 성분 2~3가지를 포함한 특징 (한 줄 요약)
        2. skin_type: 추천 피부 타입 (예: 건성, 지성, 트러블성, 모든피부)
        3. functionality: 기능성 여부 (예: 주름개선, 미백, 자외선차단, 수분보습)
        4. price: 예상 소비자 가격 (숫자만, 모르면 30000)
        
        출력 형식:
        {{"features": "...", "skin_type": "...", "functionality": "...", "price": 0000}}
        """
        
        try:
            response = model.generate_content(prompt)
            result = response.text.strip().replace('```json', '').replace('```', '')
            import json
            ai_data = json.loads(result)
            
            # 기존 데이터에 AI가 만든 정보 덮어쓰기
            row['features'] = ai_data.get('features', row['features'])
            row['skin_type'] = ai_data.get('skin_type', row['skin_type'])
            row['category'] = ai_data.get('functionality', row['category']) # 기능성 정보로 대체
            row['price'] = ai_data.get('price', row['price'])
            
        except Exception as e:
            print(f"⚠️ AI 분석 실패 (그냥 넘어감): {e}")
        
        enriched_data.append(row)
        time.sleep(1) # API 과부하 방지

    # 3. 저장
    final_df = pd.DataFrame(enriched_data)
    final_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n🎉 데이터 보완 완료! '{OUTPUT_PATH}' 파일을 확인해보세요.")

if __name__ == "__main__":
    enrich_product_data()