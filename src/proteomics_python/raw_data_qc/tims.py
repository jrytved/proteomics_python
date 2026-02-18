import pandas as pandas
import alphatims.bruker
import re
from pathlib import Path

def extract_tic_data(
	tims_folder_path: str,
	output_path: str,
	re_pattern: str = 'AL000028_S_([A-z]\\d)'
):

	"""

	Extracts TIC-data (retention time, summed intensities at MS1-level) for all Bruker-TIMS (.d) files in a specified folder. 
	Saves the TIC-data as .csv.

	:param str tims_folder_path: a path to the folder containing only Bruker-TIMS (.d) files.
	:param str re_pattern: a regex pattern to extract a unique identifier from the path to the (.d) files. Usually a sample id.
	:param output_path: a path to the folder where the .csv files are output to.

	"""

	p = Path(tims_folder_path)
	full_paths = [f for f in p.iterdir()]

	for path in full_paths:
		id = re.search(re_pattern, tims_folder_path).group(1)
		data = alphatims.bruker.TimsTOF(tims_folder_path)
		tic_data = data.frames.query('MsMsType == 0')[['Time', 'SummedIntensities']]

		filename = f"{id}.csv"
		out_path = Path(output_path, filename)

		tic_data.to_csv(out_path)

		del bruker_data
		del tic_data

def extract_ion_chromatogram(
    paths: list[str],
    mz_low: float,
    mz_high: float,
    output_path: str,
    pattern: str = r'AL000028_S_([A-Za-z]\d)',
):
    """
    Extracts an ion chromatogram from the files given in path.
    Uses the passed regex pattern to name files and dataframe ID column.
    """
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in paths:
        path = Path(path)  # normalize to Path

        match = re.search(pattern, path.name)
        if not match:
            raise ValueError(f"Pattern {pattern!r} not found in {path}")
        sample_id = match.group(1)

        # alphatims requires a string path so conv. from Path obj. b4 passing
        data = alphatims.bruker.TimsTOF(str(path))
        data_subset = data[:, :, 0, mz_low:mz_high, :]

        out_file = out_dir / f"{sample_id}_{mz_low}_{mz_high}.csv"
        data_subset.to_csv(out_file)

        del data
        del data_subset





