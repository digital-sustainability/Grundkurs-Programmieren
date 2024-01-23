import nbformat
import os
import json
import re
import shutil
import argparse

from nbgrader.apps import NbGraderAPI
from traitlets.config import Config

SEMESTER_WEEKS = {}

NOTEBOOK_FOLDER = "notebooks"
RELEASE_FOLDER = "release"
WEEK_IDENTIFIER = "WEEK_"


def load_semester_json():
  global SEMESTER_WEEKS
  try:
    SEMESTER_WEEKS = json.loads(os.environ['SEMESTER_WEEKS'])
  except:
    print("Error while loading SEMESTER_WEEKS")
    print("Check the Pipeline configuration")
    exit(1)


def replace_last_occurrence(text, old, new):
  """
    Replaces the last occurrence of a substring in a string.
    """
  split_text = text.rsplit(old, 1)
  return new.join(split_text)


def generate_assignments(folders):
  c = Config()
  #c.CourseDirectory.root = '/home/jovyan/work/unterlagen'
  c.CourseDirectory.source_directory = NOTEBOOK_FOLDER
  c.ClearSolutions.code_stub = {
    "python": "# YOUR CODE HERE",
  }
  api = NbGraderAPI(config=c)
  for dir in folders:
    res = api.generate_assignment(dir)
    if res['success'] == False:
      print(f"Something went wrong with {dir} :/")
      print(res['log'])
      # Abort further execution
      exit(1)


def generate_toc():
  """
  Generates a table of content
  """

  HEADER = """
  <img src="https://i.imgur.com/XSzy00d.png" style="float:right;width:150px">
  
  **Inhaltsverzeichnis**
  """

  toc = nbformat.v4.new_notebook()
  toc['cells'] = [nbformat.v4.new_markdown_cell(HEADER)]

  # Specify the kernel for the notebook
  kernelspec = {
      'display_name': 'Python 3',
      'language': 'python',
      'name': 'python3'
  }
  toc['metadata']['kernelspec'] = kernelspec

  for date in SEMESTER_WEEKS.values():
    try:
      entries = os.scandir(f"{RELEASE_FOLDER}/{date}")
      notebook_files = list(
        filter(lambda e: e.is_file() and e.name.endswith(".ipynb"), entries))

      # TODO: Check that len(notebook_files) == 1
      for n in notebook_files:
        with open(n.path, "r") as f:
          notebook = nbformat.read(f, as_version=4)

        # extract name from file name
        name = n.name.replace(".ipynb", "")
        name = replace_last_occurrence(name, "_", " und ")
        if "_" in name:
          name = name.replace("_", ", ")

        content = f"- [{name}]({date}/{n.name})\n"
        headings = []
        cells = filter(lambda c: c["cell_type"] == "markdown",
                       notebook["cells"])
        for cell in cells:
          source = cell["source"]
          lines = source.splitlines()
          for line in lines:
            # only get h1
            if line.startswith("# "):
              text = line.strip().strip("# ").strip().replace("*", "")
              headings.append(text)

        for heading in headings:
          link = f"{date}/{n.name}" + "#" + heading.replace(" ", "-")
          result = f"  - [{heading}]({link})\n"
          content += result

        toc['cells'].append(nbformat.v4.new_markdown_cell(content))
    except:
      print(f"Folder {date} not found")

  nbformat.write(toc, f"{RELEASE_FOLDER}/Inhaltsverzeichnis.ipynb")


def set_exercise_tag(path):
  # Read the Jupyter notebook
  with open(path, "r") as f:
    notebook = nbformat.read(f, as_version=4)

  # Iterate over the cells in the notebook
  for cell in notebook["cells"]:
    # Check if the cell is a code cell
    if cell["cell_type"] == "code":
      # Check if the string "# YOUR CODE HERE" is in the source
      if '# YOUR CODE HERE' in cell["source"]:
        # Get the existing tags or an empty list if there are no tags
        tags = cell["metadata"].get("tags", [])
        # Append the tag "exercise" to the existing tags
        tags.append("exercise")
        # Update the tags in the metadata of the cell
        cell["metadata"]["tags"] = tags

  # Write the modified notebook to a file
  with open(path, "w") as f:
    nbformat.write(notebook, f)

def replace_links(path):
  with open(path, "r") as f:
    notebook = nbformat.read(f, as_version=4)

  cells = notebook["cells"]

  REGEX = fr"\/(?P<week>{WEEK_IDENTIFIER}\d{{1,2}})\/"
  cells = filter(lambda c: c["cell_type"] == "markdown", notebook["cells"])
  for cell in cells:
    source = cell["source"]
    lines = source.splitlines()
    for index, line in enumerate(lines):
      offset = 0
      # NOTE: we assume that WEEK_IDENTIFIER may only be used for links
      match = re.search(REGEX, line)
      while match != None:
        week = match.group('week')
        _, end = match.span()

        line = line.replace(week, SEMESTER_WEEKS[week])
        offset += end
        # Check for next occurence
        match = re.search(REGEX, line[offset:])
      lines[index] = line
    cell["source"] = "\n".join(lines)

  with open(path, "w") as f:
    nbformat.write(notebook, f)


def modify_assignments(assignment_folders):
  for a in assignment_folders:
    try:
      entries = os.scandir(f"{RELEASE_FOLDER}/{a}")
      notebook_files = list(
        filter(lambda e: e.is_file() and e.name.endswith(".ipynb"), entries))
      for n in notebook_files:
        replace_links(n.path)
        set_exercise_tag(n.path)
    except:
      print(f"Folder {a} not found")


def move_assignment_folders(assignment_folders):
  for a in assignment_folders:
    semester_date = SEMESTER_WEEKS[a]
    try:
      shutil.move(f"{RELEASE_FOLDER}/{a}", f"{RELEASE_FOLDER}/{semester_date}")
    except:
      print(f"Could not move {a} folder")


def get_assignment_folders():
  return list(SEMESTER_WEEKS.keys())

def main():
  parser = argparse.ArgumentParser(description="A CLI tool that accepts a directory argument.")
  parser.add_argument("-d", "--directory", help="Path to the directory", type=str, required=False)

  args = parser.parse_args()
  load_semester_json()
  print(SEMESTER_WEEKS)


  # Check if the provided path is a directory
  if os.path.isdir(f"{NOTEBOOK_FOLDER}/{args.directory}"):
    print(f"{args.directory} is a valid directory.")
    folders = [args.directory]
  else:
    print(f"{args.directory} is not a valid directory.")
    folders = get_assignment_folders()

  generate_assignments(folders)
  modify_assignments(folders)
  move_assignment_folders(folders)
  generate_toc()



if __name__ == '__main__':
  main()

