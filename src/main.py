from vector_db import init_db, search_best_product
from generator import generate_marketing_copy

def run_agent(user_query):
    print(f"\n💬 [User]: {user_query}")
    print("--------------------------------------------------")
    
    # 1. DB 초기화 (데이터 로드)
    init_db()
    
    # 2. 검색 (Retrieve) - RAG의 R
    print("🔍 고객님에게 딱 맞는 제품을 찾는 중...")
    best_product = search_best_product(user_query)
    
    if not best_product:
        print("❌ 적절한 제품을 찾지 못했습니다.")
        return

    print(f"✅ 찾은 제품: {best_product['name']}")
    
    # 3. 생성 (Generate) - RAG의 G
    print("✍️ 마케팅 메시지 작성 중...")
    copy_text = generate_marketing_copy(best_product, user_query)
    
    # 4. 결과 출력
    print("\n[📩 생성된 메시지]")
    print("==================================================")
    print(copy_text)
    print("==================================================")

if __name__ == "__main__":
    # 테스트하고 싶은 가상의 고객 질문
    test_query = "요즘 얼굴이 너무 건조하고 화장이 떠요."
    
    run_agent(test_query)