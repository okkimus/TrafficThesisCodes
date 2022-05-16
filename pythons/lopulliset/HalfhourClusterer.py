from DatasetReader import DatasetReader
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

import pandas as pd
import numpy as np

class HalfhourClusterer:


  def __init__(self, data_or_path, low_traffic_filter):
    dr = DatasetReader()
    scaler = TimeSeriesScalerMeanVariance()
    if (isinstance(data_or_path, pd.DataFrame)):
      self.data = data_or_path
    else:
      self.data = dr.read_pickle(data_or_path)
    self.halfhour_data = self.data.CarCount.apply(lambda x: np.sum(x.reshape(-1, 6), axis=1))
    self.halfhour_dataset = to_time_series_dataset(self.halfhour_data)
    self.halfhour_data_scaled = scaler.fit_transform(self.halfhour_dataset)
    self.halfhour_small_removed = to_time_series_dataset(self.halfhour_data[self.halfhour_data.apply(lambda x: x.max() > low_traffic_filter)].reset_index()["CarCount"])
    self.halfhour_data_scaled_small_removed = scaler.fit_transform(self.halfhour_small_removed)

  def train(self, cluster_count, scaled, include_small):
    dataset = self.get_dataset(scaled, include_small)

    model = TimeSeriesKMeans(cluster_count, n_jobs=6, metric="dtw", random_state=1, metric_params={"global_constraint":"sakoe_chiba", "sakoe_chiba_radius":5})
    model.fit(dataset)
    return model

  def predict(self, model, scaled, include_small):
    dataset = self.get_dataset(scaled, include_small)
    preds = model.predict(dataset)
    return preds

  # def print_prediction_stats(self, preds):
  #   class_counts = Counter(preds)

  def get_dataset(self, scaled, include_small):
    if scaled:
      if include_small:
        dataset = self.halfhour_data_scaled
      else:
        dataset = self.halfhour_data_scaled_small_removed
    else:
      if include_small:
        dataset = self.halfhour_dataset
      else:
        dataset = self.halfhour_small_removed
    return dataset