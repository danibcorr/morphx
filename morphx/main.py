# 3pps
import streamlit as st

# Own modules
from morphx.configs import pages_config

# Pages navigation
pg = st.navigation(pages_config.PAGES)
pg.run()
