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

    # 2. Add annotations
    task = {"_id": "1", "order": 1}
    update_task_annotations("annotator_1", task, ["label1", "label2"], "comment")

    # 3. Download CSV content
    csv_content = download_annotations()

    # 4. Read existing CSV file and compare content
    csv_filename = "tests_data/work_dir/tasks_exported.csv"
    with open(csv_filename, "r", encoding="utf-8") as f:
        saved_csv_content = f.read()

    assert saved_csv_content.strip() == csv_content.strip(), f"CSV content mismatch:\n{saved_csv_content}"

    # 5. Cleanup
    cleanup()

def test_download_annotations_columns():
    # 0. Clean the database
    cleanup()
    initialize_db()

    # 1. Load tasks
    tasks = load_tasks()

    # 2. Add annotations
    task = {"_id": "1", "order": 1}
    update_task_annotations("annotator_1", task, ["label1", "label2"], "comment")

    # 3. Download CSV content
    csv_content = download_annotations()

    # 4. Extract the header row
    csv_lines = csv_content.strip().split("\n")
    header = csv_lines[0].split(",")

    # 5. Expected columns
    expected_columns = [
        "task_id",
        "url",
        "annotator_1_labels",
        "annotator_1_comment",
        "annotator_1_order",
        "annotator_1_random_seed"
    ]

    # 6. Validate column names
    missing_columns = [col for col in expected_columns if col not in header]
    assert not missing_columns, f"Missing columns: {missing_columns}"

    # 7. Cleanup
    cleanup()