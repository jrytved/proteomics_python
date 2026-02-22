"""
Tab 3 — Data Analysis
Multivariate and inter-sample analyses: correlation heatmap,
hierarchical clustering, PCA/UMAP, UpSet plot, and volcano preview.
"""
import streamlit as st
from utils.plots import show_placeholder

def render():
    if not st.session_state.get("data_loaded"):
        st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
        return

    st.markdown("## Data Analysis")
    st.markdown("Multivariate views of sample similarity, identity overlap, and dimensionality reduction.")

    # ── Controls ─────────────────────────────────────────────────────────
    with st.expander("⚙️ Analysis settings", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            matrix_level = st.selectbox(
                "Feature level",
                ["Protein group (log2 intensity)", "Precursor (log2 intensity)"],
                key="analysis_level",
            )
        with col2:
            similarity_metric = st.selectbox(
                "Similarity metric (heatmap / dendrogram)",
                ["Pearson correlation", "Spearman correlation", "Jaccard index"],
                key="analysis_metric",
            )
        with col3:
            linkage_method = st.selectbox(
                "Hierarchical linkage",
                ["ward", "average", "complete", "single"],
                key="analysis_linkage",
            )
        min_samples_upset = st.slider(
            "UpSet plot: minimum samples sharing a protein group",
            min_value=1,
            max_value=max(2, st.session_state["report"]["sample_id"].nunique() if st.session_state.get("report") is not None else 2),
            value=2,
            key="upset_min_samples",
        )

    st.markdown("---")

    # ── Heatmap ───────────────────────────────────────────────────────────
    with st.expander("**Sample–Sample Correlation / Similarity Heatmap**", expanded=True):
        show_placeholder("TODO: clustered_heatmap")

    # ── Dendrogram ────────────────────────────────────────────────────────
    with st.expander("**Hierarchical Clustering Dendrogram**", expanded=True):
        show_placeholder("TODO: dendrogram")

    # ── PCA ───────────────────────────────────────────────────────────────
    with st.expander("**PCA**", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            show_placeholder("TODO: pca_scatter")
        with col2:
            show_placeholder("TODO: pca_scree")

    # ── UMAP ─────────────────────────────────────────────────────────────
    with st.expander("**UMAP**", expanded=False):
        st.info("ℹ️  UMAP requires the `umap-learn` package. Install with: `pip install umap-learn`")
        show_placeholder("TODO: umap_scatter")

    # ── UpSet ────────────────────────────────────────────────────────────
    with st.expander("**UpSet Plot — Identity Overlap Between Samples**", expanded=True):
        st.caption(
            "Shows the intersection sizes of protein groups detected across sample subsets. "
            f"Currently filtered to groups present in ≥ {st.session_state.get('upset_min_samples', 2)} samples."
        )
        show_placeholder("TODO: upset_plot")

    # ── Sample distance matrix ────────────────────────────────────────────
    with st.expander("**Sample-to-Sample Distance Matrix**", expanded=False):
        show_placeholder("TODO: distance_matrix")
