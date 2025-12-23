@echo off
echo Amore AI Agent를 실행합니다...
cd %~dp0
streamlit run src/app.py
pause