import os
import pandas as pd

TASKS_FILE = 'data/tasks.csv' # TODO: Move this to .env (mayhaps)
ANNOTATIONS_DIR = 'data/annotations' # TODO: Move this to .env (mayhaps)
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

def loadTasks():
    """
    Load the tasks from the local storage
    """
    tasks = pd.read_csv(TASKS_FILE)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks

def loadAnnotations(task_id: str):
    """
    Load the annotations for the task with the given id
    """
    try:
        # Read the content of the page
        path = f"{ANNOTATIONS_DIR}/{task_id}.json"
        with open(path, "r") as f:
            return pd.read_json(f)
    except FileNotFoundError:
        return None
    
def loadAnnotation(task_id: str, annotator_id: str):
    """
    Load the annotation for the task with the given id and annotator id
    """
    annotations = loadAnnotations(task_id)

    if annotations is not None:
        return annotations[annotations['annotator_id'] == annotator_id].iloc[0]
    else:
        return None

def updateTask(task_id: str, annotator_id: str, new_annotations: dict):
    """
    Update the annotation for the task with the given id
    """
    print(f"Updating task {task_id} with annotations {new_annotations}")

    # Load the annotations
    annotations = loadAnnotations(task_id)

    # If the annotations file doesn't exist, create it
    if annotations is None:
        annotations = pd.DataFrame(columns=['annotator_id', 'comment', 'labels'])
    
    # Update the annotations
    annotations = annotations[annotations['annotator_id'] != annotator_id]
    annotations = pd.concat([annotations, pd.DataFrame([{'annotator_id': annotator_id, **new_annotations}])])

    # TODO: doesn't quite save it in the expected format -- also the new_annotations aren't really new

    # Save the annotations
    annotations.to_json(f"{ANNOTATIONS_DIR}/{task_id}.json")

def downloadAnnotations():
    """
    Download the annotations for all tasks
    """
    annotations = []

    for file in os.listdir(ANNOTATIONS_DIR):
        task_id = file.split('.')[0]
        task_annotations = loadAnnotations(task_id)

        if task_annotations is None:
            continue
        
        task_annotations['task_id'] = task_id
        
        annotations.append(task_annotations)
    
    # to csv
    annotations = pd.concat(annotations)
    return annotations.to_csv(index=False)\

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
    