import numpy as np
import pandas as pd

from datetime import datetime

class MeanMaker:
  def __init__(self):
    pass

  def create_means_from_monday(self, ith_monday:int, from_month:int, year:int, week_count:int, data:pd.DataFrame, feature_name:str):
    start = self.get_first_weekday_of_month(year, from_month, 0, ith_monday)
    data[feature_name] = data[feature_name].apply(lambda x: x.astype(int))

    weeks = []
    for i in range(week_count):
      days = []
      for j in range(7):
        days.append(start + i * 7 + j)
      weeks.append(days)

    # Filter the data by days
    # Group by lam ids and directions
    
    all_weeks_data = pd.DataFrame()

    for week in weeks:
      print(week)
      week_data = data[data["day"].isin(week)].reset_index()
      unfull_weeks_removed = week_data.groupby(["lamId", "direction"]).filter(lambda x: len(x) == 7)
      # Concat all the data into one
      sorted_week = unfull_weeks_removed.sort_values("day").groupby(["lamId", "direction"])
      week_data_concated = sorted_week.agg({feature_name: lambda data: np.concatenate([d for d in data])})
      all_weeks_data = pd.concat([all_weeks_data, week_data_concated])

    lams_with_all_weeks = all_weeks_data.groupby(["lamId", "direction"]).filter(lambda x: len(x) == week_count)
    grouped = lams_with_all_weeks.groupby(["lamId", "direction"])
    meaned_data = grouped[feature_name].mean().reset_index()
    meaned_data.insert(1, 'year', year)
    meaned_data.insert(2, 'startDay', start)
    meaned_data.insert(3, 'weeksInMean', week_count)

    return meaned_data

  def get_first_weekday_of_month(self, year:int, month:int, weekday:int, ith_weekday:int):
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    time_delta = 0
    if weekday < first_weekday:
      time_delta = 7 - first_weekday + weekday
    elif weekday > first_weekday:
      time_delta = weekday - first_weekday

    day_index = first_day.timetuple().tm_yday
    result = day_index + time_delta + 7 * (ith_weekday-1)

    return result