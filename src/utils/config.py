import streamlit as st
import os
import json
import shutil
from dotenv import load_dotenv
from os.path import join

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
        # if .env does not exist, load 
        if not os.path.exists('.env'):
            # copy .env-example to .env using shutil
            shutil.copyfile('.env-example', '.env')

        load_dotenv()
        loaded = True


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
    
def create_directories():
    """
    Create the directories for the data if they don't exist.

    Args:
        None

    Returns:
        None
    """
    for directory in [RAW_TEXT_DIR, CLEANED_TEXT_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)


load_environment()

# Get the environment variables
TASKS_ID_COLUMN = os.getenv("TASKS_ID_COLUMN", '_id')
TASKS_URL_COLUMN = os.getenv("TASKS_URL_COLUMN", 'url')

WORKING_DIR = os.getenv('WORKING_DIR', 'data')
TASKS_FILE = join(WORKING_DIR, os.getenv('TASKS_FILE', 'tasks.csv'))
ANNOTATIONS_DB = join(WORKING_DIR, os.getenv('ANNOTATIONS_DB', 'annotations.sqlite'))
RAW_TEXT_DIR = join(WORKING_DIR, os.getenv('RAW_TEXT_DIR', 'raw_text'))
CLEANED_TEXT_DIR = join(WORKING_DIR, os.getenv('CLEANED_TEXT_DIR', 'cleaned_text'))
HTML_DIR = join(WORKING_DIR, os.getenv('HTML_DIR', 'html'))

LABELS = os.getenv("LABELS", "").split(",")

STATE = st.session_state