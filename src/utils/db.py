import sqlite3
import json
from utils.config import *

config = Config()

def initialize_db():
    """Initialize the SQLite database and create the annotations table if it doesn't exist."""
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS annotations (
            task_id TEXT NOT NULL,
            annotator_id TEXT NOT NULL,
            annotations TEXT,
            PRIMARY KEY (task_id, annotator_id)
        )
    ''')
    conn.commit()
    conn.close()

def load_annotations(task_id: str):
    """
    Load the annotations for the task with the given id (all annotators).

    Args:
        task_id (str): The id of the task.
    
    Returns:
        dict | None: The annotations made by all annotators for the task. (may be None if no annotations exist)
    """
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute('SELECT annotator_id, annotations FROM annotations WHERE task_id = ?', (task_id,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None
    
    annotations = {}
    for annotator_id, annotation_json in rows:
        annotations[annotator_id] = json.loads(annotation_json)
    
    return annotations


def load_annotation(task_id: str, annotator_id: str):
    """
    Load the annotation for the task with the given id and annotator id.

    Args:
        task_id (str): The id of the task.
        annotator_id (str): The id of the annotator.
    
    Returns:
        dict: The annotations made by the annotator for the task.
    """
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute('SELECT annotations FROM annotations WHERE task_id = ? AND annotator_id = ?', (task_id, annotator_id))
    row = c.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    else:
        return {
            'labels': [],
            'comment': "",
            'random_seed': None,
            'task_order': None
        }

def save_annotation(task_id: str, annotator_id: str, new_annotations: dict):
    """
    Save the annotations the annotator made for a given task.

    Args:
        task_id (str): The id of the task.
        annotator_id (str): The id of the annotator.
        new_annotations (dict): The annotations made by the annotator.

    Returns:
        None
    """
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()

    annotations_json = json.dumps(new_annotations)

    # Upsert the annotations
    c.execute('''
        INSERT INTO annotations (task_id, annotator_id, annotations)
        VALUES (?, ?, ?)
        ON CONFLICT(task_id, annotator_id) 
        DO UPDATE SET annotations=excluded.annotations
    ''', (task_id, annotator_id, annotations_json))

    conn.commit()
    conn.close()