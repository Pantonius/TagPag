import os
import json
import pandas as pd

from dotenv import load_dotenv
from selectolax.parser import HTMLParser
from trafilatura import extract

TASKS_FILE = 'data/tasks.csv' # TODO: Move this to .env (mayhaps)
ANNOTATIONS_DIR = 'data/annotations' # TODO: Move this to .env (mayhaps)
SELECTOLAX_DIR = 'data/selectolax' # TODO: Move this to .env (mayhaps)
TRAFILATURA_DIR = 'data/trafilatura' # TODO: Move this to .env (mayhaps)
HTML_DIR = 'data/html' # TODO: Move this to .env (mayhaps)

loaded = False

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

def load_environment():
    """
    Load the environment
    """
    global loaded
    if not loaded:
        load_dotenv()
        loaded = True


def loadTasks():
    """
    Load the tasks from the local storage
    """
    tasks = pd.read_csv(TASKS_FILE)

    # add annotations (as json)
    tasks['annotations'] = tasks['_id'].apply(loadAnnotations).apply(lambda x: x.to_json() if x is not None else None)
    # TODO: will not update upon new annotations

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


def update_task_annotations(annotator, task, labels, comment):
    """
    Update task annotations
    """
    try:
        annotation = loadAnnotation(task.get('_id'), annotator)

        if annotation is None:
            annotation = {
                'annotator_id': annotator,
                'labels': [],
                'comment': ""
            }
        
        # add the selected tags to the annotation
        annotation['labels'] = labels

        # add the comment to the annotation
        annotation['comment'] = comment

        save_annotation(task.get('_id'), annotator, annotation)

    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)


def save_annotation(task_id: str, annotator_id: str, new_annotations: dict):
    """
    Update the annotation for the task with the given id
    """

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

    tasks = loadTasks()

    for task in tasks:
        task_id = task.get('_id')
        task_annotations = loadAnnotations(task_id)

        if task_annotations is None:
            # empty annotations
            task_annotations = pd.DataFrame(columns=['annotator_id', 'comment', 'labels', 'task_id'], data=[{'annotator_id': None, 'comment': None, 'labels': None, 'task_id': task_id}])
        else:
            task_annotations['task_id'] = task_id
        
        annotations.append(task_annotations)

    # to csv
    annotations = pd.concat(annotations, ignore_index=True)
    return annotations.to_csv(index=False)

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


def read_json_file(file_path: str) -> dict:
    """
    Read and parse a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the file specified by `file_path` is not found.
        json.JSONDecodeError: If there is an error decoding the JSON data.
        Exception: If any other error occurs while reading the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Error: Failed to decode JSON in file '{file_path}'.")
    except Exception as e:
        raise Exception(f"Error: An error occurred while reading the JSON file: {str(e)}")

def extractText(id: str):
    """Extracts the actual text from an HTML document associated with a task (selectolax)"""

    # First check if there already is a parsed version in the selectolax directory
    try:
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # get page content
        html_document = getPageContent(id)

        if html_document is None:
            return None
        
        tree = HTMLParser(html_document)

        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()

        text = tree.body.text(separator='\n')

        # Save the parsed version
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        return text

def extractTextTrafilatura(id: str):
    """Extracts the actual text from an HTML document associated with a task (trafilatura)"""

    # First check if there already is a parsed version in the trafilatura directory
    try:
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        html_document = getPageContent(id)
        
        if html_document is None:
            return None
        
        text = extract(html_document)

        if text is None:
            return None

        # Save the parsed version
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        return text