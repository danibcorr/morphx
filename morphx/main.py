# 3pps
import streamlit as st
from configs.pages import PAGES

# Pages navigation
pg = st.navigation(PAGES)
pg.run()
