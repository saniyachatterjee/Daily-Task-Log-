#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
