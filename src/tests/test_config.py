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

# =================== WRONG DATA TYPES ===================
# This test checks if the Config class can handle wrong data types in the environment variables.
# TODO: This created sqllite database file in the root directory.


def create_invalid_env(original_env, invalid_env, variable_to_modify, invalid_value):
    """
    Create an environment file with an invalid value for a specific variable.

    Args:
        original_env (str): Path to the original .env file.
        invalid_env (str): Path to the invalid .env file.
        variable_to_modify (str): The name of the variable to modify.
        invalid_value (str): The invalid value to assign to the variable.
    """
    shutil.copyfile(original_env, invalid_env)
    with open(invalid_env, 'r') as file:
        lines = file.readlines()

    with open(invalid_env, 'w') as file:
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith(variable_to_modify):
                file.write(f"{variable_to_modify} = {invalid_value}\n")
            else:
                # Keep the line unchanged
                file.write(line)


@pytest.fixture
def setup_invalid_env():
    """
    Pytest fixture to create and manage invalid environment files during the test.
    """
    original_env = 'tests_data/.env-test'
    invalid_env = 'tests_data/.env-invalid'

    # Ensure the invalid file is removed after the test
    def cleanup_invalid_env():
        if os.path.exists(invalid_env):
            os.remove(invalid_env)

    yield original_env, invalid_env

    cleanup_invalid_env()


# @pytest.mark.parametrize("variable", [
#    * "ANNOTATOR",
#     *"RANDOM_SEED",
#     "TASKS_ID_COLUMN",
#     "TASKS_URL_COLUMN",
#     * "WORKING_DIR", <--- dangerous to test
#     *"TASKS_FILE",
#     *"ANNOTATIONS_DB",
#     *"RAW_TEXT_DIR",
#     *"CLEANED_TEXT_DIR",
#     *"HTML_DIR",

#     "LABELS",
#     "URL_QUERY_PARAMS",
#     "NOT_SEO_TITLES",
#     "COMMON_EXTENSIONS",
#     "SPECIAL_CHARACTER_MAP"
# ])
# @pytest.mark.parametrize("invalid_value", [
#     # "'INVALID_STRING'",  # String
#     # "123456",            # Integer
#     # "true",              # Boolean-like string
#     "['item1', 'item2']"  # List
# ])
# def test_invalid_config_value(setup_invalid_env, variable, invalid_value):
#     """
#     Test that the Config class handles invalid environment variable values gracefully by loading the config successfully
#     and that database operations do not fail after loading the config.
#     """
#     original_env, invalid_env = setup_invalid_env

#     # Step 1: Create the invalid environment file
#     create_invalid_env(original_env, invalid_env, variable, invalid_value)

#     try:
#         # Step 2: Load the invalid environment and initialize Config
#         load_environment(invalid_env, force=True)
#         config_instance = Config()
#         assert config_instance is not None, f"Config should be loaded successfully even with invalid value for {variable}"

#         # Step 3: Initialize the database
#         initialize_db()

#         # Step 4: Load tasks
#         tasks = load_tasks()
#         assert tasks is not None, "Loading tasks should return a valid list"
#     except Exception as e:
#         pytest.fail(
#             f"Test failed for variable {variable} with value {invalid_value}: {e}")

@pytest.mark.parametrize("variable", [
    "RANDOM_SEED",
])
@pytest.mark.parametrize("invalid_value", [
    "'INVALID_STRING'",  # String
])
def test_invalid_random_seed(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid random seed values gracefully 
    by failing with the appropiate error message.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    # Step 2: Load the invalid environment
    with pytest.raises(ValueError):
        load_environment(invalid_env, force=True)

@pytest.mark.parametrize("variable", [
    "WORKING_DIR",
])
@pytest.mark.parametrize("invalid_value", [
    "'not_existing_directory'",
])
def test_invalid_working_directory(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid random seed values gracefully 
    by failing with the appropiate error message.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    # Step 2: Load the invalid environment
    with pytest.raises(ValueError):
        load_environment(invalid_env, force=True)


@pytest.mark.parametrize("variable", [
    "HTML_DIR",
])
@pytest.mark.parametrize("invalid_value", [
    "'not_existing_directory'",
])
def test_invalid_html_directory(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid random seed values gracefully 
    by failing with the appropiate error message.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    # Step 2: Load the invalid environment
    with pytest.raises(ValueError):
        load_environment(invalid_env, force=True)

@pytest.mark.parametrize("variable", [
    "TASKS_FILE",
])
@pytest.mark.parametrize("invalid_value", [
    "'not_existing_file'",  
])
def test_invalid_tasks_file(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid random seed values gracefully 
    by failing with the appropiate error message.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    # Step 2: Load the invalid environment
    with pytest.raises(ValueError):
        load_environment(invalid_env, force=True)


@pytest.mark.parametrize("variable", [
    "SPECIAL_CHARACTER_MAP",
])
@pytest.mark.parametrize("invalid_value", [
    "'not_a_dictionary'",  
])
def test_invalid_character_map(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid random seed values gracefully 
    by failing with the appropiate error message.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    # Step 2: Load the invalid environment
    with pytest.raises(ValueError):
        load_environment(invalid_env, force=True)



@pytest.mark.parametrize("variable", [
    "TASKS_ID_COLUMN",
    "TASKS_URL_COLUMN",
])
@pytest.mark.parametrize("invalid_value", [
    "invalid_column"  # List
])
def test_invalid_config_value(setup_invalid_env, variable, invalid_value):
    """
    Test that the Config class handles invalid environment variable values gracefully by loading the config successfully
    and that database operations do not fail after loading the config.
    """
    original_env, invalid_env = setup_invalid_env

    # Step 1: Create the invalid environment file
    create_invalid_env(original_env, invalid_env, variable, invalid_value)

    try:
        # Step 2: Load the invalid environment and initialize Config
        load_environment(invalid_env, force=True)

        # Step 3: Initialize the database
        initialize_db()

        # Step 4: Load tasks
        tasks = load_tasks()
        assert tasks is not None, "Loading tasks should return a valid list"

    except Exception as e:

        # Step 5: Restore the original environment for future tests
        load_environment(original_env, force=True)

        pytest.fail(
            f"Test failed for variable {variable} with value {invalid_value}: {e}")