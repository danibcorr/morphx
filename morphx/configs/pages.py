# 3pps
import streamlit as st

# Page definitions
PAGES = {
	"Home": [
		st.Page("pages/home.py", title="Home", icon=":material/home:", default=True)
	],
	"Tools": [
		st.Page(
			"tools/transcriptions.py", title="Transcriptions", icon=":material/airwave:"
		)
	],
}
