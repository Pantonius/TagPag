import streamlit as st
import os
import json
import shutil
import warnings

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
        try:
            # Use the ENV_FILE variable
            load_dotenv(ENV_FILE)
        except:
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

def get_env_set(var_name, default_value):
    """
    Retrieves an environment variable and returns its value as a set.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (set): The default value to return if the environment variable is not set or cannot be parsed.

    Returns:
        set: The value of the environment variable as a set, or the default value if an error occurs.

    Notes:
        The environment variable is expected to be a comma-separated list of values.
        If an error occurs while parsing the environment variable, a warning is raised and the default value is returned.
    """

    try:
        return set(os.getenv(var_name, "").split(","))
    except Exception as e:
        warnings.warn(f"Error parsing {var_name}: {e}. Using default value ({default_value}). See .env-example for more information.")
        return default_value

def get_env_dict(var_name, default_value):
    """
    Retrieves an environment variable and returns its value as a dictionary.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (dict): The default value to return if the environment variable is not set or cannot be parsed.

    Returns:
        dict: The value of the environment variable as a dictionary, or the default value if an error occurs.

    Notes:
        The environment variable is expected to be a JSON-formatted string.
        If an error occurs while parsing the environment variable, a warning is raised and the default value is returned.
    """

    try:
        return json.loads(os.getenv(var_name, "{}"))
    except json.JSONDecodeError as e:
        warnings.warn(f"Error parsing {var_name}: {e}. Using default value ({default_value}). See .env-example for more information.")
        return default_value
    except Exception as e:
        warnings.warn(f"Unexpected error parsing {var_name}: {e}. Using default value ({default_value}). See .env-example for more information.")
        return default_value


load_environment()

# Get the environment variables
ANNOTATOR = os.getenv("ANNOTATOR", "annotator_name")
RANDOM_SEED = int(os.getenv("RANDOM_SEED", '-1')) if os.getenv("RANDOM_SEED", 'None') != 'None' else -1

## clip the random seed to -1 if it is less than 0
RANDOM_SEED = RANDOM_SEED if RANDOM_SEED >= 0 else -1

TASKS_ID_COLUMN = os.getenv("TASKS_ID_COLUMN", '_id')
TASKS_URL_COLUMN = os.getenv("TASKS_URL_COLUMN", 'url')

# set the directories
WORKING_DIR = os.getenv('WORKING_DIR', 'data')
TASKS_FILE = join(WORKING_DIR, os.getenv('TASKS_FILE', 'tasks.csv'))
ANNOTATIONS_DB = join(WORKING_DIR, os.getenv('ANNOTATIONS_DB', 'annotations.sqlite'))
RAW_TEXT_DIR = join(WORKING_DIR, os.getenv('RAW_TEXT_DIR', 'raw_text'))
CLEANED_TEXT_DIR = join(WORKING_DIR, os.getenv('CLEANED_TEXT_DIR', 'cleaned_text'))
HTML_DIR = join(WORKING_DIR, os.getenv('HTML_DIR', 'html'))

# parse the labels for annotation
LABELS = os.getenv("LABELS", "").split(",")

# set the URL query parameters
URL_QUERY_PARAMS = get_env_set("URL_QUERY_PARAMS", set())
NOT_SEO_TITLES = get_env_set("NOT_SEO_TITLES", set())
COMMON_EXTENSIONS = get_env_set("COMMON_EXTENSIONS", set())
SPECIAL_CHARACTER_MAP = get_env_dict("SPECIAL_CHARACTER_MAP", {})

# making a global variable for the session state
STATE = st.session_state
