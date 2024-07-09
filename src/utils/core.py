import os
import json
import re
import pandas as pd

from utils.config import *
from selectolax.parser import HTMLParser
from trafilatura import extract

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


def reduce_line_breaks(text):
    """
    Reduce multiple line breaks to a single line break
    
    Args:
        text (str): The text to reduce line breaks in
        
    Returns:
        str: The text with reduced line breaks
    """
    
    # Use regular expression to replace multiple line breaks with a single line break
    return re.sub(r'\n\s*\n+', '\n', text.strip())

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
    tasks['annotations'] = tasks[TASKS_ID_COLUMN].apply(load_annotations)

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
    tasks['annotations'] = tasks[TASKS_ID_COLUMN].apply(load_annotations)

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
        annotation = load_annotation(task.get(TASKS_ID_COLUMN), annotator_id)
        
        # add the selected tags to the annotation
        annotation['labels'] = labels

        # add the comment to the annotation
        annotation['comment'] = comment

        save_annotation(task.get(TASKS_ID_COLUMN), annotator_id, annotation)

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
        task_id = task.get(TASKS_ID_COLUMN)
        task_annotations = load_annotations(task_id)

        url = task.get(TASKS_URL_COLUMN)

        if task_annotations is None:
            # empty annotations
            task_annotations = {
                'task_id': task_id,
            }
        else:
            # compose the annotations into a single row
            task_annotations_composite = {
                'task_id': task_id
            }

            # for each annotator, add the labels and comment
            for annotator_id, annotation in task_annotations.items():
                labels = None
                comment = ""

                if annotation is not None:
                    labels = annotation.get('labels')
                    comment = annotation.get('comment')

                if labels == []:
                    labels = None

                task_annotations_composite[f'{annotator_id}_labels'] = labels
                task_annotations_composite[f'{annotator_id}_comment'] = comment
            
            # update the task annotations to be the composite
            task_annotations = task_annotations_composite

        # url should be the last column
        task_annotations['url'] = url

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
        with open(f'{RAW_TEXT_DIR}/{id}.txt', 'r') as f:
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
        text = reduce_line_breaks(tree.body.text(separator='\n'))

        # Save the parsed selectolax text to a file
        with open(f'{RAW_TEXT_DIR}/{id}.txt', 'w') as f:
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
        with open(f'{CLEANED_TEXT_DIR}/{id}.txt', 'r') as f:
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
        with open(f'{CLEANED_TEXT_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        # Return the extracted text
        return text

def update_cleaned_text(task_id: str, text: str):
    """
    Update the cleaned text for the task with the given id

    Args:
        id (str): The id of the task.
        text (str): The cleaned text for the task.
    
    Returns:
        None
    """
    
    with open(f'{CLEANED_TEXT_DIR}/{task_id}.txt', 'w') as f:
        f.write(text)