import streamlit as st
import os
import json
from dotenv import load_dotenv
from os.path import join, dirname

# Load the environment variables
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

load_environment()

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

# Get the environment variables
TASK_ID_COLUMN = os.getenv("TASK_ID_COLUMN", "_id")
TASK_URL_COLUMN = os.getenv("TASK_URL_COLUMN", "target_url")

WORKING_DIR = os.getenv('WORKING_DIR', 'data')
TASKS_FILE = join(WORKING_DIR, os.getenv('TASKS_FILE', 'tasks.csv'))
ANNOTATIONS_DIR = join(WORKING_DIR, os.getenv('ANNOTATIONS_DIR', 'annotations'))
SELECTOLAX_DIR = join(WORKING_DIR, os.getenv('SELECTOLAX_DIR', 'selectolax'))
TRAFILATURA_DIR = join(WORKING_DIR, os.getenv('TRAFILATURA_DIR', 'trafilatura'))
HTML_DIR = join(WORKING_DIR, os.getenv('HTML_DIR', 'html'))

LABELS = os.getenv("LABELS", "").split(",")

TASKS = read_json_file("example_data.json")
STATE = st.session_state