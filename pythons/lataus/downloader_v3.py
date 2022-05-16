import concurrent.futures
from io import TextIOWrapper
import os
import queue
import requests
import threading
import time
import json

from FileExistChecker import FileHandledChecker

class Downloader:
  def __init__(self, download_destination, error_file_destination, progress_file_destination, exists_file_destination) -> None:
    self.download_destination = download_destination
    self.error_file_destination = error_file_destination
    self.progress_file_destination = progress_file_destination
    self.exists_file_destination = exists_file_destination
    self.done_queue = queue.Queue()
    self.existed_queue = queue.Queue()
    self.error_queue = queue.Queue()
    self.skipped_queue = queue.Queue()

    self.download_on = False

    self.file_handled_checker = FileHandledChecker()

  def download_lam_data(self, year, ely, file_name, destination):
    if self.file_handled_checker.is_handled(file_name):
      self.skipped_queue.put(1)
      return None

    url = f"https://aineistot.vayla.fi/lam/rawdata/{year:d}/{ely}/{file_name}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
      file_name = os.path.join(destination, f'{year:d}\\{ely}\\{file_name}')
      with open(file_name, 'wb') as f:
        f.write(response.content)
      return f"{file_name} OK"
    else:
      return f"Invalid response code: {response.status_code} for {file_name}"
    
  def download(self, download_args_list, file_identifier=""):
    # Setup file appending threads
    fwt = FileWritterThread(
      self.done_queue, self.progress_file_destination, 
      self.error_queue, self.error_file_destination, 
      self.existed_queue, self.exists_file_destination, 
      self.skipped_queue, file_identifier)
    fwt.start()

    print("Starting downloaders")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
      future_to_tuple = {executor.submit(self.download_lam_data, *args_list): args_list for args_list in download_args_list}
      for future in concurrent.futures.as_completed(future_to_tuple):
        year, ely, filename, destination = future_to_tuple[future]

        try:
          status = future.result()
          if status == None:
            pass
          elif status[-2:] == "OK":
            self.done_queue.put(status)
          elif status[:7] == "Invalid":
            self.error_queue.put(status)
        except Exception as exc:
          print('%r generated an exception: %s' % ((year, ely, filename), exc))
            
    while self.done_queue.qsize() + self.existed_queue.qsize() + self.error_queue.qsize() > 0:
      print(f"Writing still going... {(self.done_queue.qsize(), self.existed_queue.qsize(), self.error_queue.qsize())}")
      time.sleep(2)
    
    fwt.set_tasks_left(False)

    return True

class FileWritterThread(threading.Thread):
  def __init__(self, doneq, donef, errorq, errorf, existq, existf, skippedq, file_identifier):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    print("Creating FileWritterThread")
    threading.Thread.__init__(self)
    self.done_queue = doneq
    self.error_queue = errorq
    self.existed_queue = existq
    self.skippedq = skippedq
    self.done_file = open(f"{donef}_{timestamp}_{file_identifier}.txt", "a")
    self.error_file = open(f"{errorf}_{timestamp}_{file_identifier}.txt", "a")
    self.existed_file = open(f"{existf}_{timestamp}_{file_identifier}.txt", "a")
    self.rows_written = 0
    self.tasks_left = True

  def write_to_open_file(self, message, file:TextIOWrapper):
    file.write(f"{message} \n")
    self.rows_written += 1

  def save_and_reopen(self, file:TextIOWrapper):
    name = file.name
    file.close()
    return open(name, 'a')

  def save_files_and_resume(self):
    self.done_file = self.save_and_reopen(self.done_file)
    self.existed_file = self.save_and_reopen(self.existed_file)
    self.error_file = self.save_and_reopen(self.error_file)
    print("Saved files and reopened them")

  def write_if_in_queue(self, queue, file):
    if queue.qsize() > 0:
      item = queue.get()
      if item == None:
        print("Item not found")
      self.write_to_open_file(item, file)
      queue.task_done()

  def close_files(self):
    print("Closing files")
    self.done_file.close()
    self.existed_file.close()
    self.error_file.close()

  def set_tasks_left(self, setting):
    self.tasks_left = setting
    if setting == False:
      self.close_files()

  def run(self):
    print("Starting FileWritterThread")
    report_threshold = 1000
    try:
      while self.tasks_left:
        if self.done_queue.qsize() + self.existed_queue.qsize() + self.error_queue.qsize() == 0:
          print("Waiting for items to write")
          time.sleep(10)
          print(f"File downloads skipped so far: {self.skippedq.qsize()}")
          print(f"Queued rows: Done -> {self.done_queue.qsize()}, Existed -> {self.existed_queue.qsize()}, Errored -> {self.error_queue.qsize()}")
        if self.rows_written > report_threshold:
          report_threshold += 1000
          print(f"Done writing {self.rows_written} rows")
          self.save_files_and_resume()
        self.write_if_in_queue(self.done_queue, self.done_file)
        self.write_if_in_queue(self.error_queue, self.error_file)
        self.write_if_in_queue(self.existed_queue, self.existed_file)
    except Exception as e: print(e)