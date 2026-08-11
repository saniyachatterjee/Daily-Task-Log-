@echo off
cd /d "%~dp0"
python -m pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
pause
