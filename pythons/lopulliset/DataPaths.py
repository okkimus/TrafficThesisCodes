from strenum import StrEnum

class Paths(StrEnum):
  raw_data_path = "YOUR_PATH\\data\\raw_data",
  processed_image_path = "YOUR_PATH\\data\\processed_image_files",
  processed_image_path_v2 = "YOUR_PATH\\data\\processed_image_files_v2",
  processed_image_path_v3 = "YOUR_PATH\\data\\processed_image_files_v3",
  full_year_pickle_path = "YOUR_PATH\\data\\full_year_pickles",
  full_year_pickle_path_v2 = "YOUR_PATH\\data\\full_year_pickles_v2",
  full_year_pickle_path_v3 = "YOUR_PATH\\data\\full_year_pickles_v3",
  aggregated_path = "YOUR_PATH\\data\\aggregated_data"
  mean_pickles = "YOUR_PATH\\data\\mean_pickles"
  mean_pickles_v2 = "YOUR_PATH\\data\\mean_pickles_v2"
  model_path = "YOUR_PATH\\models"