"""
Tab 1 — Raw Data QC
Plots covering the m/z, RT, and IM (if available) dimensions,
TIC at MS1/MS2, charge state distributions, and mass accuracy.
"""
import streamlit as st
from utils.plots import show_placeholder

_SECTIONS = {
    "Retention Time": [
        ("RT distribution (density per sample)", "rt_density"),
        ("RT range per sample (box/violin)", "rt_violin"),
        ("Peak width FWHM distribution", "rt_fwhm"),
    ],
    "m/z": [
        ("Precursor m/z distribution (density per sample)", "mz_precursor_density"),
        ("Fragment m/z distribution", "mz_fragment_density"),
        ("MS1 mass accuracy (Δm/z ppm)", "mz_ms1_accuracy"),
        ("MS2 mass accuracy (Δm/z ppm)", "mz_ms2_accuracy"),
    ],
    "Ion Mobility (diaPASEF only)": [
        ("IM distribution (observed vs predicted)", "im_obs_vs_pred"),
        ("2D density: RT × IM ion map", "im_rt_2d"),
        ("IM deviation (observed − predicted)", "im_deviation"),
    ],
    "Signal Intensity": [
        ("MS1 TIC per sample (summed)", "tic_ms1"),
        ("MS2 TIC per sample (summed)", "tic_ms2"),
        ("Precursor intensity distribution per sample", "intensity_dist"),
    ],
    "Identifications (raw)": [
        ("Charge state distribution per sample", "charge_dist"),
        ("Q-value / score distribution per sample", "qval_dist"),
        ("Missed cleavages distribution", "missed_cleavages"),
    ],
}

def render():
    if not st.session_state.get("data_loaded"):
        st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
        return

    has_im = st.session_state.get("has_im", False)

    st.markdown("## Raw Data QC")
    st.markdown(
        "Per-sample quality metrics across the retention time, m/z, "
        + ("ion mobility, " if has_im else "")
        + "and intensity dimensions."
    )

    for section, plots in _SECTIONS.items():
        # Skip IM section for standard DIA data
        if "Ion Mobility" in section and not has_im:
            continue

        with st.expander(f"**{section}**", expanded=True):
            # Pair plots side-by-side where there are ≥2
            pairs = [plots[i:i+2] for i in range(0, len(plots), 2)]
            for pair in pairs:
                cols = st.columns(len(pair))
                for col, (label, key) in zip(cols, pair):
                    with col:
                        st.caption(label)
                        show_placeholder(f"TODO: {key}")
