import streamlit as st
import os
import time
from vector_db import init_db, search_best_product
from generator import generate_marketing_copy
from dotenv import load_dotenv

# 1. 환경 변수 및 페이지 설정 (Wide 모드 필수)
load_dotenv()
st.set_page_config(
    page_title="Adore AI Agent",
    page_icon="✨",
    layout="wide",  # 3단 구조를 위해 넓은 화면 사용
    initial_sidebar_state="collapsed" # 사이드바 숨김 (헤더 중심 디자인)
)

# 2. 커스텀 CSS (카드 디자인, 칩 스타일 등)
st.markdown("""
<style>
    /* 전체 폰트 및 배경 조정 */
    .block-container { padding-top: 2rem; }
    
    /* 상단 헤더 스타일 */
    .header-title { font-size: 28px; font-weight: 800; color: #333; }
    .header-subtitle { font-size: 14px; color: #666; }
    
    /* 요약 컨텍스트 바 */
    .context-bar {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        gap: 20px;
        align-items: center;
        border: 1px solid #e0e0e0;
    }
    .context-label { font-weight: bold; color: #555; font-size: 14px; }
    .context-chip {
        background-color: #ffffff;
        padding: 5px 12px;
        border-radius: 15px;
        border: 1px solid #ddd;
        font-size: 13px;
        color: #333;
        font-weight: 600;
    }
    
    /* 메시지 카드 스타일 */
    .message-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .message-card:hover { border-color: #ff4b4b; transform: translateY(-2px); }
    .tag {
        display: inline-block;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 4px;
        background-color: #fff4f4;
        color: #ff4b4b;
        margin-right: 5px;
        margin-bottom: 10px;
    }
    
    /* 버튼 스타일링 */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 상태 관리 (생성된 메시지 저장)
if 'generated_results' not in st.session_state:
    st.session_state['generated_results'] = []

# --- [1️⃣ 최상단 헤더 영역] ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="header-title">✨ Glow Code </div>', unsafe_allow_html=True)
    st.caption("Data-driven Marketing Copilot")
with col_h2:
    # 우측: 프로젝트 선택 및 프로필
    project = st.selectbox("📂 프로젝트/캠페인", ["12월 재구매 캠페인", "신규 가입 웰컴", "장바구니 리마인드"], label_visibility="collapsed")

st.divider()

# --- [UI 레이아웃 구성: 3단 구조] ---
# 왼쪽(전략) : 가운데(생성) : 오른쪽(결과) = 1 : 1.5 : 1.5
col_left, col_center, col_right = st.columns([1, 1.4, 1.6])


# --- [⬅️ 왼쪽: 메시지 전략 선택 패널] ---
with col_left:
    st.subheader("🛠️ 전략 설정")
    
    # 1) 메시지 목적
    st.markdown("**🎯 메시지 목적**")
    purpose = st.radio(
        "목적 선택",
        ["신규 고객 유입", "재구매 유도", "이탈 고객 리마인드"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 2) 고객 상태
    st.markdown("**👥 타겟 고객 상태**")
    status_options = {
        "recent_visit": "최근 7일 내 방문",
        "cart_abandon": "장바구니 이탈",
        "purchased": "최근 구매 완료",
        "inactive": "장기 미접속"
    }
    selected_status = []
    for key, label in status_options.items():
        if st.checkbox(label, key=key):
            selected_status.append(label)
            
    st.markdown("---")

    # 3) 톤 & 스타일
    st.markdown("**🎨 톤 & 매너**")
    tone = st.select_slider(
        "톤 선택",
        options=["친근한", "신뢰감 있는", "긴급한", "감성적인"],
        value="친근한"
    )
    brand_voice = st.checkbox("브랜드 말투 적용 (Adore Tone)", value=True)


# --- [2️⃣ 상단 요약 컨텍스트 바 (헤더 아래, 메인 위)] ---
# *왼쪽 패널의 선택값에 따라 동적으로 변함*
context_summary = f"""
<div class="context-bar">
    <span class="context-label">📌 현재 설정:</span>
    <span class="context-chip">🎯 {purpose}</span>
    <span class="context-chip">👥 {', '.join(selected_status) if selected_status else '타겟 미설정'}</span>
    <span class="context-chip">🎨 {tone}</span>
    <span class="context-chip">📢 문자(SMS)</span>
</div>
"""
# 컨텍스트 바는 전체 너비로 보여주거나, 중앙 컬럼 상단에 배치
# 여기서는 3단 구조 안에 자연스럽게 녹이기 위해 중앙 컬럼 상단에 배치합니다.


# --- [🟦 가운데: 메시지 생성 영역] ---
with col_center:
    st.markdown(context_summary, unsafe_allow_html=True) # 요약 바 배치
    
    st.subheader("⚡ AI 메시지 생성")
    
    # 자동 요약 텍스트 (Read-only 느낌)
    summary_text = f"**'{', '.join(selected_status) if selected_status else '모든'}'** 고객에게 **'{tone}'** 톤으로 **'{purpose}'**를 위한 메시지를 생성합니다."
    st.info(summary_text, icon="🤖")
    
    # 추가 요청 입력
    additional_req = st.text_area(
        "✍️ 추가 요청사항 (옵션)", 
        placeholder="예: 이번 주말 한정 혜택이라는 점을 강조해줘, 이모지 많이 써줘",
        height=100
    )
    
    # 옵션
    c_opt1, c_opt2 = st.columns(2)
    with c_opt1:
        count_opt = st.checkbox("메시지 3개 생성", value=True)
    with c_opt2:
        ab_test_opt = st.checkbox("A/B 테스트용 변형 포함")
    
    st.markdown("###") # 여백
    
    # [생성하기] 버튼
    if st.button("✨ 메시지 생성하기", type="primary", use_container_width=True):
        if not selected_status:
            st.warning("타겟 고객 상태를 최소 하나 이상 선택해주세요!")
        else:
            with st.spinner("🔍 고객 데이터 분석 및 카피 작성 중... (약 5초 소요)"):
                # 1. 검색 쿼리 구성
                search_query = f"{purpose}를 위한 화장품 추천, 타겟: {', '.join(selected_status)}, 톤: {tone}"
                if additional_req:
                    search_query += f", 추가요청: {additional_req}"
                
                # 2. RAG 검색 (기존 모듈 활용)
                # (실제로는 여기서 DB 검색이 돌지만, 데모를 위해 로직 연결)
                collection = init_db()
                best_product = search_best_product(search_query)
                
                # 3. 메시지 생성 (기존 모듈 활용)
                # 여러 개 생성 요청 시 반복 호출
                generated_list = []
                try:
                    # 첫 번째 메시지
                    msg1 = generate_marketing_copy(best_product, f"상황: {search_query}")
                    generated_list.append({"text": msg1, "tags": ["👍 클릭 유도", "⏱ 간결함"]})
                    
                    # (데모용) 추가 메시지 시뮬레이션
                    if count_opt:
                         # 실제로는 프롬프트를 다르게 해서 다시 호출해야 함
                         generated_list.append({"text": f"(B안) {msg1.replace('하세요', '해볼까요?')}", "tags": ["⚖️ 감성 소구", "A/B 테스트"]})
                         generated_list.append({"text": f"(C안) [긴급] {msg1[:30]}...", "tags": ["🔥 긴급성", "짧은 호흡"]})
                    
                    st.session_state['generated_results'] = generated_list
                    st.toast("메시지 생성이 완료되었습니다!", icon="✅")
                    
                except Exception as e:
                    st.error(f"생성 중 오류 발생: {e}")


# --- [➡️ 오른쪽: 결과 & 액션 패널] ---
with col_right:
    st.subheader("📂 생성 결과 & 액션")
    
    if st.session_state['generated_results']:
        # 1) 생성 결과 리스트
        for idx, item in enumerate(st.session_state['generated_results']):
            # 카드 형태 컨테이너
            with st.container():
                st.markdown(f"""
                <div class="message-card">
                    <div style="margin-bottom:8px;">
                        {' '.join([f'<span class="tag">{tag}</span>' for tag in item['tags']])}
                    </div>
                    <div style="font-size:15px; line-height:1.6; margin-bottom:15px;">
                        {item['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 카드 하단 액션 버튼 (작게 배치)
                b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
                with b_col1:
                    if st.button("복사", key=f"copy_{idx}"):
                        st.toast("클립보드에 복사되었습니다!")
                with b_col2:
                    st.button("수정", key=f"edit_{idx}")
                with b_col3:
                    st.button("저장", key=f"save_{idx}")
            
            st.markdown("---") # 구분선
            
        # 3) 하단 글로벌 액션 영역
        st.markdown("#### 🚀 실행 액션")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.button("CRM 발송 예약", use_container_width=True)
        with g_col2:
            st.button("팀원 공유하기", use_container_width=True)
            
    else:
        # 결과 없을 때 빈 화면 안내
        st.container(border=True).info("👈 왼쪽에서 조건을 설정하고\n\n'메시지 생성하기'를 눌러주세요.")