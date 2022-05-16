from os import walk
from os import listdir

import pandas as pd

class DataReader:
    data_path = ""
    
    def __init__(self, data_path):
        self.data_path = data_path
        
    def combine_dfs(self, lam_id):
        files = listdir(self.data_path)
        filtered = filter(lambda path: self.get_lam_id(path) == lam_id, files)
        dfs = []
        for path in filtered:
            dfs.append(pd.read_csv(self.data_path + path))
        return pd.concat(dfs)
        
    def get_lam_id(self, file_path):
        return file_path.split("_")[1]