from os import walk
import pandas as pd

class DatasetReader:
  def read_directories(self, path):
    files = []
    directories = []
    full_path = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
        directories.extend(dirnames)
        full_path.extend([f"{dirpath}\\{fn}" for fn in filenames])
        break
    return DirContents(directories, files, full_path)

  def read_pickle(self, path):
    df = pd.read_pickle(path)
    return df

class DirContents:
  def __init__(self, directories, files, full_file_paths):
    self.directories = directories
    self.files = files
    self.full_file_paths = full_file_paths

  def __str__(self):
    return f"Directories: {self.directories}\nFiles: {self.files}\nFull file paths: {self.full_file_paths}"

  def __repr__(self):
    return f"Directories: {self.directories}\nFiles: {self.files}\nFull file paths: {self.full_file_paths}"
