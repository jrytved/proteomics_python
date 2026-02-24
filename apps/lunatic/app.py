# -*- coding: utf-8 -*-
"""
Lunatic Peptide Quantification Visualisation App
Run with:  streamlit run lunatic_app.py
"""

import os
import re
import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =============================================================================
# Domain classes
# =============================================================================

class LunaticFolder:
    def __init__(self, path_str):
        self.path_str = str(path_str)
        self.path = Path(self.path_str)

        m = re.match(r"^\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m\d{2}_\d+_(.+)$", self.path.name)
        if not m:
            raise ValueError(f"Folder name does not match Lunatic pattern: {self.path.name}")
        self.id = m.group(1)

        if not os.path.isdir(self.path_str):
            raise AssertionError(f"Not a directory: {self.path_str}")

        contents = os.listdir(self.path_str)
        txt_files  = [f for f in contents if os.path.splitext(f)[1] == ".txt"]
        html_files = [f for f in contents if os.path.splitext(f)[1] == ".html"]

        if len(txt_files) != 1:
            raise AssertionError(f"Expected 1 .txt file, found {len(txt_files)}")
        if len(html_files) != 1:
            raise AssertionError(f"Expected 1 .html file, found {len(html_files)}")

        self.txt_path  = os.path.join(self.path, txt_files[0])
        self.html_path = os.path.join(self.path, html_files[0])

        self.graphs_path = os.path.join(self.path, "Graphs")
        if not (os.path.exists(self.graphs_path) and os.path.isdir(self.graphs_path)):
            raise AssertionError("Graphs sub-folder not found.")

        self.graph_image_paths = [
            os.path.join(self.graphs_path, p) for p in os.listdir(self.graphs_path)
        ]
        self.dataframe = pd.read_csv(self.txt_path, sep="\t")

    def get_conc_plot(self):
        plt.style.use("Solarize_Light2")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(self.dataframe["Sample name"], self.dataframe["Peptide (ug/ul)"],
               color="#5b8db8", edgecolor="#1a3a5c", linewidth=0.8)
        ax.scatter(self.dataframe["Sample name"], self.dataframe["Peptide (ug/ul)"],
                   color="#1a3a5c", zorder=5, s=40)
        ax.set_xticklabels(self.dataframe["Sample name"].tolist(), rotation=90)
        ax.set_xlabel("Sample ID", labelpad=8)
        ax.set_ylabel("Peptide Concentration [ug/uL]", labelpad=8)
        ax.set_title(f"Peptide c [ug/uL] - {self.id}", fontsize=13, fontweight="bold")
        fig.tight_layout()
        return fig, ax


