import streamlit as st
import pandas as pd
from utils.datahandler import ParquetReport, MetadataFile
from utils.session import init_session_state


_SECTIONS = {
	# "Retention Time": [
	# 	("RT distribution (density per sample)", "rt_density"),
	# 	("RT range per sample (box/violin)", "rt_violin"),
	# 	("Peak width FWHM distribution", "rt_fwhm"),
	# ],
	# "m/z": [
	# 	("Precursor m/z distribution (density per sample)", "mz_precursor_density"),
	# 	("Fragment m/z distribution", "mz_fragment_density"),
	# 	("MS1 mass accuracy (Δm/z ppm)", "mz_ms1_accuracy"),
	# 	("MS2 mass accuracy (Δm/z ppm)", "mz_ms2_accuracy"),
	# ],
	# "Ion Mobility (diaPASEF only)": [
	# 	("IM distribution (observed vs predicted)", "im_obs_vs_pred"),
	# 	("2D density: RT × IM ion map", "im_rt_2d"),
	# 	("IM deviation (observed − predicted)", "im_deviation"),
	# ],
	# "Signal Intensity": [
	# 	("MS1 TIC per sample (summed)", "tic_ms1"),
	# 	("MS2 TIC per sample (summed)", "tic_ms2"),
	# 	("Precursor intensity distribution per sample", "intensity_dist"),
	# ],
	"Identifications (raw)": [
		("Charge state distribution per sample", "charge_dist"),
		("Q-value / score distribution per sample", "qval_dist"),
		("Missed cleavages distribution", "missed_cleavages"),
		("Missed cleavages distribution (dataset wide)", "missed_cleavages_dataset_wide")
	],
}


def is_valid():

	if (st.session_state.get("report") is not None):
		if (st.session_state.get("report").data_loaded):
			return True

	else:
		return False

def render():

	if is_valid():

		report = st.session_state.get("report")

		st.markdown("## Raw Data QC")
		st.markdown(
			"Per-sample quality metrics across the retention time, m/z, "
			+ ("ion mobility, " if st.session_state["report"].is_timstof else "")
			+ "and intensity dimensions."
		)

		st.code(report.columns)

		for section, plots in _SECTIONS.items():
			# Skip IM section for standard DIA data
			if "Ion Mobility" in section and not st.session_state["report"].is_timstof:
				continue

			with st.expander(f"**{section}**", expanded=True):
				# Pair plots side-by-side where there are ≥2
				pairs = [plots[i:i+2] for i in range(0, len(plots), 2)]
				for pair in pairs:
					cols = st.columns(len(pair))
					for col, (label, key) in zip(cols, pair):
						with col:
							st.caption(label)
							st.plotly_chart(st.session_state.get("report").get_plot(key), key=key)
							



	else:
		st.info("⬅️  Load your data on the **Upload & Configure** tab first.")
		return


