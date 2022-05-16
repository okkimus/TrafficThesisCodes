from tkinter import Image
from ImageProcessor import ImageProcessor
from calendar import isleap
import pandas as pd

class DataFramer:
  def __init__(self, data_path, pickle_path):
    self.data_path = data_path
    self.pickle_path = pickle_path

  def pickle_year(self, year, feature):
    df = self.frame_year(year, feature)

    pickle_name = f"full_year_{year}_{feature}.pkl"
    df.to_pickle(f"{self.pickle_path}\\{pickle_name}")

    return True

  def pickle_year_with_common_lams(self, year, feature, lams):
    df = self.frame_year(year, feature)
    df = df[df["lamId"].isin(lams["commonLams"])]
    pickle_name = f"full_year_commonlams_{year}_{feature}.pkl"
    df.to_pickle(f"{self.pickle_path}\\{pickle_name}")

    return True

  def frame_year(self, year, feature):
    day_count = 366 if isleap(year) else 365
    processor = ImageProcessor(feature, self.data_path)
    dataframes = []

    for day in range(1, day_count + 1):
      day_df = processor.process_day(year, day)
      dataframes.append(day_df)
    
    return pd.concat(dataframes)