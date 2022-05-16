from os import walk
from os import listdir

import os
import numpy as np
import pandas as pd

class DataProcessor:
    data_path = ""
    available_data = {}
    COLUMN_NAMES = ["pistetunnus", "vuosi", "päivän järjestysnumero", "tunti", "minuutti", "sekunti", "sadasosasekunti", "pituus (m)", "kaista", "suunta", "ajoneuvoluokka", "nopeus (km/h)", "faulty", "kokonaisaika ", "aikaväli ", "jonoalku "]
    CARGO_IDS = [2,4,5]
    CAR_IDS = [1,3,6,7]
    
    def __init__(self, data_path):
        self.data_path = data_path
        
    def read_available_data(self):
        available_years = self.filter_integers(listdir(self.data_path))
        data = {}
        
        for year in available_years:
            year_data = {}
            year_path = self.data_path + str(year)
            elys = listdir(year_path)
            for ely in elys:
                lam_files = listdir(year_path + "/" + ely)
                available_lams = set()
                for file in lam_files:
                    if file == ".ipynb_checkpoints": continue
                    available_lams.add(self.get_lam_id(file))
                year_data[ely] = available_lams
            data[year] = year_data
        self.available_data = data
        
    def process_data(self, save_path):
        paths = self.create_paths()
        for path in paths:
            file_name = path[path.rfind("/"):]
            if os.path.exists(save_path + "/" + file_name):
                print(f"{file_name} already exists")
            df = pd.read_csv(path, sep=";", names=self.COLUMN_NAMES)
            created = self.create_data_file(df, 5)
            self.save_df_to_csv(created, save_path + "/" + file_name)
        
        return True
    
    def save_df_to_csv(self, df, save_path):
        df.to_csv(save_path)
    
    def create_data_file(self, dataframe, interval_in_minutes):
        grouped, interval = self.divide_to_bins(dataframe, interval_in_minutes)
        lam_id = dataframe["pistetunnus"].min()
        year = dataframe["vuosi"].min()
        day = dataframe["päivän järjestysnumero"].min()
        direction = grouped["suunta"].max()
        cargo_group = self.get_vehicle_class_rows(grouped, self.CARGO_IDS)
        car_group = self.get_vehicle_class_rows(grouped, self.CAR_IDS)

        result = pd.DataFrame({
            "lamid": lam_id,
            "year": year,
            "day": day,
            "speed_cargo": self.speed_sum(cargo_group),
            "speed_car": self.speed_sum(car_group),
            "count_car": self.vehicle_count(car_group),
            "count_cargo": self.vehicle_count(cargo_group),
        }).reset_index()

        result = self.add_minute_index(result)
        result = result.rename(columns={"tunti": "hour", "suunta": "direction"})

        return result

    # Will return only the rows which are in intreset for now...
    def get_vehicle_class_rows(self, df, vehicle_classes):
        return df.apply(lambda x: x[x['ajoneuvoluokka'].isin(vehicle_classes)])[["nopeus (km/h)", "pituus (m)"]].groupby(["tunti", "minuutti", "suunta"])

    def add_minute_index(self, df):
        df["minuutti"] = df["minuutti"].apply(lambda x: x.right / 5 - 1).astype({"minuutti": int})
        df = df.rename(columns={"minuutti": "minute_index"})
        return df    

    def get_minute_indices(self, df):
        return pd.DataFrame(df).reset_index()[0].apply(lambda x: x[1].right / 5 - 1)

    def vehicle_count(self, df):
        return df.size()

    def speed_sum(self, df):
        return df['nopeus (km/h)'].sum()

    def minutes(self, df, interval):
        return (df["minuutti"].max() / interval - 1).round()

    def hours(self, df):
        return grouped_df["tunti"].min()

    def cargo_length(self, df):
        return df.apply(lambda x: x[x['ajoneuvoluokka'].isin([2,4,5])]['pituus (m)'].sum())
        
    def divide_to_bins(self, df, minute_interval):
        interval = np.arange(0, 61, minute_interval)
        cut = pd.cut(df["minuutti"], interval, include_lowest=True)
        grouped = df.groupby(["tunti", cut, "suunta"])
        return (grouped, interval)    
        
    def create_paths(self):
        paths = []
        years = self.available_data.keys()
        for year in years:
            elys = self.available_data[year].keys()
            for ely in elys:
                files = listdir(f"{self.data_path}{year}/{ely}/")
                for file in files:
                    if file != ".ipynb_checkpoints":
                        paths.append(f"{self.data_path}{year}/{ely}/{file}")
        return paths
    
    def get_lam_id(self, file_name):
        end_of_id = file_name.index("_", 7)
        return file_name[7:end_of_id]         
        
    def filter_integers(self, list_to_filter):
        list_of_numbers = []
        for el in list_to_filter:
            try:
                list_of_numbers.append(int(el))
            except ValueError:
                pass
        return list_of_numbers