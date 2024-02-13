import os
import nbformat
import json
from common import *

SEMESTER_WEEKS = {}

def get_cell_ids(path):
  # Read the Jupyter notebook
  with open(path, "r") as f:
    notebook = nbformat.read(f, as_version=4)

  cell_ids = []
  h1 = 0
  h2 = 0
  a = 0
  # Iterate over the cells in the notebook
  for cell in notebook["cells"]:
    # Check if the cell is a markdown cell
    if cell["cell_type"] == "markdown":
      source = cell["source"]
      lines = source.splitlines()
      for line in lines:
        # only get h1
        if line.startswith("# "):
          h1 += 1
          h2 = 0
          a = 0
        if line.startswith("## "):
          h2 += 1
          a = 0

    # Check if the cell has a 'exercise' tag
    if 'exercise' in cell["metadata"]["tags"]:
      a += 1
      cell_ids.append({'cellId': cell["id"], 'position': f"{h1}.{h2}.{a}"})

  return cell_ids


def get_exercises():
  ids = {}
  for date in SEMESTER_WEEKS.values():
    try:
      entries = os.scandir(f"{NOTEBOOK_FOLDER}/{date}")
      notebook_files = list(
        filter(lambda e: e.is_file() and e.name.endswith(".ipynb"), entries))

      for n in notebook_files:
        # Assuming no two notebooks have the same name
        ids[n.name.split(".")[0]] = get_cell_ids(n.path)
    except:
      print(f"Folder {date} not found")

  return ids

def main():
    global SEMESTER_WEEKS
    SEMESTER_WEEKS = load_semester_json()
    ids = get_exercises()
    with open('feedback_ids.json', 'w') as f:
        json.dump(ids, f)


if __name__ == '__main__':
  main()

