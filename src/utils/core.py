import os
import json
import pandas as pd

from dotenv import load_dotenv
from selectolax.parser import HTMLParser
from trafilatura import extract

loaded = False

def load_environment():
    """
    Load the environment only once to avoid unnecessary page reloads

    Args:
        None
    
    Returns:
        None
    """
    global loaded
    if not loaded:
        load_dotenv()
        loaded = True

# CONFIGURATION
TASK_ID_COLUMN = os.getenv("TASK_ID_COLUMN", "_id")

WORKING_DIR = os.getenv('WORKING_DIR', 'data')
TASKS_FILE = os.getenv('TASKS_FILE', f'{WORKING_DIR}/tasks.csv')
ANNOTATIONS_DIR = os.getenv('ANNOTATIONS_DIR', f'{WORKING_DIR}/annotations')
SELECTOLAX_DIR = os.getenv('SELECTOLAX_DIR', f'{WORKING_DIR}/selectolax')
TRAFILATURA_DIR = os.getenv('TRAFILATURA_DIR', f'{WORKING_DIR}/trafilatura')
HTML_DIR = os.getenv('HTML_DIR', f'{WORKING_DIR}/html')

def init():
    """
    Initialize the local storage

    Args:
        None
    
    Returns:
        None
    """
    # create the tasks file if it doesn't exist
    try:
        with open(TASKS_FILE, 'x') as f:
            pass
    except FileExistsError:
        pass


def load_annotator_tasks(annotator_id: str ):
    """
    Load the tasks from the local storage for the given annotator

    Args:
        annotator_id (str): The id of the annotator.
    
    Returns:
        list[dict]: The tasks with the annotations made by the annotator.
    """
    tasks = pd.read_csv(TASKS_FILE)

    # add annotations (as json)
    tasks['annotations'] = tasks[TASK_ID_COLUMN].apply(load_annotations)

    # only show the annotator's annotations
    tasks['annotations'] = tasks['annotations'].apply(lambda x: x.get(annotator_id) if x is not None else None)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks

def load_tasks():
    """
    Load the tasks from the local storage (includes all annotations from all annotators)

    Args:
        None
    
    Returns:
        list[dict]: The tasks with all annotations from all annotators.
    """
    tasks = pd.read_csv(TASKS_FILE)

    # add annotations (as json)
    tasks['annotations'] = tasks[TASK_ID_COLUMN].apply(load_annotations)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks

def load_annotations(task_id: str):
    """
    Load the annotations for the task with the given id (all annotators)

    Args:
        task_id (str): The id of the task.
    
    Returns:
        dict | None: The annotations made by all annotators for the task. (may be None if no annotations exist)
    """
    try:
        # Read the content of the page
        path = f"{ANNOTATIONS_DIR}/{task_id}.json"
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    
def load_annotation(task_id: str, annotator_id: str):
    """
    Load the annotation for the task with the given id and annotator id

    Args:
        task_id (str): The id of the task.
        annotator_id (str): The id of the annotator.
    
    Returns:
        dict: The annotations made by the annotator for the task.
    """
    annotations = load_annotations(task_id)

    if annotations is not None:
        return annotations[annotator_id]
    else:
        return {
            'labels': [],
            'comment': ""
        }


def update_task_annotations(annotator_id: str, task: dict, labels: list[str], comment: str):
    """
    Update task annotations for a given annotator and task

    Args:
        annotator_id (str): The id of the annotator.
        task (dict): The task to update.
        labels (list[str]): The labels to add to the task.
        comment (str): The comment to add to the task.
    
    Returns:
        None
    """
    try:
        annotation = load_annotation(task.get(TASK_ID_COLUMN), annotator_id)
        
        # add the selected tags to the annotation
        annotation['labels'] = labels

        # add the comment to the annotation
        annotation['comment'] = comment

        save_annotation(task.get(TASK_ID_COLUMN), annotator_id, annotation)

    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)


def save_annotation(task_id: str, annotator_id: str, new_annotations: dict):
    """
    Save the annotations the annotator made for a given task

    Args:
        task_id (str): The id of the task.
        annotator_id (str): The id of the annotator.
        new_annotations (dict): The annotations made by the annotator.

    Returns:
        None
    """

    # Load the annotations
    annotations = load_annotations(task_id)

    # If the annotations file doesn't exist, create it
    if annotations is None:
        annotations = { annotator_id: new_annotations }
    else:
        # Update the annotations
        annotations[annotator_id] = new_annotations

    # Save the annotations
    with open(f"{ANNOTATIONS_DIR}/{task_id}.json", "w") as f:
        json.dump(annotations, f)

def download_annotations():
    """
    Download all annotations by all annotators for all tasks

    Args:
        None
    
    Returns:
        str: The CSV content such that a file can be downloaded
    """
    annotations = []

    tasks = load_tasks()

    for task in tasks:
        task_id = task.get(TASK_ID_COLUMN)
        task_annotations = load_annotations(task_id)

        if task_annotations is None:
            # empty annotations
            task_annotations = {
                'task_id': task_id,
            }
        else:
            # compose the annotations into a single row
            task_annotations_composite = {
                'task_id': task_id,
            }

            # for each annotator, add the labels and comment
            for annotator_id, annotation in task_annotations.items():
                task_annotations_composite[f'{annotator_id}_labels'] = annotation.get('labels')
                task_annotations_composite[f'{annotator_id}_comment'] = annotation.get('comment')
            
            # update the task annotations to be the composite
            task_annotations = task_annotations_composite

        # append the task annotations to the list of annotations
        annotations.append(task_annotations)

    # save to csv
    annotations = pd.DataFrame(annotations)
    return annotations.to_csv(index=False)

def get_page_content(id: str):
    """
    Get the content of the page with the given id

    Args:
        id (str): The id of the page.
    
    Returns:
        str: The html content of the page.
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

def extract_raw_text(id: str):
    """
    Extracts the text from an HTML document associated with a task (selectolax)
    
    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """

    # First check if there already is a parsed version in the selectolax directory
    try:
        # read the file content if it exists
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'r') as f:
            # return the content of the file
            return f.read()
    except FileNotFoundError:
        # get page content
        html_document = get_page_content(id)

        # if the page content is None, there is nothing to extract
        if html_document is None:
            return None
        
        tree = HTMLParser(html_document)

        # if the body is None, there is nothing to extract
        if tree.body is None:
            return None

        # Remove scripts and styles
        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()

        # Extract the text
        text = tree.body.text(separator='\n')

        # Save the parsed selectolax text to a file
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        # Return the extracted text
        return text

def extract_cleaned_text(id: str):
    """
    Extracts the text from an HTML document associated with a task and cleans it up (trafilatura)
    
    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """

    # First check if there already is a parsed version in the trafilatura directory
    try:
        # read the file content if it exists
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'r') as f:
            # return the content of the file
            return f.read()
    except FileNotFoundError:
        # read the html content
        html_document = get_page_content(id)
        
        # if the page content is None, there is nothing to extract
        if html_document is None:
            return None
        
        # extract the text
        text = extract(html_document)

        # if the text is None, there is nothing to save
        if text is None:
            return None

        # Save the parsed trafilatura text to a file
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        # Return the extracted text
        return text

def update_cleaned_text(id: str, text: str):
    """
    Update the cleaned text for the task with the given id

    Args:
        id (str): The id of the task.
        text (str): The cleaned text for the task.
    
    Returns:
        None
    """
    
    with open(f'{TRAFILATURA_DIR}/{id}.txt', 'w') as f:
        f.write(text)