# Standard libraries
from typing import Any, Final

# 3pps
import streamlit as st


class PagesConfig:
    PAGES: Final[dict[str, list[Any]]] = {
        "Home": [
            st.Page("pages/home.py", title="Home", icon=":material/home:", default=True)
        ],
        "Tools": [
            st.Page(
                "tools/transcriptions.py",
                title="Transcriptions",
                icon=":material/airwave:",
            ),
            st.Page(
                "tools/file_conversion.py",
                title="File Conversion",
                icon=":material/markdown:",
            ),
        ],
    }


pages_config: PagesConfig = PagesConfig()
