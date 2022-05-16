import concurrent.futures
from io import TextIOWrapper
import os
import queue
import requests
import threading
import time
import json

class FileHandledChecker:
  def __init__(self) -> None:
    self.existed_lookup = {}
    self.errored_lookup = {}
    self.already_downloaded_lookup = {}
    with open("downloaded_files_full_4yr.json") as f:
      self.existed_lookup = json.load(f)
    with open("errored_files_full_4yr.json") as f:
      self.errored_lookup = json.load(f)
    with open("downloaded_files_full_4yr.json") as f:
      self.already_downloaded_lookup = json.load(f)

  def check_if_exists(self, year, day, lam_id):
    try:
      return lam_id in self.existed_lookup[year][day]
    except:
      return False

  def check_if_errored(self, year, day, lam_id):
    try:
      return lam_id in self.errored_lookup[year][day]
    except:
      return False

  def check_if_already_downloaded(self, year, day, lam_id):
    try:
      return lam_id in self.already_downloaded_lookup[year][day]
    except:
      return False

  def extract_params_from_filename(self, file_name):
      split_f = file_name.split("_")
      lam_id = split_f[1]
      year = split_f[2]
      day = split_f[3].split(".")[0]
      return year, day, lam_id

  def is_handled(self, filename):
    yr_short, day, lam_id = self.extract_params_from_filename(filename)
    if self.check_if_already_downloaded(yr_short, day, lam_id):
      return True
    if self.check_if_exists(yr_short, day, lam_id):
      return True
    if self.check_if_errored(yr_short, day, lam_id):
      return True
    return False