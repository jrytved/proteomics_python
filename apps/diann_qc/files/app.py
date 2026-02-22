import streamlit as st
import pandas as pd
import re
from utils.loader import load_report, load_metadata, extract_sample_ids
from utils.session import init_session_state
from tabs import tab_upload, tab_raw_qc, tab_summary, tab_analysis, tab_normalization

st.set_page_config(
    page_title="DIA-NN QC Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
      font-family: 'IBM Plex Sans', sans-serif;
  }
  h1, h2, h3 {
      font-family: 'IBM Plex Mono', monospace;
      letter-spacing: -0.02em;
  }
  .stTabs [data-baseweb="tab"] {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.82rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
  }
  .stTabs [data-baseweb="tab-highlight"] {
      background-color: #00b4d8;
  }
  .metric-card {
      background: #0f1117;
      border: 1px solid #2a2d3e;
      border-radius: 8px;
      padding: 1rem 1.2rem;
      margin-bottom: 0.5rem;
  }
  .sidebar-badge {
      display: inline-block;
      background: #00b4d8;
      color: #000;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 3px;
      margin-left: 6px;
  }
  .sidebar-badge.warn {
      background: #f4a261;
  }
  .sidebar-badge.ok {
      background: #52b788;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
init_session_state()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 DIA-NN QC")
    st.markdown("---")

    if st.session_state.get("data_loaded"):
        df = st.session_state["report"]
        meta = st.session_state["metadata"]
        n_samples = df["sample_id"].nunique()
        n_pgs = df["Protein.Group"].nunique() if "Protein.Group" in df.columns else "—"
        n_precursors = df["Precursor.Id"].nunique() if "Precursor.Id" in df.columns else "—"
        has_im = st.session_state.get("has_im", False)

        st.markdown(f"**Samples** &nbsp;<span class='sidebar-badge ok'>{n_samples}</span>", unsafe_allow_html=True)
        st.markdown(f"**Protein groups** &nbsp;<span class='sidebar-badge'>{n_pgs}</span>", unsafe_allow_html=True)
        st.markdown(f"**Precursors** &nbsp;<span class='sidebar-badge'>{n_precursors}</span>", unsafe_allow_html=True)
        im_label = "diaPASEF ✓" if has_im else "Standard DIA"
        im_cls = "ok" if has_im else "warn"
        st.markdown(f"**Mode** &nbsp;<span class='sidebar-badge {im_cls}'>{im_label}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Groups** (from metadata)")
        if meta is not None and "group" in meta.columns:
            groups = meta["group"].value_counts()
            for g, cnt in groups.items():
                st.markdown(f"&nbsp;• `{g}` — {cnt} samples")
        else:
            st.caption("No 'group' column found in metadata.")

        st.markdown("---")
        if st.button("🔄 Reset / Load new data"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.info("Upload your data on the **Upload** tab to get started.")

# ── Tabs ─────────────────────────────────────────────────────────────────────
TAB_LABELS = [
    "📂  Upload & Configure",
    "📊  Raw Data QC",
    "📋  Summary Statistics",
    "🔍  Data Analysis",
    "⚖️  Normalization",
]

tabs = st.tabs(TAB_LABELS)

with tabs[0]:
    tab_upload.render()

with tabs[1]:
    tab_raw_qc.render()

with tabs[2]:
    tab_summary.render()

with tabs[3]:
    tab_analysis.render()

with tabs[4]:
    tab_normalization.render()
