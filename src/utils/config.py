import streamlit as st
import os
import json
import shutil
import streamlit as st

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
        self.URL_QUERY_PARAMS = config_dict.get("URL_QUERY_PARAMS", set())
        self.NOT_SEO_TITLES = config_dict.get("NOT_SEO_TITLES", set())
        self.COMMON_EXTENSIONS = config_dict.get("COMMON_EXTENSIONS", set())
        self.SPECIAL_CHARACTER_MAP = config_dict.get("SPECIAL_CHARACTER_MAP", {})
    

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

    working_dir = validate_path('WORKING_DIR', 'example_workdir')
    tasks_file = validate_path('TASKS_FILE', 'tasks.csv', working_dir)

    config_dict = {
        "ANNOTATOR": validate_string("ANNOTATOR", "annotator_name"),
        "RANDOM_SEED": validate_random_seed(),
        "WORKING_DIR": working_dir,
        "TASKS_FILE": tasks_file,
        "TASKS_ID_COLUMN": validate_csv_column("TASKS_ID_COLUMN", '_id', tasks_file),
        "TASKS_URL_COLUMN": validate_csv_column("TASKS_URL_COLUMN", 'url', tasks_file),
        "ANNOTATIONS_DB": join(working_dir, validate_string('ANNOTATIONS_DB', 'annotations.sqlite')),
        "RAW_TEXT_DIR": join(working_dir, validate_string('RAW_TEXT_DIR', 'raw_text')),
        "CLEANED_TEXT_DIR": join(working_dir, validate_string('CLEANED_TEXT_DIR', 'cleaned_text')),
        "HTML_DIR": validate_path('HTML_DIR', 'html', working_dir),
        "LABELS": validate_list("LABELS", ""),
        "URL_QUERY_PARAMS": validate_set("URL_QUERY_PARAMS", set()),
        "NOT_SEO_TITLES": validate_set("NOT_SEO_TITLES", set()),
        "COMMON_EXTENSIONS": validate_set("COMMON_EXTENSIONS", set()),
        "SPECIAL_CHARACTER_MAP": validate_dict("SPECIAL_CHARACTER_MAP", {})
    }

    return Config(config_dict)

def validate_string(variable: str, default_value: str) -> str:
    """
    Validate the environment variable as a string.

    Args:
        variable (str): The environment variable to validate.
        default_value (str): The default value to return if the environment variable is not set.

    Returns:
        str: The value of the environment variable, or the default value if the environment variable is not set.
    """
    value = os.getenv(variable, default_value)

    # check if the value is a string
    if not isinstance(value, str):
        raise ValueError(f"{variable} must be a string. Check the configuration file.")
    
    return value


def validate_path(variable: str, default_value: str, parent_dir: str = None) -> str:
    """
    Validate the environment variable as a existing path.

    Args:
        variable (str): The environment variable to validate.
        default_value (str): The default value to return if the environment variable is not set.
        parent_dir (str): The parent directory of the path (default: None).
    
    Returns:
        str: The path if it exists.
    """

    path = validate_string(variable, default_value)

    if parent_dir:
        path = join(parent_dir, path)
    
    if not os.path.exists(path):
        raise ValueError(f"{variable} does not exist ({path}). Check the configuration file.")
    
    return path


def validate_parent_directory(variable: str, directory: str) -> str:
    """
    Validate the parent directory of the environment variable.

    Args:
        variable (str): The environment variable to validate.
        directory (str): The directory to validate.
    
    Returns:
        str: The directory if it exists.
    """

    try:
        parent_dir = os.path.dirname(directory)
        if not os.path.exists(parent_dir):
            raise ValueError(f"{variable} parent directory does not exist ({parent_dir}). Check the configuration file.")
    except Exception as e:
        raise ValueError(f"Error validating {variable} parent directory: {e}")
    
    return directory

def validate_random_seed():
    """
    Validate the random seed environment variable.

    Args:
        None

    Returns:
        None

    Raises:
        ValueError: If the random seed is not a positive integer or 'None'.
    """
    random_seed = os.getenv('RANDOM_SEED', 'None')

    if random_seed == 'None':
        random_seed = -1
    else:
        try:
            random_seed = int(random_seed)

            if random_seed < 0:
                raise ValueError()
    
        except ValueError:
            raise ValueError("RANDOM_SEED must be a positive ingeger or 'None' to avoid randomization")
   
    
    return random_seed

def validate_csv_column(var_name: str, default_value: str, filepath: str) -> str:
    """
    Validate and retrieve a column name from the TASKS_FILE at filepath.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (str): The default value to return if the environment variable is not set properly.
    
    Returns:
        str: The value of the environment variable, or the default value if an error occurs.
    """
    
    value = validate_string(var_name, default_value)

    try:
        with open(filepath, 'r') as file:
            columns = file.readline().strip().split(",")
            if value not in columns:
                raise ValueError(f"{value} not found in the tasks.csv file. Check the configuration file.")
    except Exception as e:
        raise ValueError(f"Error validating {var_name}: {e}\n\nError validating {var_name}. Check the configuration file.")
    
    return value

def validate_set(var_name, default_value):
    """
    Validate and retrieves an environment variable and returns its value as a set.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (set): The default value to return if the environment variable is not set or cannot be parsed.

    Returns:
        set: The value of the environment variable as a set, or the default value if an error occurs.

    Notes:
        The environment variable is expected to be a comma-separated list of values.
        If an error occurs while parsing the environment variable, a warning is raised and the default value is returned.
    """

    value = validate_string(var_name, "")

    try:
        return set(value.split(","))
    except Exception as e:
        raise ValueError(f"Error parsing {var_name}: {e}\n\nError parsing {var_name}. Check the configuration file.")
    

def validate_list(var_name, default_value):
    """
    Validate and retrieves an environment variable and returns its value as a list.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (list): The default value to return if the environment variable is not set or cannot be parsed.

    Returns:
        list: The value of the environment variable as a list, or the default value if an error occurs.

    Notes:
        The environment variable is expected to be a comma-separated list of values.
        If an error occurs while parsing the environment variable, a warning is raised and the default value is returned.
    """

    value = validate_string(var_name, "")

    try:
        return value.split(",")
    except Exception as e:
        raise ValueError(f"Error parsing {var_name}: {e}\n\nError parsing {var_name}. Check the configuration file.")

def validate_dict(var_name, default_value):
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

    value = validate_string(var_name, "")

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing {var_name}: JSON Decoding Error. Check the configuration file.")
    except Exception as e:
        raise ValueError(f"Error parsing {var_name}: {e}\n\nError parsing {var_name}. Check the configuration file.")

   
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


try:
    load_environment()
except:
    st.warning("Error loading environment variables. Please check the configuration file. More information below.")

STATE = st.session_state