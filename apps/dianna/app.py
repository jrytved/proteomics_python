import streamlit as st
import pandas as pd
from utils.datahandler import ParquetReport, MetadataFile
from utils.session import init_session_state

init_session_state()

st.title("DIANNA")
st.write("Quality Control and Analysis of Your DIA-NN Experiment")


pq_raw  = st.file_uploader("Upload parquet report", accept_multiple_files=False, type="parquet")


if pq_raw:
    report_data = pd.read_parquet(pq_raw)
    report = ParquetReport(name="TEST")
    report.load_data(report_data)
    st.session_state["report"] = report

    re_patt = st.text_input("Input a re-pattern to extract a unique identifier")

    if re_patt and  st.session_state["report"].apply_regex(pattern=re_patt):
        st.write("Showing application of re-pattern to Run")
        st.table(st.session_state["report"].dataframe["Clean_ID"].head(5))
    else:
        ex = st.session_state["report"].dataframe.iloc[0]["Run"]
        st.write(f"No useful re-pattern detected. Are you matching {ex}?")

metadata_raw = st.file_uploader("Upload metadata file", accept_multiple_files=False, type=["txt", "csv", "tsv"])

if metadata_raw:
    metadata_data = pd.read_csv(metadata_raw, sep = ";")
    metadata = MetadataFile(name="TEST")
    metadata.load_data(metadata_data)
    st.session_state["metadata"] = metadata

    st.write("Showing first 5 rows of metadata")
    st.table(st.session_state["metadata"].dataframe.head(5))
