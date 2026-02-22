"""
Tab 0 — Upload & Configure
Handles file ingestion, regex configuration, metadata joining,
and transitions the app into the 'data loaded' state.
"""
import streamlit as st
import re
import pandas as pd
from utils.loader import (
    load_report, load_metadata, extract_sample_ids,
    detect_im, merge_metadata, build_color_map,
)

def render():
    st.markdown("## Upload & Configure")
    st.markdown(
        "Provide a DIA-NN parquet report, a metadata file, and a regex pattern "
        "to extract a clean sample ID from the `Run` column."
    )

    # ── File uploaders ────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        parquet_file = st.file_uploader(
            "DIA-NN report (.parquet)",
            type=["parquet"],
            key="parquet_uploader",
        )
    with col2:
        meta_file = st.file_uploader(
            "Metadata file (.csv / .txt / .tsv)",
            type=["csv", "txt", "tsv"],
            key="meta_uploader",
        )

    st.markdown("---")

    # ── Regex configuration ───────────────────────────────────────────────
    st.markdown("### Sample ID extraction")
    st.markdown(
        "The regex is applied to the `Run` column. "
        "The **first capture group** becomes the `sample_id`. "
        "Leave as default to use the full Run value."
    )

    regex_input = st.text_input(
        "Regex pattern",
        value=st.session_state["regex_pattern"],
        help="Example: `.*[\\\\/](.+?)(?:\\.\\w+)?$` extracts the filename stem.",
    )

    # Live regex validation
    regex_valid = True
    try:
        re.compile(regex_input)
    except re.error as e:
        st.error(f"Invalid regex: {e}")
        regex_valid = False

    # Preview against a few Run values once parquet is loaded
    if parquet_file and regex_valid:
        try:
            preview_df = load_report(parquet_file)
            parquet_file.seek(0)  # reset for full load later
            sample_runs = preview_df["Run"].dropna().unique()[:6].tolist()
            st.markdown("**Preview** — first 6 unique Run values → extracted sample_id:")
            rows = []
            for run in sample_runs:
                m = re.search(regex_input, str(run))
                extracted = m.group(1) if (m and m.lastindex and m.lastindex >= 1) else str(run)
                rows.append({"Run (original)": run, "sample_id (extracted)": extracted})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Could not preview parquet: {e}")

    st.markdown("---")

    # ── Metadata preview ─────────────────────────────────────────────────
    if meta_file:
        try:
            meta_preview = load_metadata(meta_file)
            meta_file.seek(0)
            st.markdown("### Metadata preview")
            st.dataframe(meta_preview.head(10), use_container_width=True, hide_index=True)
            if "sample_id" not in meta_preview.columns:
                st.warning(
                    "⚠️  No `sample_id` column detected in metadata. "
                    "Add a column named `sample_id` to enable group-aware colouring."
                )
            if "group" not in meta_preview.columns:
                st.info(
                    "ℹ️  No `group` column detected. "
                    "Add a `group` column for groupwise comparisons."
                )
        except Exception as e:
            st.error(f"Could not read metadata: {e}")

    st.markdown("---")

    # ── Load button ──────────────────────────────────────────────────────
    can_load = parquet_file is not None and regex_valid

    if not can_load:
        st.info("Upload a parquet report to enable loading.")

    if can_load and st.button("🚀 Load data", type="primary"):
        with st.spinner("Loading parquet report…"):
            try:
                parquet_file.seek(0)
                df = load_report(parquet_file)
                df = extract_sample_ids(df, regex_input)

                has_im = detect_im(df)

                meta = None
                if meta_file:
                    meta_file.seek(0)
                    meta = load_metadata(meta_file)
                    df = merge_metadata(df, meta)

                color_map = build_color_map(
                    df,
                    group_col="group" if (meta is not None and "group" in meta.columns) else "sample_id",
                )

                # Persist to session
                st.session_state["report"] = df
                st.session_state["metadata"] = meta
                st.session_state["regex_pattern"] = regex_input
                st.session_state["has_im"] = has_im
                st.session_state["color_map"] = color_map
                st.session_state["data_loaded"] = True

                mode = "diaPASEF (IM enabled)" if has_im else "Standard DIA (no IM)"
                st.success(
                    f"✅ Loaded {len(df):,} rows · "
                    f"{df['sample_id'].nunique()} samples · "
                    f"Mode: **{mode}**"
                )
                if has_im:
                    st.info("Ion mobility columns detected — IM plots will be enabled across tabs.")

            except Exception as e:
                st.error(f"Failed to load data: {e}")
                raise
