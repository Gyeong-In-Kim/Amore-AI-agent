import os
from groq import Groq
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Groq 클라이언트 설정
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def generate_marketing_copy(product_info, user_context):
    """
    Groq(Llama3)를 사용해 마케팅 카피를 생성하는 함수
    """
    
    # 프롬프트 설계
    prompt = f"""
    당신은 10년 차 베테랑 뷰티 카피라이터입니다.
    아래 고객 정보를 바탕으로 제품을 추천하는 짧고 매력적인 메시지(카카오톡/SMS용)를 작성해주세요.

    [고객 정보]
    {user_context}

    [추천 제품 정보]
    - 제품명: {product_info['name']}
    - 가격: {product_info['price']}원
    - 특징: {product_info['skin_type']} 피부용, {product_info['concern']} 해결

    [요청사항]
    1. 고객의 이름과 고민을 언급하며 공감해주세요.
    2. 제품의 특징이 왜 고객에게 필요한지 자연스럽게 연결하세요.
    3. 따뜻하고 전문적인 톤앤매너를 유지하세요.
    4. 이모지를 적절히 사용하고, 300자 이내로 작성하세요.
    5. 한국어로 작성하세요.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "당신은 도움이 되는 뷰티 마케팅 어시스턴트입니다."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            # Llama-3-8b 모델 (가볍고 빠르고 한국어 잘함)
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"죄송합니다. 메시지 생성 중 오류가 발생했습니다: {str(e)}"