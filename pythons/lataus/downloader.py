import concurrent.futures
import os
import requests

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