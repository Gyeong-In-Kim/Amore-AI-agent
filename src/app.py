import streamlit as st
import os
import json
import time
import requests
import pandas as pd
from collections import Counter
from vector_db import init_db, search_best_product
from generator import generate_marketing_copy
from dotenv import load_dotenv

# 1. 기본 설정
load_dotenv()

if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state['db_initialized'] = True
if 'messages' not in st.session_state:
    st.session_state['messages'] = {}

st.set_page_config(page_title="Glow Code", page_icon="✨", layout="wide")

# 2. 유틸리티 함수 (날씨, 사용자 로드)
def get_weather(city="Daegu"):
    """현재 날씨를 가져옵니다. (위치 표시 추가)"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "📍 대구 | ☀️ 24°C / 맑음 (API키 필요)"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        res = requests.get(url).json()
        # [수정] 날씨 정보 앞에 위치(City)를 명시
        return f"📍 {city} | 🌡️ {res['main']['temp']}°C / {res['weather'][0]['description']}"
    except: 
        return f"📍 {city} | ☀️ 날씨 정보 수신 불가"
    
def get_weekly_forecast(city="Daegu"):
    """OpenWeatherMap API를 통해 5일간의 날씨 예보를 가져와 요약합니다."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "⚠️ API 키 필요"

    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return "⚠️ 날씨 정보 수신 실패"

        forecast_summary = []
        today = time.strftime("%Y-%m-%d")

        for item in data['list']:
            dt_txt = item['dt_txt']
            if "12:00:00" in dt_txt and today not in dt_txt:
                date = dt_txt.split(" ")[0][5:]
                temp = round(item['main']['temp'])
                desc = item['weather'][0]['description']
                forecast_summary.append(f"{date}: {temp}°C/{desc}")

        return ", ".join(forecast_summary[:5])

    except Exception as e:
        return f"❌ 예보 오류: {str(e)}"

def get_users():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, 'data', 'users.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [{"name": f"고객{i+1}", "age": 25+i, "skin_type": "복합성", "concerns": ["모공"]} for i in range(10)]

# 3. CSS 스타일링
st.markdown("""
<style>
    .weather-box { background-color: #f0f2f6; padding: 10px 20px; border-radius: 10px; border: 1px solid #ddd; font-weight: bold; color: #555; }
    .score-badge { background-color: #ebf8ff; color: #2b6cb0; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    div[data-testid="stPopoverBody"] { min-width: 500px !important; }
</style>
""", unsafe_allow_html=True)

# --- [상단 헤더] ---
weather = get_weather("Daegu") # 여기서 도시 설정 (기본 대구)
col_h1, col_h2 = st.columns([3, 1])

with col_h1: 
    st.title("✨ Glow Code")
with col_h2: 
    # 날씨 박스 출력
    st.markdown(f'<div class="weather-box">{weather}</div>', unsafe_allow_html=True)

st.divider()

# --- [메인 레이아웃] ---
left_col, center_col, right_col = st.columns([1, 2.5, 1.2], gap="large")

# 🟦 [LEFT] 전략 설정 & 플로팅 분석 버튼
with left_col:
    st.subheader("🛠️ 전략 설정")
    with st.container(border=True):
        mode = st.radio("모드 선택", ["모드 1: 고객 맞춤", "모드 2: 제품 교육", "모드 3: 시즌/날씨"])
        st.write("---")
        st.checkbox("신규 가입 웰컴", value=True)
        st.checkbox("재구매 유도")
        st.checkbox("장바구니 리마인드")
        st.checkbox("이탈 방지 SOS")

    st.write("") 
    
    st.subheader("📊 데이터 분석")
    with st.popover("📊 실시간 데이터 분석 리포트", use_container_width=True):
        st.markdown("### 📈 Campaign Insights")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("타겟 고객", "10명")
        m2.metric("매칭 성공률", "94%", "+2%")
        m3.metric("기대 매출", "₩452k", "High")
        
        st.divider()
        
        target_users = get_users()[:10]
        df_users = pd.DataFrame(target_users)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🧴 피부 타입 분포**")
            if not df_users.empty:
                skin_counts = df_users['skin_type'].value_counts()
                st.bar_chart(skin_counts, color="#FF9AA2", height=200)
        
        with c2:
            st.markdown("**😟 주요 고민 TOP 5**")
            if not df_users.empty:
                all_concerns = [c for sublist in df_users['concerns'] for c in sublist]
                top_concerns = Counter(all_concerns).most_common(5)
                df_concerns = pd.DataFrame(top_concerns, columns=['키워드', '수']).set_index('키워드')
                st.bar_chart(df_concerns, color="#90CDF4", height=200)
        
        if not df_users.empty:
            top_k = Counter([c for sublist in df_users['concerns'] for c in sublist]).most_common(1)[0][0]
            st.info(f"💡 **AI 제안:** 현재 **'{top_k}'** 고민이 가장 많습니다. 메시지에 **{top_k} 케어 효능**을 강조하면 반응률이 높아질 것입니다.")

    current_weather = get_weather("Daegu") 
    weekly_forecast = get_weekly_forecast("Daegu")

# 🟦 [CENTER] 메시지 생성 및 관리
with center_col:
    st.subheader("✉️ CRM 메시지 대시보드")
    
    if st.button("🚀 10명 고객 메시지 일괄 생성", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        start_time = time.time()
        
        for i, user in enumerate(get_users()[:10]):
            query = f"{user['skin_type']} 피부, 고민: {', '.join(user['concerns'])}"
            
            # [모드 3] 주간 예보 반영
            if "모드 3" in mode: 
                query += f", (참고: 현재 날씨 {current_weather}, 주간 예보: {weekly_forecast})"
                
            best_product = search_best_product(query)
            if best_product:
                context = f"고객: {user['name']}, 고민: {query}"
                copy = generate_marketing_copy(best_product, context)
                st.session_state['messages'][i] = {"product": best_product['name'], "copy": copy}
            
            progress_bar.progress((i + 1) / 10)
            
        st.session_state['gen_time'] = f"{round(time.time() - start_time, 2)}초"
        progress_bar.empty()
    
    if 'gen_time' in st.session_state:
        st.caption(f"⏱️ 생성 완료! (소요 시간: {st.session_state['gen_time']})")

    st.write("---")
    
    for i, user in enumerate(get_users()[:10]):
        msg_data = st.session_state['messages'].get(i, {"product": "-", "copy": ""})
        
        c1, c2 = st.columns([2, 1])
        with c1: st.markdown(f"**{user['name']}** <span class='score-badge'>Match 9{9-i}%</span>", unsafe_allow_html=True)
        with c2: st.caption(f"📦 {msg_data['product']}")
        
        st.text_area(f"{user['name']}님 메시지", value=msg_data['copy'], height=100, key=f"edit_{i}", label_visibility="collapsed")
        st.write("")

# 🟦 [RIGHT] 실시간 검색
with right_col:
    st.subheader("🔍 상품 검색")
    search_q = st.text_input("제품/성분 검색", placeholder="예: 시카, 안티에이징")
    if search_q:
        res = search_best_product(search_q)
        if res:
            with st.container(border=True):
                st.markdown(f"**{res['name']}**")
                st.caption(f"💰 {res['price']}원")
                st.write(res['description'])
        else:
            st.warning("검색 결과가 없습니다.")

# --- [하단 전송] ---
st.divider()
b_l, b_r = st.columns([3, 1])
with b_l: confirm = st.checkbox("✅ 분석 리포트와 메시지를 모두 확인했습니다.")
with b_r: st.button("📩 전송하기", type="primary", use_container_width=True, disabled=not confirm) 