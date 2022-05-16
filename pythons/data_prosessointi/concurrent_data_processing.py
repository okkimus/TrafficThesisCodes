from processor_new import Processor 
import concurrent.futures

import numpy as np
import pandas as pd

from os import walk
from os import listdir
import datetime
import time


processor = Processor()

def main():
    raw_data_path = "../lataus/data/lam"
    years = listdir(raw_data_path)
    print(f"Available years {', '.join(years)}.")

    selected_year = "2016"
    elys = listdir(f"{raw_data_path}/{selected_year}")
    print(f"Available elys {', '.join(elys)}.")

    selected_ely = "01"

    lam_data_files = listdir(f"{raw_data_path}/{selected_year}/{selected_ely}")
    lam_ids = set()

    for filename in lam_data_files:
        lam_ids.add(filename.split("_")[-1].split(".")[0])

    print(f"Available lam ids {', '.join(sorted(lam_ids))}.")

    selected_lam = "1"

    files = []

    for filename in lam_data_files:
        if filename.split("_")[1] == selected_lam:
            files.append(filename)

    print(f"{len(files)} file(s) found for lam id {selected_lam}.")

    data_path = f"{raw_data_path}/{selected_year}"
    day_1_files = []

    for ely in elys:
        files = listdir(f"{data_path}/{ely}")
        for file in files:
            if file.split("_")[-1].split(".")[0] == "1":
                day_1_files.append(f"{data_path}/{ely}/{file}")

    

    start = time.time()

    result = np.zeros((288, 1))
    i = 0
    start_time = datetime.datetime.now().time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        for path, cols in zip(day_1_files, executor.map(create_columns, day_1_files)):
            i += 1
            if i % 10 == 0:
                print(f"{i} files done")
            result = np.concatenate((result, cols), axis=1)

    done = time.time()
    elapsed = done - start
    print(elapsed)


def create_columns(path):
    processor_object = Processor()
    result = processor.create_columns(processor_object.process_file_in_path(path, 5), processor_object.PROCESSED_COL_NAMES[-1])
    return result
            
if __name__ == '__main__':
    main()