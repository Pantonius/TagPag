import streamlit as st
import os
import json
import shutil
import warnings

from dotenv import load_dotenv
from os.path import join

# Define the Config class to store the configuration settings
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_dict: dict = None):
        self.set_config(config_dict)
    
    def set_config(self, config_dict: dict) -> None:
        """
        Set the configuration settings from a dictionary.

        Args:
            config_dict (dict): The configuration settings as a dictionary.

        Returns:
            None
        """
        if not config_dict: # If no config_dict is provided, return the current instance
            return self

        self.ANNOTATOR = config_dict.get("ANNOTATOR", "annotator_name")
        self.RANDOM_SEED = config_dict.get("RANDOM_SEED", -1)
        self.TASKS_ID_COLUMN = config_dict.get("TASKS_ID_COLUMN", '_id')
        self.TASKS_URL_COLUMN = config_dict.get("TASKS_URL_COLUMN", 'url')
        self.WORKING_DIR = config_dict.get("WORKING_DIR", 'example_workdir')
        self.TASKS_FILE = config_dict.get('TASKS_FILE', join(self.WORKING_DIR, 'tasks.csv'))
        self.ANNOTATIONS_DB = config_dict.get('ANNOTATIONS_DB', join(self.WORKING_DIR, 'annotations.sqlite'))
        self.RAW_TEXT_DIR = config_dict.get('RAW_TEXT_DIR', join(self.WORKING_DIR, 'raw_text'))
        self.CLEANED_TEXT_DIR = config_dict.get('CLEANED_TEXT_DIR', join(self.WORKING_DIR, 'cleaned_text'))
        self.HTML_DIR = config_dict.get('HTML_DIR', join(self.WORKING_DIR, 'html'))
        self.LABELS = config_dict.get("LABELS", [])
        self.URL_QUERY_PARAMS = get_env_set("URL_QUERY_PARAMS", set())
        self.NOT_SEO_TITLES = get_env_set("NOT_SEO_TITLES", set())
        self.COMMON_EXTENSIONS = get_env_set("COMMON_EXTENSIONS", set())
        self.SPECIAL_CHARACTER_MAP = get_env_dict("SPECIAL_CHARACTER_MAP", {})
    

# Load the environment variables
loaded = False
def load_environment(file_path: str = '.env', force: bool = False) -> Config:
    """
    Loads the environment variables once from the given .env file, unless forced, such that there are no unnecessary page reloads.


    Args:
        file_path (str): The path to the environment file (default: '.env')
        force (bool): Force the environment to be loaded again (default: False)
    
    Returns:
        Config: The configuration settings as a Config object.
    """
    global loaded
    if not loaded or force: # only load the environment once, unless forced
        if not os.path.exists(file_path):
            # If the file is not found, copy the .env-example file to .env
            shutil.copyfile('.env-example', '.env')
            file_path = '.env'

        # Load the environment from the given .env file
        load_dotenv(dotenv_path=file_path, override=True)

        loaded = True
    
    return load_environment_variables()

def load_environment_variables():
    """
    Load the environment variables from os.environ and return them as a dictionary.

    Args:
        None
    
    Returns:
        None
    """
    # TODO: It maybe desirable to move this to the Config class, but I find that seperating this from the Config class leaves the possability
    # of setting the Config fields via additional methods, without having to modify the Config class itself.
    # For instance, someone may add a Streamlit Page which allows researchers to set the Config fields via a GUI.
    # So we'll keep it like this for now.

    working_dir = os.getenv('WORKING_DIR', 'example_workdir')
    random_seed = os.getenv('RANDOM_SEED', '-1')
    
    try:
        random_seed = int(random_seed)
    except ValueError:
        random_seed = -1

    config_dict = {
        "ANNOTATOR": os.getenv("ANNOTATOR", "annotator_name"),
        "RANDOM_SEED": random_seed,
        "TASKS_ID_COLUMN": os.getenv("TASKS_ID_COLUMN", '_id'),
        "TASKS_URL_COLUMN": os.getenv("TASKS_URL_COLUMN", 'url'),
        "WORKING_DIR": working_dir,
        "TASKS_FILE": join(working_dir, os.getenv('TASKS_FILE', 'tasks.csv')),
        "ANNOTATIONS_DB": join(working_dir, os.getenv('ANNOTATIONS_DB', 'annotations.sqlite')),
        "RAW_TEXT_DIR": join(working_dir, os.getenv('RAW_TEXT_DIR', 'raw_text')),
        "CLEANED_TEXT_DIR": join(working_dir, os.getenv('CLEANED_TEXT_DIR', 'cleaned_text')),
        "HTML_DIR": join(working_dir, os.getenv('HTML_DIR', 'html')),
        "LABELS": os.getenv("LABELS", "").split(","),
        "URL_QUERY_PARAMS": get_env_set("URL_QUERY_PARAMS", set()),
        "NOT_SEO_TITLES": get_env_set("NOT_SEO_TITLES", set()),
        "COMMON_EXTENSIONS": get_env_set("COMMON_EXTENSIONS", set()),
        "SPECIAL_CHARACTER_MAP": get_env_dict("SPECIAL_CHARACTER_MAP", {})
    }

    return Config(config_dict)

   
def create_directories():
    """
    Create the directories for the data if they don't exist.

    Args:
        None

    Returns:
        None
    """
    config = Config()

    for directory in [config.RAW_TEXT_DIR, config.CLEANED_TEXT_DIR]:
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

STATE = st.session_state