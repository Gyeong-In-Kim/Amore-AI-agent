import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"🔑 API Key 확인: {api_key[:5]}... (로드 성공)")

print("\n📋 사용 가능한 모델 리스트:")
try:
    # 내 키로 쓸 수 있는 모델을 싹 다 조회함
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
except Exception as e:
    print(f"🚨 에러 발생: {e}")