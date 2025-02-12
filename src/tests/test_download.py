from utils.core import *
from utils.config import *
from utils.db import initialize_db

load_environment('tests_data/.env-test', force=True)
config = Config()


def cleanup():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)

    # 1. Cleanup: Remove the directories
    if os.path.exists(config.RAW_TEXT_DIR):
        shutil.rmtree(config.RAW_TEXT_DIR)

    if os.path.exists(config.CLEANED_TEXT_DIR):
        shutil.rmtree(config.CLEANED_TEXT_DIR)


def test_update_task_annotations():

    # 0. Clean the database
    cleanup()
    initialize_db()

    # 1. Load tasks
    tasks = load_tasks()

    task = {"_id": "1", "order": 1}
    update_task_annotations("annotator_1", task, [
                            "label1", "label2"], "comment")
    # No assertion needed, just ensure no exceptions are raised

    # 2. Cleanup
    cleanup()


def test_download_annotations():

    # 0. Clean the database
    cleanup()
    initialize_db()

    # 1. Load tasks
    tasks = load_tasks()

    csv_content = download_annotations()
    assert "_id,url" in csv_content
