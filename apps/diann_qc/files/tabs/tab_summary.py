"""
Tab 2 — Summary Statistics
Per-sample identification counts, CV metrics, data completeness,
run-order drift monitoring, and tabular summaries.
"""
import streamlit as st
from utils.plots import show_placeholder

_SECTIONS = {
    "Identification Counts": [
        ("Precursor IDs per sample", "ids_precursor"),
        ("Protein group IDs per sample", "ids_pg"),
    ],
    "ID Rate over Retention Time": [
        ("Precursor ID rate binned over RT (per sample)", "id_rate_rt"),
        ("Protein group ID rate binned over RT (per sample)", "id_rate_rt_pg"),
    ],
    "Intensity & Loading": [
        ("Median precursor intensity per sample", "median_intensity"),
        ("Total precursor intensity per sample", "total_intensity"),
    ],
    "Coefficient of Variation": [
        ("Average protein group CV per sample/group", "pg_cv_avg"),
        ("% Protein groups with CV ≤ 20% per sample", "pg_cv_pct20"),
        ("CV distribution (violin) per group", "cv_violin"),
    ],
    "Data Completeness": [
        ("Missingness heatmap (precursor × sample)", "missingness_heatmap"),
        ("% Data completeness per sample", "completeness_bar"),
        ("Cumulative IDs vs number of samples", "cumulative_ids"),
    ],
    "Run-Order Monitoring": [
        ("Total IDs over run order (drift detection)", "runorder_ids"),
        ("Median RT over run order", "runorder_rt"),
        ("Median intensity over run order", "runorder_intensity"),
        ("iRT / IndexRT deviation over run order (if available)", "runorder_irt"),
    ],
    "Spectral Library Usage": [
        ("Library coverage: detected / library size per sample", "lib_coverage"),
        ("Decoy/target ratio per sample", "decoy_target"),
    ],
    "Summary Table": [
        ("Per-sample KPI table (exportable)", "kpi_table"),
    ],
}

def render():
    if not st.session_state.get("data_loaded"):
        st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
        return

    st.markdown("## Summary Statistics")
    st.markdown("Per-sample and per-group identification quality metrics.")

    for section, plots in _SECTIONS.items():
        is_table = section == "Summary Table"
        with st.expander(f"**{section}**", expanded=(section in ("Identification Counts", "Summary Table"))):
            if is_table:
                st.info("TODO: Render interactive per-sample KPI table with CSV export button.")
            else:
                pairs = [plots[i:i+2] for i in range(0, len(plots), 2)]
                for pair in pairs:
                    cols = st.columns(len(pair))
                    for col, (label, key) in zip(cols, pair):
                        with col:
                            st.caption(label)
                            show_placeholder(f"TODO: {key}")
