import streamlit as st
import pandas as pd
from utils.datahandler import ParquetReport, MetadataFile
from utils.session import init_session_state

def is_valid():

	if (st.session_state.get("report") is not None):
		if (st.session_state.get("report").data_loaded):
			return True

	else:
		return False

def render():

	if is_valid():
		
		st.title("Summary Statistics")

	else:
		st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
		return

