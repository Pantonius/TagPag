from utils.db import initialize_db, load_annotations, load_annotation, save_annotation
from utils.config import *
import os
import sqlite3
import json

load_environment('.env-test', force=True)
config = Config()

def cleanup():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)

def test_initialize_db():
    # 0. Cleanup: Remove the database file, if it exists
    cleanup()
    
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

    # 3. Cleanup
    cleanup()

def test_save_annotation():
    # 0. Cleanup: Remove the databse file, if it exists
    cleanup()
    initialize_db()

    save_annotation("1", "annotator_1", {
        'labels': ['label_1', 'label_2'],
        'comment': "Comment"
    })

    conn = sqlite3.connect(config.ANNOTATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM annotations")
    assert c.fetchall() == [('1', 'annotator_1', '{"labels": ["label_1", "label_2"], "comment": "Comment"}')]
    conn.close()

    # Cleanup
    cleanup()

def test_load_annotations():
    # 0. Cleanup
    cleanup()
    
    # and initialize the database
    initialize_db()

    # 1. Preparation: Insert annotations into the database
    annotation_01 = {
        'labels': ['label_1', 'label_2'],
        'comment': 'This is a comment.',
        'random_seed': '42',
        'random_order': '1'
    }
    annotation_02 = {
        'labels': ['label_2', 'label_3'],
        'comment': 'This is another comment.',
        'random_seed': '43',
        'random_order': '1'
    }
    
    save_annotation('1', 'annotator_1', None)
    save_annotation('2', 'annotator_1', annotation_01)
    save_annotation('2', 'annotator_2', annotation_02)

    # 2. No visits for the task: Should return None
    result_01 = load_annotations('0')
    assert result_01 == None

    # 3. No annotations for the task: Should return a None annotation for annotator_1
    result_02 = load_annotations('1')
    assert len(result_02) == 1 # only one
    assert result_02['annotator_1'] == None # None annotation for annotator_1
    
    # 4. Annotations for the task: Should return a dictionary with the annotator id as the key and the annotations as the value
    result_03 = load_annotations('2')
    assert len(result_03) == 2 # two annotators

    assert result_03['annotator_1']['comment'] == annotation_01['comment']
    assert result_03['annotator_1']['labels'] == annotation_01['labels']
    assert result_03['annotator_1']['random_seed'] == annotation_01['random_seed']
    assert result_03['annotator_1']['random_order'] == annotation_01['random_order']

    assert result_03['annotator_2']['comment'] == annotation_02['comment']
    assert result_03['annotator_2']['labels'] == annotation_02['labels']
    assert result_03['annotator_2']['random_seed'] == annotation_02['random_seed']
    assert result_03['annotator_2']['random_order'] == annotation_02['random_order']

    # 5. Cleanup
    cleanup()

def test_load_annotation():
    # 0. Cleanup
    cleanup()
    
    # and initialize the database
    initialize_db()

    # 1. Preparation: Insert annotations into the database
    annotation_01 = {
        'labels': ['label_1', 'label_2'],
        'comment': "This is a comment.",
    }
    
    save_annotation('1', 'annotator', None)
    save_annotation('2', 'annotator', annotation_01)

    # 2. Never visited
    result_01 = load_annotation('0', 'annotator')
    assert result_01['comment'] == ''
    assert result_01['labels'] == []
    assert result_01['random_order'] == None
    assert result_01['random_seed'] == None 

    # 3. Visited, but no annotation
    result_02 = load_annotation('1', 'annotator')
    assert result_02 == None

    # 4. Annotation
    result_03 = load_annotation('2', 'annotator')
    assert result_03['comment'] == annotation_01['comment']
    assert result_03['labels'] == annotation_01['labels']

    # 5. Cleanup
    cleanup()