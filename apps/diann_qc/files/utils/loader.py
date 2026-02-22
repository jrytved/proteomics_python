import pandas as pd
import re
import streamlit as st

# Columns present only in diaPASEF / IM-enabled data
IM_COLUMNS = {"IM", "iIM", "Predicted.IM", "IM.Predicted"}


def load_report(uploaded_file) -> pd.DataFrame:
    """Load DIA-NN parquet report."""
    df = pd.read_parquet(uploaded_file)
    return df

def load_metadata(uploaded_file) -> pd.DataFrame:
    """Load metadata CSV or TSV."""
    name = uploaded_file.name
    sep = "\t" if name.endswith(".txt") or name.endswith(".tsv") else ","
    meta = pd.read_csv(uploaded_file, sep=sep)
    # Normalise column names to lowercase
    meta.columns = [c.strip().lower() for c in meta.columns]
    return meta

def extract_sample_ids(df: pd.DataFrame, pattern: str) -> pd.DataFrame:
    """
    Apply a regex pattern to the 'Run' column to extract a sample_id.
    The first capture group is used; falls back to the full Run value.
    """
    def _extract(run_val):
        try:
            m = re.search(pattern, str(run_val))
            if m and m.lastindex and m.lastindex >= 1:
                return m.group(1)
            return str(run_val)
        except re.error:
            return str(run_val)

    df = df.copy()
    df["sample_id"] = df["Run"].apply(_extract)
    return df

def detect_im(df: pd.DataFrame) -> bool:
    """Return True if the dataframe contains ion-mobility columns."""
    return bool(IM_COLUMNS.intersection(df.columns))

def merge_metadata(df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join metadata onto the report on sample_id.
    Metadata must have a column called 'sample_id' (case-insensitive normalised).
    """
    if "sample_id" not in meta.columns:
        st.warning(
            "Metadata file has no 'sample_id' column — group coloring will be unavailable. "
            "Please add a 'sample_id' column matching the extracted run IDs."
        )
        return df
    df = df.merge(meta, on="sample_id", how="left")
    return df

def build_color_map(df: pd.DataFrame, group_col: str = "group") -> dict:
    """Return a dict mapping group label → hex colour."""
    import plotly.express as px
    if group_col not in df.columns:
        # Fall back: one colour per sample
        groups = df["sample_id"].unique().tolist()
    else:
        groups = df[group_col].dropna().unique().tolist()

    palette = px.colors.qualitative.Pastel + px.colors.qualitative.Bold
    return {g: palette[i % len(palette)] for i, g in enumerate(sorted(groups))}
