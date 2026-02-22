import pandas as pd
import streamlit as st
import re


class ParquetReport():

    def __init__(self, name):
        
        self.name = name,
        self.data_loaded = False

    def get_name(self):

        return(self.name)

    def load_data(self, dataframe):

        self.dataframe = dataframe
        self.data_loaded = True


    def apply_regex(self, pattern: str):
        regex = re.compile(pattern)
        
        def extract(run):
            match =  re.match(regex, run)
            if match:
                return match.group()
            else:
                return None

        try:
            self.dataframe["Clean_ID"] = self.dataframe["Run"].apply(lambda x: extract(x))
            return True
        except:
            return False

class MetadataFile():

    def __init__(self, name):
        self.name = name,
        self.data_loaded = False

    def get_name(self):
        return(self.name)

    def load_data(self, dataframe):
        self.dataframe = dataframe
        self.data_loaded = True
