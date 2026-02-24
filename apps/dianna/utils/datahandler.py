import pandas as pd
import streamlit as st
import re
import warnings
import plotly.express as pe
from .helpers import analyze_missed_cleavages

class ParquetReport():

    """Representation of the Parquet report output by DIA-NN"""

    def __init__(self, name):
        
        self.name = name,
        self.data_loaded = False
        self.data_id_mapped = False

    def load_data(self, dataframe):

        self.dataframe = dataframe
        self.data_loaded = True
        self.columns = self.dataframe.columns

        self.is_timstof = {"IM", "iIM", "Predicted.IM", "Predicted.iIM"}.issubset(set(self.columns))



    def apply_regex(self, pattern: str):

        """Apply regex over the Run column to create a new 'Identifier' column"""

        regex = re.compile(pattern)
        
        def extract(s):
            """Small driver to extract regex patterns over the Run column"""
            
            m =  re.search(regex, s)

            if m:
                return m.group(1)
            else:
                warnings.warn("At least one Run string didn't match the provided pattern.")
                return "No match"

        try:
            self.dataframe["Identifier"] = self.dataframe["Run"].map(lambda x: extract(x))
            self.data_id_mapped = True
            return True
        
        except Exception as e:
            print(e)
            return False

    def calc_sidebar_stats(self):

        """Calculates minimal stats used in the sidebar. Any stats shown in the sidebar should be calculated here."""
        
        self.n_samples = self.dataframe.Identifier.nunique()
        self.n_pgs = self.dataframe["Protein.Group"].nunique()
        self.n_precursors = self.dataframe["Precursor.Id"].nunique()



    def get_plot(self, key: str):
        """Maps a key to a plotting function. Always returns a plot."""

        df = self.dataframe


        if key == "charge_dist":

            precursor_charge_data = (
                    df
                    .groupby(["Identifier", "Precursor.Charge"])
                    .size()
                    .reset_index(name="counts")
                )

            precursor_charge_data["Percent of Precursors"] = (
                    precursor_charge_data["counts"] /
                    precursor_charge_data.groupby("Identifier")["counts"].transform("sum")
            ) * 100

            precursor_charge_data["Precursor.Charge"] = precursor_charge_data["Precursor.Charge"].apply(lambda x: str(x))

            plot = pe.bar(precursor_charge_data, x = "Identifier", y="Percent of Precursors", color = "Precursor.Charge", title = "Precursor Charge State Distribution")

            return plot

        elif key == "qval_dist":
                        
            plot = pe.violin(
                df, x="Identifier", y="Q.Value",height = 800,
                title = "Q.Value Distribution Per Sample"
            )

            return plot

        elif key == "missed_cleavages":
            
            mc = analyze_missed_cleavages(self.dataframe)["by_identifier"]
            plot = pe.bar(mc, x="Identifier", y="percent", color="mc_label")
            return(plot)

        elif key == "missed_cleavages_dataset_wide":
            mc_dataset_wide = analyze_missed_cleavages(self.dataframe)["by_missed_cleavages"]
            plot = pe.bar(mc_dataset_wide, x = "mc_label", y = "percent", color = "mc_label")
            return(plot)

        else:
            raise ValueError("Not a plot key.")




class MetadataFile():

    def __init__(self, name):
        self.name = name,
        self.data_loaded = False

    def load_data(self, dataframe):
        self.dataframe = dataframe
        self.data_loaded = True
        self.cols = self.dataframe.columns
