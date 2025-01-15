from utils.config import Config
from utils.core import load_environment
import shutil
import os
import pytest
from utils.core import *
from utils.config import *
from utils.db import initialize_db


def cleanup(config_instance):
    """
    Cleanup function to remove the database and directories after tests.
    """
    if config_instance:
        if os.path.exists(config_instance.ANNOTATIONS_DB):
            os.remove(config_instance.ANNOTATIONS_DB)

        if os.path.exists(config_instance.RAW_TEXT_DIR):
            shutil.rmtree(config_instance.RAW_TEXT_DIR)

        if os.path.exists(config_instance.CLEANED_TEXT_DIR):
            shutil.rmtree(config_instance.CLEANED_TEXT_DIR)


# =================== MISSING VARIABLE ===================
# Env gets corrupted by removing a variable. The Config class should handle missing variables gracefully.
# TODO: env file gets loaded several times before my corroped env file is loaded. This is not ideal because this way there is always a valid env file loaded.

def create_corrupted_env(original_env, corrupted_env, variable_to_remove):
    """
    Create a corrupted environment file by copying the original and removing a specific variable.

    Args:
        original_env (str): Path to the original .env file.
        corrupted_env (str): Path to the corrupted .env file.
        variable_to_remove (str): The name of the variable to remove.
    """
    shutil.copyfile(original_env, corrupted_env)
    with open(corrupted_env, 'r') as file:
        lines = file.readlines()

    with open(corrupted_env, 'w') as file:
        for line in lines:
            stripped_line = line.strip()
            if not (stripped_line.startswith(variable_to_remove)):
                file.write(line)
            # else:
            #     print(f"Removed variable: {variable_to_remove}")


@pytest.fixture
def setup_corrupted_env():
    """
    Pytest fixture to manage corrupted environment files during the test.
    """
    original_env = 'tests_data/.env-test'
    corrupted_env = 'tests_data/.env-corrupted'
    yield original_env, corrupted_env

    # Cleanup after the test)
    if os.path.exists(corrupted_env):
        os.remove(corrupted_env)


@pytest.mark.parametrize("variable", [
    "ANNOTATOR",
    "RANDOM_SEED",
    "TASKS_ID_COLUMN",
    "TASKS_URL_COLUMN",
    "WORKING_DIR",
    "TASKS_FILE",
    "ANNOTATIONS_DB",
    "RAW_TEXT_DIR",
    "CLEANED_TEXT_DIR",
    "HTML_DIR",
    "LABELS",
    "URL_QUERY_PARAMS",
    "NOT_SEO_TITLES",
    "COMMON_EXTENSIONS",
    "SPECIAL_CHARACTER_MAP"
])
def test_missing_config_variable(setup_corrupted_env, variable):
    """
    Test that the Config class handles missing environment variables gracefully by loading the config successfully
    and that database operations do not fail after loading the config.
    """
    original_env, corrupted_env = setup_corrupted_env
    create_corrupted_env(original_env, corrupted_env, variable)

    try:
        # Criteria 1: Load the corrupted environment
        load_environment(corrupted_env, force=True)
        config_instance = Config()
        assert config_instance is not None, f"Config should be loaded successfully even without {variable}"

        # Criteria 2: Initialize the database
        initialize_db()

        # Criteria 3: Load tasks
        tasks = load_tasks()
        assert tasks is not None, "Loading tasks should return a valid list"
    except Exception as e:
        pytest.fail(f"Test failed for missing variable {variable}: {e}")
