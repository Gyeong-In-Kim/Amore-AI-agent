# [src/app.py 수정본]
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

# 2. 유틸리티 함수
def get_weather(city="Daegu"):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "📍 대구 | ☀️ 24°C / 맑음 (API키 필요)"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        res = requests.get(url).json()
        return f"📍 {city} | 🌡️ {res['main']['temp']}°C / {res['weather'][0]['description']}"
    except: return f"📍 {city} | ☀️ 날씨 정보 수신 불가"
    
def get_weekly_forecast(city="Daegu"):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "⚠️ API 키 필요"
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200: return "⚠️ 날씨 정보 수신 실패"
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
    except Exception as e: return f"❌ 예보 오류: {str(e)}"

def get_users():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, 'data', 'users.json')
        with open(file_path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return [{"name": f"고객{i+1}", "age": 25+i, "skin_type": "복합성", "concerns": ["모공"]} for i in range(10)]

# CSS 스타일링
st.markdown("""
<style>
    .weather-box { background-color: #f0f2f6; padding: 10px 20px; border-radius: 10px; border: 1px solid #ddd; font-weight: bold; color: #555; }
    .score-badge { background-color: #ebf8ff; color: #2b6cb0; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    div[data-testid="stPopoverBody"] { min-width: 500px !important; }
</style>
""", unsafe_allow_html=True)

# 헤더
weather = get_weather("Daegu")
col_h1, col_h2 = st.columns([3, 1])
with col_h1: st.title("✨ Glow Code")
with col_h2: st.markdown(f'<div class="weather-box">{weather}</div>', unsafe_allow_html=True)
st.divider()

# 메인 레이아웃
left_col, center_col, right_col = st.columns([1, 2.5, 1.2], gap="large")

# [LEFT] 설정
with left_col:
    st.subheader("🛠️ 전략 설정")
    with st.container(border=True):
        mode = st.radio("모드 선택", ["모드 1: 고객 맞춤", "모드 2: 제품 교육", "모드 3: 시즌/날씨"])
        st.write("---")
        st.checkbox("신규 가입 웰컴", value=True)
        st.checkbox("재구매 유도")
        st.checkbox("장바구니 리마인드")

    st.write("") 
    st.subheader("📊 데이터 분석")
    with st.popover("📊 실시간 분석 리포트", use_container_width=True):
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
            if not df_users.empty: st.bar_chart(df_users['skin_type'].value_counts(), color="#FF9AA2", height=200)
        with c2:
            if not df_users.empty:
                all_concerns = [c for sublist in df_users['concerns'] for c in sublist]
                st.bar_chart(pd.DataFrame(Counter(all_concerns).most_common(5), columns=['키워드', '수']).set_index('키워드'), color="#90CDF4", height=200)

    current_weather = get_weather("Daegu") 
    weekly_forecast = get_weekly_forecast("Daegu")

# [CENTER] 메시지 생성 (핵심 수정 부분 포함)
with center_col:
    st.subheader("✉️ CRM 메시지 대시보드")
    
    if st.button("🚀 10명 고객 메시지 일괄 생성", type="primary", use_container_width=True):
        if 'db_initialized' not in st.session_state:
            init_db()
            st.session_state['db_initialized'] = True
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()
        
        users = get_users()[:10]
        for i, user in enumerate(users):
            status_text.text(f"🔄 {user['name']}님 분석 및 메시지 생성 중... ({i+1}/10)")
            
            concerns_text = ", ".join(user.get('concerns', ['피부 고민']))
            query = f"{user.get('skin_type', '모든')} 피부, 고민: {concerns_text}"
            
            if "모드 3" in mode: query += f", (상황: 현재 날씨 {current_weather}, 주간 예보: {weekly_forecast})"
            elif "모드 1" in mode: query += ", (포인트: 고객 맞춤형 혜택 강조)"
            
            best_product = search_best_product(query)
            
            if best_product:
                context = f"고객: {user['name']}, 고민: {concerns_text}, 검색상황: {query}"
                copy = generate_marketing_copy(best_product, context)
                
                # 결과 저장
                st.session_state['messages'][i] = {
                    "product": best_product['name'], 
                    "copy": copy,
                    "match_score": 90 + (i % 9)
                }
                # 🔥 [핵심 수정] 텍스트 에디터의 세션 상태를 강제로 업데이트!
                # 이 줄이 없으면 화면의 텍스트 상자가 갱신되지 않고 빈 값으로 남습니다.
                st.session_state[f"edit_{i}"] = copy 

            else:
                st.session_state['messages'][i] = {"product": "추천 없음", "copy": "적절한 제품을 찾지 못했습니다.", "match_score": 0}
            
            progress_bar.progress((i + 1) / 10)
            
        st.session_state['gen_time'] = f"{round(time.time() - start_time, 2)}초"
        progress_bar.empty()
        status_text.empty()
        st.toast("메시지 생성이 완료되었습니다!", icon="✅")
    
    if 'gen_time' in st.session_state:
        st.caption(f"⏱️ 생성 완료! (소요 시간: {st.session_state['gen_time']})")

    st.write("---")
    
    users = get_users()[:10]
    for i, user in enumerate(users):
        msg_data = st.session_state['messages'].get(i, {"product": "-", "copy": "", "match_score": 0})
        
        c1, c2 = st.columns([2, 1])
        with c1: st.markdown(f"**{user['name']}** <span class='score-badge'>Match {msg_data.get('match_score', 0)}%</span>", unsafe_allow_html=True)
        with c2: st.caption(f"📦 {msg_data['product']}")
        
        # 메시지 수정 창
        new_copy = st.text_area(
            f"{user['name']}님 메시지", 
            value=msg_data['copy'], 
            height=100, 
            key=f"edit_{i}",  # 이 키(key)와 위에서 업데이트한 세션 키가 일치해야 함
            label_visibility="collapsed"
        )
        
        if new_copy != msg_data['copy']:
            st.session_state['messages'][i]['copy'] = new_copy
            
        st.write("")

# [RIGHT] 검색
with right_col:
    st.subheader("🔍 상품 검색")
    search_q = st.text_input("제품/성분 검색", placeholder="예: 시카")
    if search_q:
        res = search_best_product(search_q)
        if res:
            with st.container(border=True):
                st.markdown(f"**{res['name']}**")
                st.caption(f"💰 {res['price']}원")
                st.write(res['description'])
        else: st.warning("검색 결과가 없습니다.")

# 하단 전송
st.divider()
b_l, b_r = st.columns([3, 1])
with b_l: confirm = st.checkbox("✅ 확인 완료")
with b_r: st.button("📩 전송하기", type="primary", use_container_width=True, disabled=not confirm)