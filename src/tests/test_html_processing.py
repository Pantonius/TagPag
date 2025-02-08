from utils.core import *
from utils.config import *
from utils.db import initialize_db
import pytest


def cleanup():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)

    # 1. Cleanup: Remove the directories
    if os.path.exists(config.RAW_TEXT_DIR):
        shutil.rmtree(config.RAW_TEXT_DIR)

    if os.path.exists(config.CLEANED_TEXT_DIR):
        shutil.rmtree(config.CLEANED_TEXT_DIR)


@pytest.mark.parametrize("task_id,description", [
    ("0", "Image file"),
    ("1", "Empty file"),
    ("2", "Malformed HTML"),
    ("3", "Non-HTML file (Markdown)"),
    ("4", "Multilingual character set"),
    ("5", "Unusual characters"),
])
def test_extract_corrupted_raw_text(task_id, description):
    """
    Test that extract_raw_text does not raise an error for various cases.
    """
    cleanup()
    load_environment('tests_data/.env-test', force=True)

    config = Config()
    config.HTML_DIR = 'corrupted_html'

    initialize_db()
    create_directories()

    try:
        extract_raw_text(task_id)  # Ensure no unhandled exception is raised
    except Exception as e:
        pytest.fail(
            f"extract_raw_text failed for task ID {task_id} ({description}): {e}")
    finally:
        cleanup()


@pytest.mark.parametrize("task_id,description", [
    ("0", "Image file"),
    ("1", "Empty file"),
    ("2", "Malformed HTML"),
    ("3", "Non-HTML file (Markdown)"),
    ("4", "Multilingual character set"),
    ("5", "Unusual characters"),
])
def test_load_corrupted_raw_text(task_id, description):
    """
    Test that load_raw_text does not raise an error for various cases.
    """
    cleanup()
    load_environment('tests_data/.env-test', force=True)

    config = Config()
    config.HTML_DIR = 'corrupted_html'

    initialize_db()
    create_directories()

    try:
        load_raw_text(task_id)  # Ensure no unhandled exception is raised
    except Exception as e:
        pytest.fail(
            f"load_raw_text failed for task ID {task_id} ({description}): {e}")
    finally:
        cleanup()


@pytest.mark.parametrize("task_id,description", [
    ("0", "Image file"),
    ("1", "Empty file"),
    ("2", "Malformed HTML"),
    ("3", "Non-HTML file (Markdown)"),
    ("4", "Multilingual character set"),
    ("5", "Unusual characters"),
])
def test_extract_corrupted_cleaned_text(task_id, description):
    """
    Test that extract_cleaned_text does not raise an error for various cases.
    """
    cleanup()
    load_environment('tests_data/.env-test', force=True)

    config = Config()
    config.HTML_DIR = 'corrupted_html'

    initialize_db()
    create_directories()

    try:
        # Ensure no unhandled exception is raised
        extract_cleaned_text(task_id)
    except Exception as e:
        pytest.fail(
            f"extract_cleaned_text failed for task ID {task_id} ({description}): {e}")
    finally:
        cleanup()


@pytest.mark.parametrize("task_id,description", [
    ("0", "Image file"),
    ("1", "Empty file"),
    ("2", "Malformed HTML"),
    ("3", "Non-HTML file (Markdown)"),
    ("4", "Multilingual character set"),
    ("5", "Unusual characters"),
])
def test_load_corrupted_cleaned_text(task_id, description):
    """
    Test that load_cleaned_text does not raise an error for various cases.
    """
    cleanup()
    load_environment('tests_data/.env-test', force=True)

    config = Config()
    config.HTML_DIR = 'corrupted_html'

    initialize_db()
    create_directories()

    try:
        load_cleaned_text(task_id)  # Ensure no unhandled exception is raised
    except Exception as e:
        pytest.fail(
            f"load_cleaned_text failed for task ID {task_id} ({description}): {e}")
    finally:
        cleanup()
