# Standard libraries
from typing import Any

# 3pps
import streamlit as st

# Page definitions
PAGES: dict[str, list[Any]] = {
	"Home": [
		st.Page("pages/home.py", title="Home", icon=":material/home:", default=True)
	],
	"Tools": [
		st.Page(
			"tools/transcriptions.py", title="Transcriptions", icon=":material/airwave:",
		),
		st.Page(
			"tools/genppt.py", title="PPT Generator", icon=":material/co_present:",
		)
	],
}
