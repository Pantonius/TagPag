from utils.db import initialize_db, load_annotations
import os
import sqlite3
import json

global ENV_FILE
ENV_FILE = '.env-test'

from utils.config import *


def test_initialize_db():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(ANNOTATIONS_DB):
        os.remove(ANNOTATIONS_DB)
    
    # 1. Database doesn't exist: Should create the database and the annotations table
    initialize_db()
    conn = sqlite3.connect(ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'")
    assert c.fetchone() is not None
    conn.close()
    
    # 2. Database exists: Should not create the database and the annotations table
    initialize_db()
    conn = sqlite3.connect(ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'")
    assert c.fetchone() is not None
    conn.close()

def test_load_annotations():
    # Test cases for load_annotations
    
    # 0. Preparation: Insert annotations into the database
    conn = sqlite3.connect(ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute('''
        INSERT INTO annotations (task_id, annotator_id, annotations) VALUES
        ('0', 'annotator_1', NULL),
        ('1', 'annotator_1', ?),
        ('1', 'annotator_2', ?)
    ''', (
        json.dumps({
            'labels': ['label_1', 'label_2'],
            'comment': "This is a comment.",
            'random_seed': 42,
            'random_order': False
        }),
        json.dumps({
            'labels': ['label_2', 'label_3'],
            'comment': "This is another comment.",
            'random_seed': 24,
            'random_order': True
        })
    ))

    # 1. No annotations for the task: Should return None
    assert load_annotations('0') == None
    
    # 2. Annotations for the task: Should return a dictionary with the annotator id as the key and the annotations as the value
    assert load_annotations('1') == {
        'annotator_1': {
            'labels': ['label_1', 'label_2'],
            'comment': "This is a comment.",
            'random_seed': 42,
            'random_order': False
        },
        'annotator_2': {
            'labels': ['label_2', 'label_3'],
            'comment': "This is another comment.",
            'random_seed': 24,
            'random_order': True
        }
    }