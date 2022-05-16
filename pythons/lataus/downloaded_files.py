import json

file_dir = "YOUR_PATH\\data\\raw_data\\error_log"
file_name = "progress_log_20220122-152355_full_4yr_download.txt"
json_name = "errored_files_full_4yr.json"

def add_key_if_not_exist(key, value, dictionary):
  if key not in dictionary:
    dictionary[key] = value

def append_to_list_or_create_list(key, value, dictionary):
  if key not in dictionary:
    dictionary[key] = [value]
  else:
    dictionary[key].append(value)

def handle_row(row, result_dict):
  split_row = row.split(" ")[-2].split("_")
  lam_id = split_row[1]
  year = split_row[2]
  day = split_row[3].split(".")[0]

  add_key_if_not_exist(year, {}, result_dict)
  append_to_list_or_create_list(day, lam_id, result_dict[year])

f = open(f"{file_dir}\\{file_name}", "r")

created_data = {}
for line in f:
  if len(line) > 0:
    handle_row(line, created_data)

f.close()

with open(json_name, 'w') as fp:
  json.dump(created_data, fp)