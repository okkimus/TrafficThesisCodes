from PIL import Image
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join
from LamIndexer import LamIndexer

class ImageProcessor:
  def __init__(self, feature_name, base_path):
    self.feature_name = feature_name
    self.base_path = base_path
    self.lam_indexer = LamIndexer()

  def process_day(self, year, day):
    img_dir = f"{self.base_path}\\{year}\\{day}"
    img_files = [f for f in listdir(img_dir) if isfile(join(img_dir, f))]
    for img_name in img_files:
      if self.img_is_selected_feature(img_name):
        lam_ids, directions, data = self.process_img(f"{img_dir}\\{img_name}")
        continue
    return self.create_df(lam_ids, year, day, directions, data)

  def create_df(self, lam_ids, year, day, directions, data):
    data_count = len(lam_ids)
    years = [year for i in range(data_count)]
    days = [day for i in range(data_count)]
    return pd.DataFrame({
      "lamId": lam_ids,
      "year": years,
      "day": days,
      "direction": directions,
      self.feature_name: data
    })

  def img_is_selected_feature(self, img_name):
    return self.feature_name in img_name

  def process_img(self, path):
    img = Image.open(path)
    width, height = img.size

    lam_ids = []
    directions = []
    data = []

    img_bytes = img.tobytes()

    for i in range(width):
      is_empty = img_bytes[(height-2) * width + i] == 255
      if not is_empty:
          col = img_bytes[i:(height-2)*width:width]
          lam_id = self.lam_indexer.get_lam_id_for_index(i)
          direction = (i % 2) + 1
          lam_ids.append(lam_id)
          directions.append(direction)
          data.append(np.array(bytearray(col), dtype="uint8"))
    
    return (lam_ids, directions, data)
