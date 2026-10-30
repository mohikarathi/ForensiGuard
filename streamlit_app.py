"""Root Streamlit entrypoint for ForensiGuard.

Allows zero-configuration deployment on Streamlit Community Cloud (https://share.streamlit.io).
"""

from pathlib import Path
import sys

# Ensure src/ is on Python search path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from app.streamlit_app import main

if __name__ == "__main__":
    main()
