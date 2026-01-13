import pandas as pd, numpy as np
import pyopenms as oms

def build_spectrum_from_mzmine_txt(path, sep = "\t"):

    spectrum = oms.MSSpectrum()
    data =  pd.read_csv(path, sep = sep)

    peaks = data["m/z"].to_list()
    intensities = data["Intensity"].to_list()
    n_peaks = len(peaks)

    spectrum.set_peaks([peaks, intensities])

    return spectrum
