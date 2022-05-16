import numpy as np
import pandas as pd

class Processor:
    COLUMN_NAMES = ["pistetunnus", "vuosi", "päivän järjestysnumero", "tunti", "minuutti", "sekunti", "sadasosasekunti", "pituus (m)", "kaista", "suunta", "ajoneuvoluokka", "nopeus (km/h)", "faulty", "kokonaisaika", "aikaväli", "jonoalku"]
    CARGO_IDS = [2,4,5]
    CAR_IDS = [1,3,6]
    PROCESSED_COL_NAMES = ["time_index", "direction", "cargo_min_v", "cargo_max_v", "cargo_mean_v", "cargo_count", "car_min_v", "car_max_v", "car_mean_v", "car_count"]  
    
    def process_file_in_path(self, path, interval_in_minutes):
        df = pd.read_csv(path, sep=";", names=self.COLUMN_NAMES)
        df["time_index"] = df["tunti"] * 60 + df["minuutti"]
        df = df.drop(["tunti", "minuutti", "sekunti", "sadasosasekunti", "kokonaisaika", "aikaväli", "jonoalku", "kaista"], axis=1)
        bin_defs = self.create_bin_definition(interval_in_minutes)
        ind = np.digitize(df["time_index"], bin_defs)
        
        processed_rows = []
        ind_set = set(ind)
        
        for bin_index in range(1, len(bin_defs) + 1):
            # Process the bin
            if bin_index in ind_set:
                processed = self.process_data(df.loc[ind == bin_index], bin_index)
                processed_rows.append(processed[0])
                processed_rows.append(processed[1])
            else:
                processed_rows.append([bin_index, 1, 0, 0, 0, 0, 0, 0, 0, 0])
                processed_rows.append([bin_index, 2, 0, 0, 0, 0, 0, 0, 0, 0])
    
        processed_np = np.array(processed_rows)
        
        speed_cols = ["cargo_min_v", "cargo_max_v", "cargo_mean_v", "car_min_v", "car_max_v", "car_mean_v"]
        min_speed = 20
        max_speed = 140

        # removing too high or low values
        for col in speed_cols:
            processed_np = self.preprocess_col(processed_np, min_speed, max_speed, col)
        
        # scaling speed values to the range [0, 256]
        processed_np[:, 2:5] = processed_np[:, 2:5] / (max_speed - min_speed) * 256
        processed_np[:, 7:10] = processed_np[:, 7:10] / (max_speed - min_speed) * 256
        
        return processed_np
        
    def create_bin_definition(self, minute_interval):
        return np.arange(0, 24 * 60, minute_interval)
    
    def process_data(self, data, i):
        direction_1 = data.loc[data["suunta"] == 1]
        direction_2 = data.loc[data["suunta"] == 2]

        cargo_cols_1 = self.process_car_type(direction_1, self.CARGO_IDS)
        car_cols_1 = self.process_car_type(direction_1, self.CAR_IDS)
        cargo_cols_2 = self.process_car_type(direction_2, self.CARGO_IDS)
        car_cols_2 = self.process_car_type(direction_2, self.CAR_IDS)

        return ([i, 1] + cargo_cols_1 + car_cols_1, [i, 2] + cargo_cols_2 + car_cols_2)

    def process_car_type(self, data, car_types):
        car_type_data = data[data['ajoneuvoluokka'].isin(car_types)]
        speeds = self.calculate_speed_data(car_type_data["nopeus (km/h)"])
        count = len(car_type_data)

        return speeds + [count]

    def calculate_speed_data(self, speed_col):
        if len(speed_col) == 0:
            return [0, 0, 0]
        max_v = speed_col.max()
        min_v = speed_col.min()
        mean_v = round(speed_col.mean())
        return [max_v, min_v, mean_v]
    
    def preprocess_col(self, a, min_value, max_value, col_name):
        col_index = self.PROCESSED_COL_NAMES.index(col_name)
        a[a[:, col_index] >= max_value, col_index] = max_value
        a[a[:, col_index] < min_value, col_index] = min_value
        a[:, col_index] = a[:, col_index] - min_value
        return a
    
    def create_columns(self, a, column_name):  
        col_index = self.PROCESSED_COL_NAMES.index(column_name)

        dir_1 = a[a[:, 1] == 1]
        dir_2 = a[a[:, 1] == 2]
        col_1 = dir_1[:, col_index]
        col_2 = dir_2[:, col_index]

        result = np.column_stack((col_1, col_2))

        return result