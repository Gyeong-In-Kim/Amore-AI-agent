import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(page_title="Glow Code", page_icon="✨", layout="wide")

# 2. 커스텀 CSS (날씨, 뱃지, 분석 카드 등)
st.markdown("""
<style>
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; margin-bottom: 20px; }
    .weather-box { background-color: #f0f2f6; padding: 10px 20px; border-radius: 10px; border: 1px solid #ddd; font-size: 14px; }
    
    /* 분석 지표 카드 (플로팅 창 내부용) */
    .analysis-card {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .analysis-val { font-size: 18px; font-weight: 800; color: #3182ce; }
    .analysis-label { font-size: 11px; color: #718096; }

    /* 매칭 점수 뱃지 */
    .score-badge {
        background-color: #ebf8ff;
        color: #2b6cb0;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    
    /* 고객 상태 뱃지 */
    .badge { padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; color: white; margin-left: 5px; }
    .badge-vip { background-color: #f1c40f; }
    .badge-new { background-color: #2ecc71; }
    .badge-churn { background-color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수
def get_users():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        with open(os.path.join(project_root, 'data', 'users.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [{"name": f"고객{i+1}", "age": 25+i, "skin_type": "복합성", "concerns": ["모공"]} for i in range(10)]

users = get_users()

# --- [상단 헤더 영역] ---
st.markdown(f"""
<div class="header-container">
    <div style="font-size: 32px; font-weight: 800;">✨ Glow Code</div>
    <div class="weather-box">☀️ <b>오늘의 날씨</b>: 24°C / 맑음 (대구광역시)</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- [메인 레이아웃: 3단 구조] ---
left_col, center_col, right_col = st.columns([1, 2.5, 1.2], gap="large")

# 🟦 [LEFT] 전략 설정 & 플로팅 분석 버튼
with left_col:
    st.subheader("🛠️ 전략 설정")
    with st.container(border=True):
        st.write("**🎯 발송 목적 선택**")
        st.checkbox("신규 가입 웰컴", value=True)
        st.checkbox("재구매 유도", value=True)
        st.checkbox("장바구니 리마인드")
        st.checkbox("이탈 방지 SOS")
        
        st.write("---")
        
        # 🔥 핵심 수정: 플로팅 분석 리포트 버튼 (Popover)
    st.subheader("📊 데이터 분석")
    with st.popover("캠페인 예측 지표", use_container_width=True):
        st.markdown("### 📈 Campaign Insights")
        st.caption("현재 설정 기준 AI 예측 수치입니다.")
            
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.markdown('<div class="analysis-card"><div class="analysis-val">84%</div><div class="analysis-label">매칭률</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="analysis-card"><div class="analysis-val">12.5%</div><div class="analysis-label">예상 CTR</div></div>', unsafe_allow_html=True)
        with p_col2:
            st.markdown('<div class="analysis-card"><div class="analysis-val">10명</div><div class="analysis-label">타겟수</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="analysis-card"><div class="analysis-val">₩452k</div><div class="analysis-label">기대매출</div></div>', unsafe_allow_html=True)
            
        st.info("💡 팁: '재구매 유도' 목적 선택 시 예상 매출이 15% 상승합니다.")

# 🟦 [CENTER] 메인 작업 영역
with center_col:
    st.subheader("✉️ CRM 메시지 작성")
    
    if st.button("🚀 메시지 일괄 생성 시작", type="primary", use_container_width=True):
        st.session_state['msg_generated'] = True

    st.write("---")
    
    # 10명의 고객 리스트
    for i, user in enumerate(users[:10]):
        # 고객 정보 및 뱃지
        status_badge = '<span class="badge badge-vip">VIP</span>' if i % 4 == 0 else '<span class="badge badge-new">NEW</span>'
        
        col_info, col_prod = st.columns([2, 1])
        with col_info:
            st.markdown(f"**{user['name']}** ({user['age']}세) {status_badge} <span class='score-badge'>매칭 9{9-i}%</span>", unsafe_allow_html=True)
            st.caption(f"페르소나: 성분 중심 실속파 / 고민: {', '.join(user['concerns'])}")
        with col_prod:
            st.markdown(f"📦 **추천**: `제품 {i+1}`")
        
        default_msg = ""
        if st.session_state.get('msg_generated'):
            default_msg = f"[Glow Code] {user['name']}님, {user['concerns'][0]} 고민을 해결할 특별한 추천템을 확인해보세요! ✨"
        
        st.text_area(f"msg_{i}", value=default_msg, height=80, label_visibility="collapsed")
        st.write("")

# 🟦 [RIGHT] 상품 검색 탭
with right_col:
    st.subheader("🔍 상품 검색")
    with st.container(border=True):
        st.text_input("제품/성분 검색", placeholder="예: 시카, 세럼")
        st.write("---")
        st.write("**DB 검색 결과**")
        st.caption("• 나노펩타이드 토너")
        st.caption("• 시카 리페어 크림")
        st.caption("• 비타민C 앰플")

# --- [하단 전송 제어] ---
st.divider()
b_left, b_right = st.columns([3, 1])
with b_left:
    confirm = st.checkbox("✅ 모든 메시지와 분석 수치를 최종 확인했습니다.")
with b_right:
    st.button("📩 메시지 일괄 전송", type="primary", use_container_width=True, disabled=not confirm)