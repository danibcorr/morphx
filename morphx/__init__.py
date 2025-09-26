# 3pps
import streamlit as st
import torch

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

if "device" not in st.session_state:
	st.session_state["device"] = device
