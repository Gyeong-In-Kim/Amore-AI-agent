import os
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 설정
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def generate_marketing_copy(product_info, user_query):
    """
    제품 정보(Dict)와 사용자 고민(String)을 받아서
    세일즈 카피(String)를 생성하는 함수
    """
    
    # ★ 수정된 부분: 모델 이름을 최신으로 변경 (gemini-pro -> gemini-1.5-flash)
    model = genai.GenerativeModel('gemini-flash-latest')

    # 프롬프트 설계
    prompt = f"""
    당신은 10년 차 베테랑 뷰티 카피라이터입니다.
    아래 고객의 고민을 해결해줄 제품을 추천하는 짧고 강렬한 메시지(SMS/카톡용)를 작성해주세요.

    [고객 고민]
    "{user_query}"

    [추천 제품 정보]
    - 제품명: {product_info['name']}
    - 가격: {product_info['price']}원
    - 특징: {product_info['skin_type']} 피부용, {product_info['concern']} 해결

    [요청사항]
    1. 고객의 고민에 공감하며 시작하세요.
    2. 왜 이 제품이 답인지 핵심 성분이나 특징을 연결해서 설명하세요.
    3. 이모지를 적절히 사용하여 읽기 편하게 만드세요.
    4. 300자 이내로 작성하세요.
    """

    # AI에게 생성을 요청
    response = model.generate_content(prompt)
    return response.text