import streamlit as st
import pandas as pd
from utils.datahandler import ParquetReport, MetadataFile
from utils.session import init_session_state


def render():

	st.title("DIA-NN QC")
	st.write("Quality Control and Analysis of Your DIA-NN Experiment")


	pq_raw  = st.file_uploader("Upload parquet report", accept_multiple_files=False, type="parquet")


	if pq_raw:
		report_data = pd.read_parquet(pq_raw)
		report = ParquetReport(name="TEST")
		report.load_data(report_data)
		st.session_state["report"] = report

		re_patt = st.text_input("Input a re-pattern to extract a unique identifier. The first group (parenthesis-enclosed portion) will be extracted.")

		if re_patt and st.session_state["report"].apply_regex(pattern=re_patt):
			st.write("Showing application of the re-pattern to the Run column")
			st.table(st.session_state["report"].dataframe[["Run", "Identifier"]].head(5))
		
		else:
			ex = st.session_state["report"].dataframe.iloc[0]["Run"]
			st.write(f"No useful re-pattern detected. Are you matching a pattern found below?")
			st.code(f"{ex}")
			st.code("AL000028_S_([A-Za-z]\d)")

	metadata_raw = st.file_uploader("Upload metadata file", accept_multiple_files=False, type=["txt", "csv", "tsv"])
	
	if metadata_raw:
		delim = st.selectbox("Pick a delimiter", [",", ";", "\t"],  index = None)

	if metadata_raw and delim:
		
		metadata_data = pd.read_csv(metadata_raw, sep = delim)
		metadata = MetadataFile(name="TEST")
		st.session_state["metadata"] = metadata
		
		metadata.load_data(metadata_data)


		st.write(f"The following columns were loaded for the metadata and the metadata has the shape: {st.session_state["metadata"].dataframe.shape}")
		st.table(st.session_state["metadata"].cols, border = "horizontal")
