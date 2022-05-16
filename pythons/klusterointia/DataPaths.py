from strenum import StrEnum

your_path = "PATH"

class Paths(StrEnum):
  raw_data_path = f"{your_path}\\data\\raw_data",
  processed_image_path = f"{your_path}\\data\\processed_image_files",
  processed_image_path_v2 = f"{your_path}\\data\\processed_image_files_v2",
  full_year_pickle_path = f"{your_path}\\data\\full_year_pickles",
  full_year_pickle_path_v2 = f"{your_path}\\data\\full_year_pickles_v2",
  aggregated_path = f"{your_path}\\data\\aggregated_data"
  mean_pickles = f"{your_path}\\data\\mean_pickles"
  model_path = f"{your_path}\\models"