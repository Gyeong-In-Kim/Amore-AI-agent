import streamlit as st
import os
from vector_db import init_db, search_best_product
from generator import generate_marketing_copy
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

# 2. 페이지 기본 설정 (탭 이름, 아이콘 등)
st.set_page_config(
    page_title="아모레 AI 마케터",
    page_icon="💄",
    layout="centered"
)

# 3. 제목과 설명
st.title("✨ Amore AI Marketing Agent")
st.markdown("### 당신의 피부 고민을 이야기해주세요. AI가 해결책을 제시합니다.")

# 4. 사이드바 (옵션)
with st.sidebar:
    st.header("About")
    st.write("이 에이전트는 RAG 기술을 사용하여 아모레퍼시픽 제품을 추천하고 마케팅 카피를 작성합니다.")
    st.info("💡 Tip: 구체적인 상황을 입력하면 더 좋은 결과가 나옵니다.")

# 5. 사용자 입력 받기
query = st.text_area("고민 입력", placeholder="예: 요즘 야근 때문에 피부가 칙칙하고 탄력이 없어서 고민이야. 30대 직장인 여성에게 맞는 제품 추천해줘.")

# 6. 버튼 클릭 시 실행 로직
if st.button("🚀 솔루션 분석 시작"):
    if not query:
        st.warning("내용을 입력해주세요!")
    else:
        # 로딩 애니메이션
        with st.spinner("🔍 제품 데이터베이스 검색 중..."):
            # DB 초기화 및 검색 (캐싱을 위해 함수로 분리하면 더 좋지만 일단 직관적으로 작성)
            collection = init_db() 
            best_product = search_best_product(query)
        
        if best_product:
            # 검색 결과 표시
            st.success(f"추천 제품을 찾았습니다! : {best_product['name']}")
            
            # 제품 카드 보여주기
            with st.expander("📦 제품 상세 정보 확인", expanded=True):
                st.markdown(f"**제품명:** {best_product['name']}")
                st.markdown(f"**특징:** {best_product['description']}")
                # 가격 정보가 있다면 여기에 추가
                # st.markdown(f"**가격:** {best_product['price']}")

            # 카피라이팅 생성
            with st.spinner("✍️ 마케팅 카피 작성 중... (Gemini 생각 중)"):
                copy_text = generate_marketing_copy(best_product, query)
            
            st.markdown("---")
            st.subheader("💌 AI가 작성한 마케팅 메시지")
            st.info(copy_text)
            
        else:
            st.error("적절한 제품을 찾지 못했습니다. 질문을 다르게 해보세요.")