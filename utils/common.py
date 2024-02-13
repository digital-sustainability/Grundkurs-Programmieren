import json
import os

NOTEBOOK_FOLDER = "notebooks"
RELEASE_FOLDER = "release"
WEEK_IDENTIFIER = "WEEK_"
EXERCISE_IDENTIFIER = "exercise"


def load_semester_json():
    try:
        return json.loads(os.environ['SEMESTER_WEEKS'])
    except:
        print("Error while loading SEMESTER_WEEKS")
        print("Check the Pipeline configuration")
        exit(1)


def get_assignment_folders(semester_weeks):
    return list(semester_weeks.keys())
