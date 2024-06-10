import pandas as pd

TASKS_FILE = 'data/tasks.csv' # TODO: Move this to .env (mayhaps)
ANNOTATIONS_FILE = 'data/annotations.csv' # TODO: Move this to .env (mayhaps)
HTML_DIR = 'data/html' # TODO: Move this to .env (mayhaps)

def init():
    """
    Initialize the local storage
    """
    # create the tasks file if it doesn't exist
    try:
        with open(TASKS_FILE, 'x') as f:
            pass
    except FileExistsError:
        pass

    # create the annotations file if it doesn't exist
    try:
        with open(ANNOTATIONS_FILE, 'x') as f:
            pass
    except FileExistsError:
        pass

def loadTasks():
    """
    Load the tasks from the local storage
    """
    tasks = pd.read_csv(TASKS_FILE)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks

def loadAnnotations():
    """
    Load the annotations from the local storage
    """
    annotations = pd.read_csv(ANNOTATIONS_FILE)

    # turn into dict
    annotations = annotations.to_dict(orient='records')

    return annotations

def countAnnotations():
    """
    Count the number of annotations in the local storage
    """
    annotations = pd.read_csv(ANNOTATIONS_FILE)

    return len(annotations)

def updateTask(task_id: str, annotator_id: str, new_annotations: dict):
    """
    Update the annotation for the task with the given id
    """
    annotations = pd.read_csv(ANNOTATIONS_FILE)

    # Update the annotations
    annotations.loc[annotations["_id"] == task_id, ["annotations"]] = str({annotator_id: new_annotations})

    # Save the annotations
    annotations.to_csv(ANNOTATIONS_FILE, index=False)

def getPageContent(id: str):
    """
    Get the content of the page with the given id
    """
    try:
        # Read the content of the page
        with open(f"{HTML_DIR}/{id}.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
    