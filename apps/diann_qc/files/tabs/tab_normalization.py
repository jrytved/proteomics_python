"""
Tab 4 — Normalization & Preprocessing
Interactive normalization with before/after comparison and export.
"""
import streamlit as st
from utils.plots import show_placeholder

METHODS = [
    "None (raw)",
    "Median centering",
    "Quantile normalization",
    "Variance stabilizing normalization (VSN)",
    "Total intensity (TIC) normalization",
    "Z-score (per protein)",
]

def render():
    if not st.session_state.get("data_loaded"):
        st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
        return

    st.markdown("## Normalization & Preprocessing")
    st.markdown(
        "Compare normalization strategies on intensity distributions before exporting "
        "a processed matrix for downstream analysis."
    )

    # ── Settings ─────────────────────────────────────────────────────────
    with st.expander("⚙️ Normalization settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            method = st.selectbox("Normalization method", METHODS, key="norm_method")
            level = st.selectbox(
                "Feature level",
                ["Protein group", "Precursor"],
                key="norm_level",
            )
        with col2:
            imputation = st.selectbox(
                "Missing value imputation",
                ["None", "Min / 5 (Perseus-style)", "KNN (k=5)", "Median per protein"],
                key="norm_imputation",
            )
            min_valid = st.slider(
                "Min. valid values per protein (% of samples)",
                min_value=0, max_value=100, value=50,
                key="norm_min_valid",
            )

        apply_btn = st.button("▶ Apply", type="primary", key="norm_apply")
        if apply_btn:
            st.info("TODO: Apply normalization logic and cache result in session state.")

    st.markdown("---")

    # ── Before / After ───────────────────────────────────────────────────
    st.markdown("### Before vs After")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Before normalization — intensity distributions")
        show_placeholder("TODO: intensity_before")
    with col2:
        st.caption("After normalization — intensity distributions")
        show_placeholder("TODO: intensity_after")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Before — sample correlation heatmap")
        show_placeholder("TODO: corr_before")
    with col2:
        st.caption("After — sample correlation heatmap")
        show_placeholder("TODO: corr_after")

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Before — PCA")
        show_placeholder("TODO: pca_before")
    with col2:
        st.caption("After — PCA")
        show_placeholder("TODO: pca_after")

    st.markdown("---")

    # ── Export ───────────────────────────────────────────────────────────
    st.markdown("### Export")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬇️ Download normalised matrix (.csv)", key="export_norm_csv", disabled=True)
        st.caption("Apply normalization above to enable export.")
    with col2:
        st.button("⬇️ Download wide-format protein matrix (.csv)", key="export_wide_csv", disabled=True)
