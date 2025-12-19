import os
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# [설정 영역] 친구들이 여기서 원하는 AI를 선택하세요!
# --------------------------------------------------------------------------
# 사용하고 싶은 AI 서비스의 이름을 아래 변수에 적어주세요.
# 가능한 옵션: 'gemini', 'groq', 'openai'
CURRENT_AI_PROVIDER = 'gemini' 

# 모델 설정
MODEL_CONFIG = {
    # 2025년 기준 가장 빠르고 무료 쿼터가 넉넉한 모델 (필수!)
    'gemini': 'gemini-2.5-flash-lite',     
    'groq': 'llama-3.3-70b-versatile',
    'openai': 'gpt-4o-mini'
}
# --------------------------------------------------------------------------

load_dotenv()

def get_prompt(product_info, user_context):
    """모든 AI에게 공통으로 보낼 질문(프롬프트)을 만드는 함수"""
    # product_info가 비어있을 경우를 대비해 안전하게 처리
    if not product_info:
        product_info = {}

    return f"""
    당신은 10년 차 베테랑 뷰티 카피라이터입니다.
    아래 고객 정보를 바탕으로 제품을 추천하는 짧고 매력적인 메시지(카카오톡/SMS용)를 작성해주세요.

    [고객 정보]
    {user_context}

    [추천 제품 정보]
    - 제품명: {product_info.get('name', '제품명 없음')}
    - 가격: {product_info.get('price', '가격 미정')}원
    - 특징: {product_info.get('skin_type', '')} 추천
    
    (참고: 제품 데이터에 더 자세한 특징이나 리뷰가 있다면 반영해주세요)

    [요청사항]
    1. 고객의 이름과 고민을 언급하며 공감해주세요.
    2. 제품의 특징이 왜 고객에게 필요한지 자연스럽게 연결하세요.
    3. 따뜻하고 전문적인 톤앤매너를 유지하세요.
    4. 이모지를 적절히 사용하고, 300자 이내로 작성하세요.
    5. 한국어로 작성하세요.
    """

def generate_marketing_copy(product_info, user_context):
    """설정된 AI 제공자에 따라 마케팅 카피를 생성하는 메인 함수"""
    # 프롬프트 생성 (여기서 에러가 나면 product_info 데이터를 확인해야 함)
    prompt = get_prompt(product_info, user_context)
    
    try:
        # 설정된 AI에 따라 함수 호출
        if CURRENT_AI_PROVIDER == 'gemini':
            return _use_gemini(prompt)
        elif CURRENT_AI_PROVIDER == 'groq':
            return _use_groq(prompt)
        elif CURRENT_AI_PROVIDER == 'openai':
            return _use_openai(prompt)
        else:
            return "🚨 오류: CURRENT_AI_PROVIDER 설정을 확인해주세요!"
            
    except Exception as e:
        # 에러 발생 시 상세 내용을 출력해서 원인을 찾기 쉽게 함
        return f"죄송합니다. 메시지 생성 중 오류가 발생했습니다 ({CURRENT_AI_PROVIDER}): {str(e)}"

# ==========================================================================
# 아래는 각 AI 서비스별 연결 함수들입니다. (내부적으로 사용됨)
# ==========================================================================

def _use_gemini(prompt):
    """Google Gemini 사용"""
    import google.generativeai as genai
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "🚨 에러: .env 파일에 GOOGLE_API_KEY가 없습니다."
        
    genai.configure(api_key=api_key)
    
    # 모델 불러오기
    try:
        model = genai.GenerativeModel(MODEL_CONFIG['gemini'])
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 호출 오류: {e}"

def _use_groq(prompt):
    """Groq (Llama3) 사용"""
    try:
        from groq import Groq
    except ImportError:
        return "🚨 에러: groq 라이브러리가 설치되지 않았습니다. (pip install groq)"
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "🚨 에러: .env 파일에 GROQ_API_KEY가 없습니다."

    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "당신은 도움이 되는 뷰티 마케터입니다."},
            {"role": "user", "content": prompt}
        ],
        model=MODEL_CONFIG['groq'],
        temperature=0.7,
    )
    return chat_completion.choices[0].message.content

def _use_openai(prompt):
    """OpenAI (GPT) 사용"""
    try:
        from openai import OpenAI
    except ImportError:
        return "🚨 에러: openai 라이브러리가 설치되지 않았습니다. (pip install openai)"
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "🚨 에러: .env 파일에 OPENAI_API_KEY가 없습니다."

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL_CONFIG['openai'],
        messages=[
            {"role": "system", "content": "당신은 도움이 되는 뷰티 마케터입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content