class LunaticExperiment:
    def __init__(self, paths):
        self.paths   = [str(p) for p in paths]
        self.folders = [LunaticFolder(p) for p in self.paths]

    @property
    def combined_dataframe(self):
        dfs = []
        for folder in self.folders:
            df = folder.dataframe.copy()
            df.insert(0, "Subfolder", folder.id)
            dfs.append(df)
        return pd.concat(dfs, ignore_index=True)

    def get_experiment_conc_plot(self):
        cdf = self.combined_dataframe
        plt.style.use("Solarize_Light2")
        fig, ax = plt.subplots(figsize=(max(12, len(cdf) // 2), 5))
        colors = plt.cm.tab10.colors
        sf_ids = cdf["Subfolder"].unique().tolist()
        color_map = {sf: colors[i % len(colors)] for i, sf in enumerate(sf_ids)}
        ax.bar(range(len(cdf)), cdf["Peptide (ug/ul)"],
               color=cdf["Subfolder"].map(color_map), edgecolor="white", linewidth=0.4)
        ax.scatter(range(len(cdf)), cdf["Peptide (ug/ul)"], color="black", zorder=5, s=25)
        ax.set_xticks(range(len(cdf)))
        ax.set_xticklabels(cdf["Sample name"].tolist(), rotation=90, fontsize=7)
        ax.set_xlabel("Sample ID", labelpad=8)
        ax.set_ylabel("Peptide Concentration [ug/uL]", labelpad=8)
        ax.set_title("Experiment-Wide Peptide c [ug/uL]", fontsize=13, fontweight="bold")
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(facecolor=color_map[sf], label=sf) for sf in sf_ids],
                  loc="upper right", fontsize=8, framealpha=0.8)
        fig.tight_layout()
        return fig, ax


# =============================================================================
# UI helpers
# =============================================================================

def styled_dataframe(df):
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    styler = df.style.format(precision=4)
    if numeric_cols:
        styler = styler.background_gradient(subset=numeric_cols, cmap="Blues")
    return styler


def html_embed(html_path):
    with open(html_path, "r", encoding="utf-8") as fh:
        b64 = base64.b64encode(fh.read().encode()).decode()
    st.markdown(
        f'<iframe src="data:text/html;base64,{b64}" width="100%" height="700px" '
        'style="border:1px solid #ddd; border-radius:8px;"></iframe>',
        unsafe_allow_html=True,
    )


def image_grid(image_paths, cols=3):
    for row in [image_paths[i:i+cols] for i in range(0, len(image_paths), cols)]:
        for col, img in zip(st.columns(len(row)), row):
            with col:
                st.image(img, use_container_width=True, caption=os.path.basename(img))


def pick_folders_via_dialog():
    """
    Repeatedly open a native folder-picker dialog (askdirectory) until the
    user cancels, collecting one folder per dialog invocation.

    askdirectory is the only tkinter dialog that reliably returns a folder
    path without triggering OS file-open behaviour.  True multi-select is
    not supported by the underlying platform APIs for directories, so we
    loop instead: each call adds one folder, and cancelling (or picking the
    same folder twice) stops the loop.

    Returns a list of unique folder path strings.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        collected = []
        while True:
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes("-topmost", True)
            already = "\n".join(f"  - {p}" for p in collected)
            prompt = (
                f"Select a Lunatic folder ({len(collected)} selected so far"
                + (f":\n{already}" if already else "")
                + ").\n\nCancel to finish."
            )
            # Show a quick info box so the user knows what is happening
            # only after at least one folder has been picked
            if collected:
                messagebox.showinfo(
                    "Keep selecting folders",
                    prompt,
                    parent=root,
                )
            selected = filedialog.askdirectory(
                title=f"Folder {len(collected)+1}: select a Lunatic folder (Cancel when done)",
                parent=root,
            )
            root.destroy()
            if not selected or selected in collected:
                # Empty string = user cancelled -> stop looping
                break
            collected.append(selected)
        return collected
    except Exception as exc:
        st.error(
            f"Could not open system folder dialog ({exc}). "
            "Please paste paths manually instead."
        )
        return []


# =============================================================================
# Pages
# =============================================================================

def page_folder_picker():
    st.markdown("## Load Experiment Folders")
    st.caption(
        "Click **Browse** to open your system's folder picker and add each "
        "Lunatic output folder to the list. You can also paste paths directly. "
        "When all folders are queued, click **Load Experiment**."
    )

    if "staged_paths" not in st.session_state:
        st.session_state["staged_paths"] = []
    staged = st.session_state["staged_paths"]

    # --- controls row ---------------------------------------------------------
    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.markdown("**Pick via system dialog**")
        st.caption("A folder picker will open repeatedly. Select one folder per dialog; cancel (or press Escape) when you are done.")
        if st.button("Browse for folders...", use_container_width=True):
            chosen_folders = pick_folders_via_dialog()
            added = 0
            for folder_path in chosen_folders:
                if folder_path not in staged:
                    staged.append(folder_path)
                    added += 1
            if added:
                st.session_state["staged_paths"] = staged
                st.rerun()
            elif chosen_folders:
                st.warning("All selected folders are already in the list.")

    with right_col:
        st.markdown("**Or type / paste a path**")
        with st.form("manual_add", clear_on_submit=True, border=False):
            manual = st.text_input(
                "path",
                label_visibility="collapsed",
                placeholder="/data/lunatic/2026-02-09_11h33m15_100832_JOHA_jr_fetal_1-15",
            )
            if st.form_submit_button("Add") and manual.strip():
                p = manual.strip()
                if p not in staged:
                    staged.append(p)
                    st.session_state["staged_paths"] = staged
                else:
                    st.warning("Already in list.")

    # --- staged list ----------------------------------------------------------
    st.markdown("---")
    if not staged:
        st.info("No folders queued yet.")
    else:
        st.markdown(f"**{len(staged)} folder(s) queued**")
        for i, path in enumerate(staged):
            l, r = st.columns([9, 1])
            with l:
                valid = os.path.isdir(path)
                tag = "`[OK]`" if valid else "`[NOT FOUND]`"
                st.markdown(f"{tag}  `{path}`")
            with r:
                if st.button("X", key=f"rm_{i}", help="Remove"):
                    staged.pop(i)
                    st.session_state["staged_paths"] = staged
                    st.rerun()

    # --- load / clear ---------------------------------------------------------
    st.markdown("---")
    btn_load, btn_clear, _ = st.columns([2, 1, 4])

    with btn_clear:
        if st.button("Clear all", use_container_width=True, disabled=not staged):
            st.session_state["staged_paths"] = []
            st.rerun()

    with btn_load:
        if st.button("Load Experiment", type="primary",
                     use_container_width=True, disabled=not staged):
            errors, folders = [], []
            with st.spinner("Loading..."):
                for path in staged:
                    try:
                        folders.append(LunaticFolder(path))
                    except Exception as exc:
                        errors.append(f"`{path}` -> {exc}")
            if errors:
                st.error("Some folders failed to load:")
                for e in errors:
                    st.markdown(f"- {e}")
            if folders:
                exp = LunaticExperiment.__new__(LunaticExperiment)
                exp.paths   = [f.path_str for f in folders]
                exp.folders = folders
                st.session_state["experiment"]  = exp
                st.session_state["active_page"] = "experiment_overview"
                st.success(f"Loaded {len(folders)} folder(s).")
                st.rerun()


def page_experiment_overview(experiment):
    st.markdown("## Experiment Overview")
    tab_plot, tab_table = st.tabs(["Concentration Plot", "Data Table"])

    with tab_plot:
        fig, _ = experiment.get_experiment_conc_plot()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with tab_table:
        cdf = experiment.combined_dataframe
        dl_col, info_col = st.columns([1, 5])
        with dl_col:
            st.download_button(
                label="Download as CSV",
                data=cdf.to_csv(index=False, sep=","),
                file_name="lunatic_experiment_combined.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with info_col:
            st.caption(f"{len(cdf)} samples across {len(experiment.folders)} subfolder(s)")
        st.dataframe(styled_dataframe(cdf), use_container_width=True, height=500)


def page_folder_view(folder):
    st.markdown(f"## Subfolder: `{folder.id}`")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Concentration Plot", "Data Table", "Graph Images", "HTML Report"]
    )

    with tab1:
        fig, _ = folder.get_conc_plot()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with tab2:
        st.dataframe(styled_dataframe(folder.dataframe),
                     use_container_width=True, height=400)

    with tab3:
        if folder.graph_image_paths:
            image_grid(folder.graph_image_paths, cols=3)
        else:
            st.info("No images found in the Graphs folder.")

    with tab4:
        st.markdown(f"**HTML report:** `{folder.html_path}`")
        if st.button("Embed report", key=f"embed_{folder.id}"):
            html_embed(folder.html_path)
        st.caption("Tip: open the path above in your browser for the full interactive view.")


# =============================================================================
# Sidebar
# =============================================================================

def sidebar(experiment):
    st.sidebar.markdown("# Lunatic Viewer")
    st.sidebar.markdown("---")

    if st.sidebar.button("Load / Change Folders", use_container_width=True):
        st.session_state["active_page"]     = "folder_picker"
        st.session_state["selected_folder"] = None
        st.rerun()

    if experiment:
        if st.sidebar.button("Experiment Overview", use_container_width=True):
            st.session_state["active_page"]     = "experiment_overview"
            st.session_state["selected_folder"] = None
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("**Subfolders**")
        for folder in experiment.folders:
            if st.sidebar.button(folder.id, use_container_width=True, key=f"sb_{folder.id}"):
                st.session_state["active_page"]     = "folder_view"
                st.session_state["selected_folder"] = folder.id
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("Lunatic Peptide Quant Viewer v1.0")


# =============================================================================
# Entry point
# =============================================================================

def main():
    st.set_page_config(
        page_title="Lunatic Peptide Viewer",
        page_icon="microscope",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
        html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
        h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; letter-spacing: -0.5px; }
        .stButton > button { border-radius: 4px; transition: background 0.15s; }
        [data-testid="stSidebar"] { background: #0d2035; }
        [data-testid="stSidebar"] * { color: #e0e6ef !important; }
        [data-testid="stSidebar"] button {
            background: #1a3a5c !important; border-color: #2a5a8c !important;
            color: #e0e6ef !important; text-align: left;
        }
        [data-testid="stSidebar"] button:hover { background: #2a5a8c !important; }
        </style>
    """, unsafe_allow_html=True)

    for key, default in [
        ("active_page", "folder_picker"),
        ("selected_folder", None),
        ("experiment", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    experiment = st.session_state["experiment"]
    sidebar(experiment)

    page = st.session_state["active_page"]

    if page == "folder_picker" or experiment is None:
        page_folder_picker()
    elif page == "experiment_overview":
        page_experiment_overview(experiment)
    elif page == "folder_view":
        fid = st.session_state["selected_folder"]
        folder = next((f for f in experiment.folders if f.id == fid), None)
        if folder:
            page_folder_view(folder)
        else:
            st.error("Folder not found - please select from the sidebar.")


if __name__ == "__main__":
    main()