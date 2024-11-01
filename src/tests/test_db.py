from utils.db import initialize_db, load_annotations
from utils.config import *
import os
import sqlite3
import json

load_environment('.env-test', force=True)
config = Config()

def test_initialize_db():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)
    
    # 1. Database doesn't exist: Should create the database and the annotations table
    initialize_db()
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'")
    assert c.fetchone() is not None
    conn.close()
    
    # 2. Database exists: Should not create the database and the annotations table
    initialize_db()
    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'")
    assert c.fetchone() is not None
    conn.close()

def test_load_annotations():
    # Test cases for load_annotations
    print("ANNOTATIONS_DB", config.ANNOTATIONS_DB)
    
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)
    
    # and initialize the database
    initialize_db()

    # 1. Preparation: Insert annotations into the database
    annotation_01 = {
            'labels': ['label_1', 'label_2'],
            'comment': "This is a comment.",
            'random_seed': 42,
            'random_order': False
        }
    annotation_02 = {
            'labels': ['label_2', 'label_3'],
            'comment': "This is another comment.",
            'random_seed': 24,
            'random_order': True
        }

    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute('''
        INSERT INTO annotations (task_id, annotator_id, annotations) VALUES
        ('0', 'annotator_1', NULL),
        ('1', 'annotator_1', ?),
        ('1', 'annotator_2', ?)
    ''', (
        json.dumps(annotation_01),
        json.dumps(annotation_02)
    ))

    # 2. No annotations for the task: Should return None
    assert load_annotations('0') == None
    
    # 3. Annotations for the task: Should return a dictionary with the annotator id as the key and the annotations as the value
    assert load_annotations('1') == {
        'annotator_1': annotation_01,
        'annotator_2': annotation_02
    }