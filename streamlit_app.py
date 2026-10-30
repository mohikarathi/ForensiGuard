"""Root Streamlit entrypoint for ForensiGuard.

Allows zero-configuration deployment on Streamlit Community Cloud (https://share.streamlit.io).
"""

from pathlib import Path
import sys
import streamlit as st

# Must be called as the very first Streamlit command in the main script for full-width layout
st.set_page_config(
    page_title="ForensiGuard — Evidence Inspector",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure src/ is on Python search path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.streamlit_app import main

if __name__ == "__main__":
    main()
