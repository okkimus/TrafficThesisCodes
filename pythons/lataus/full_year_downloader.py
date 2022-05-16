from downloader import download
from calendar import monthrange
from datetime import datetime
import threading
import queue
import os
import concurrent
import json
import requests

ely_codes = ['01', '02', '03', '04', '08', '09', '10', '12', '14']
with open('../elyjenmappaus/ely_lamid_mapping.json', 'r') as mappings:
  lam_id_mapping = json.loads(mappings.read())

def create_file_name(lam_id, year, day_number):
  year_short = year % 100
  return f"lamraw_{lam_id}_{year_short}_{day_number}.csv"

def first_and_last_day_number(month, year):
  first_day = datetime(year, month, 1)
  last_day = datetime(year, month, monthrange(year, month)[1])
  
  first = first_day.timetuple().tm_yday
  last = last_day.timetuple().tm_yday
  
  return (first, last)

def create_download_parameters_for_months(lam_id, year, months, ely_code, path):
  parameters = []
  for month in months:
    first_day, last_day = first_and_last_day_number(month, year)

    for day_number in range(first_day, last_day + 1):
      parameters.append((year, ely_code, create_file_name(lam_id, year, day_number), path))    
  
  
  return parameters

def find_ely(lam_id):
  for key in lam_id_mapping.keys():
    if int(lam_id) in lam_id_mapping[key]:
        return key
  return -1

def append_to_key_value(dictionary, key, value):
  if key in dictionary:
    dictionary[key].append(value)
  else:
    dictionary[key] = [value]
        
def add_missing_dict(dictionary, key):
  if key not in dictionary:
    dictionary[key] = {}

def create_errored_json(errored):
  errored_dict = {}
  for msg in errored:
    filename = msg.split(" ")[-1]
    lam_id = filename.split("_")[1]
    day = filename.split("_")[-1].split(".")[0]
    ely = find_ely(lam_id)
    add_missing_dict(errored_dict, ely)
    append_to_key_value(errored_dict[ely], lam_id, day)
      
  return 
  
def save_json(json_data, filename):
  with open(filename, 'w') as fp:
    json.dump(json_data, fp, sort_keys=True)


def download_full_year(year, data_save_path, error_save_path):
  parameters = []
  selected_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  selected_year = year

  # create params for each ELY code and it's LAM
  for ely in ely_codes:
    lams = lam_id_mapping[ely.strip("0")]
    for lam in lams:
      parameters = parameters + create_download_parameters_for_months(lam, selected_year, selected_months, ely, data_save_path)
  
  failed_and_existed = download(parameters)
  print(f"Failed count: {len(failed_and_existed[0])}")
  errored_json = create_errored_json(failed_and_existed[0])
  save_json(errored_json, f"{error_save_path}\\errored_file_downloads_{selected_year}_1-12.json")

  error_len = 0
  for key in errored_json.keys():
    for lam_key in errored_json[key]:
      error_len += len(errored_json[key][lam_key])
          
  print(f"{error_len} file downloads failed")

def download_lam_data(year, ely, file_name, destination):
    url = f"https://aineistot.vayla.fi/lam/rawdata/{year:d}/{ely}/{file_name}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        file_name = os.path.join(destination, f'{year:d}\\{ely}\\{file_name}')
        create_dir_if_missing(file_name)
        if os.path.exists(file_name):
            return f"{file_name} already exists"
        else:    
            with open(file_name, 'wb') as f:
                f.write(response.content)
            return f"{file_name} OK"
    else:
        return f"Invalid response code: {response.status_code} for {file_name}"
    
def create_dir_if_missing(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
def download(download_args_list):
    errored = []
    existed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_tuple = {executor.submit(download_lam_data, *args_list): args_list for args_list in download_args_list}
        for future in concurrent.futures.as_completed(future_to_tuple):
            year, day, tms_station = future_to_tuple[future]
            try:
                status = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % ((year, day, tms_station), exc))
            else:
                if status[:7] == "Invalid":
                    errored.append(status)
                if status[-14:] == "already exists":
                    existed.append(status)
                
    return (errored, existed)