import pandas as pandasimport alphatims.bruker
import re
from pathlib import Path

def extract_tic_data(tims_folder_path, output_path, re_pattern = 'AL000028_S_([A-z]\\d)'):

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
		id = re.search(re_pattern, path).group(1)
		data = alphatims.bruker.TimsTOF(path)
		tic_data = data.frames.query('MsMsType == 0')[['Time', 'SummedIntensities']]

		filename = f"{id}.csv"
		out_path = Path(output_path, filename)

		tic_data.to_csv(out_path)

		del bruker_data
		del tic_data






