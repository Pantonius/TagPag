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

def test_highlight_url_with_truncation():
    # Test cases for highlight_url with truncation
    
    # 1. Truncate the URL in the middle of the domain
    assert highlight_url('https://some.website.com/long/path/to_some_file.html', 12) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python', 12) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python&lang=en', 12) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python#section', 12) == 'https://<strong>some...</strong>'

    # 2. Truncate the URL after the domain
    assert highlight_url('https://some.website.com/long/path/to_some_file.html', 30) == 'https://<strong>some.website.com</strong>/long/...'
    assert highlight_url('https://some.website.com/search?q=python', 31) == 'https://<strong>some.website.com</strong>/search...'
    assert highlight_url('https://some.website.com/search?q=python&lang=en', 36) == 'https://<strong>some.website.com</strong>/search?q=<strong>py...</strong>'
    assert highlight_url('https://some.website.com/search?lang=en&q=python#section', 36) == 'https://<strong>some.website.com</strong>/search?lang...'

def test_reduce_line_breaks():
    assert reduce_line_breaks("Line1\n\n\nLine2\n\nLine3") == "Line1\nLine2\nLine3"
    assert reduce_line_breaks("Line1\n\n\n\n\nLine2") == "Line1\nLine2"
    assert reduce_line_breaks("Line1\n\nLine2\n\n\nLine3\n\n\n") == "Line1\nLine2\nLine3"

def test_truncate_string():
    assert truncate_string("This is a long string that needs to be truncated", 20) == "This is a long strin..."
    assert truncate_string("Short string", 20) == "Short string"
    assert truncate_string("Exact length string!", 20) == "Exact length string!"

def test_highlight_substring():
    assert highlight_substring("highlight", "This is a highlight test") == "This is a <strong>highlight</strong> test"
    assert highlight_substring("test", "This is a test") == "This is a <strong>test</strong>"
    assert highlight_substring("notfound", "This is a test") == "This is a test"

def test_highlight_query_param():
    assert highlight_query_param("q", "q=python&lang=en") == "q=<strong>python</strong>&lang=en"
    assert highlight_query_param("lang", "q=python&lang=en") == "q=python&lang=<strong>en</strong>"
    assert highlight_query_param("notfound", "q=python&lang=en") == "q=python&lang=en"

def test_load_annotator_tasks():
    # 0. Prepare the database
    cleanup()
    initialize_db()

    first_task = {
        'labels': ['label_1', 'label_2'],
        'comment': "Comment"
    }
    save_annotation("1", "annotator_1", first_task)

    second_task = {
        'labels': ['label_1', 'label_2'],
        'comment': "Comment"
    }
    save_annotation("2", "annotator_1", second_task)

    # 1. Load tasks for annotator_1
    tasks = load_annotator_tasks("annotator_1")
    for i, task in enumerate(tasks):
        assert task[config.TASKS_ID_COLUMN] == f"{i}"
        assert task["order"] == i + 1
    
    assert tasks[1]["annotations"] == first_task
    assert tasks[2]["annotations"] == second_task

    # 3. Cleanup
    cleanup()

def test_load_tasks():
    # 0. Clean the database
    cleanup()
    initialize_db()
    
    # 1. Load tasks
    tasks = load_tasks()
    
    # Check if the tasks are loaded correctly
    for task in tasks:
        assert task[config.TASKS_ID_COLUMN] is not None
        assert task[config.TASKS_URL_COLUMN] is not None
    
    assert len(tasks) == 21

    # 2. Cleanup
    cleanup()

def test_update_task_annotations():
    task = {"_id": "1", "order": 1}
    update_task_annotations("annotator_1", task, ["label1", "label2"], "comment")
    # No assertion needed, just ensure no exceptions are raised

def test_download_annotations():
    csv_content = download_annotations()
    assert "_id,url" in csv_content

def test_get_page_content():
    # 0. Cleanup + Create the db anew
    cleanup()
    initialize_db()

    # 1. well-formed task_id
    tasks = load_tasks()

    # for each task check that get_page_content(task_id) matches
    for task in tasks:
        task_id = task[config.TASKS_ID_COLUMN]
        content = get_page_content(task_id)

        # content should not be None
        assert content is not None

        # URL should match (each html file in our test_data has the URL in the third line)
        html_url = content.split("\n")[2].strip().replace("url: ", "")
        task_url = task[config.TASKS_URL_COLUMN]

        # it's sufficient to check if the HTML URL is a substring of the task URL -- the other way around is not guaranteed
        assert html_url in task_url
    
    # 2. malformed task_id
    assert get_page_content("invalid_task_id") is None

    # 3. Cleanup
    cleanup()

def test_extract_raw_text():
    # 0. Cleanup + Create the db and directories anew
    cleanup()
    initialize_db()
    create_directories()

    # 1. Extract from a well-formed HTML file
    tasks = load_tasks()

    # for each task check that extract_raw_text(task_id) matches
    for task in tasks:
        task_id = task[config.TASKS_ID_COLUMN]
        text = extract_raw_text(task_id)

        # text should not be None
        assert text is not None

        # the text should match the content of the HTML file
        with open(f"{config.WORKING_DIR}/correct_raw_text/{task_id}.txt", "r") as f:
            assert text == f.read()

    # 2. Extract from a malformed HTML file
    text = extract_raw_text("invalid_task_id")
    assert text is None

    # 3. Cleanup
    cleanup()

def test_load_raw_text():
     # 0. Cleanup + Create the db and directories anew
    cleanup()
    initialize_db()
    create_directories()

    # 1. Load from a well-formed HTML file
    tasks = load_tasks()

    # for each task check that load_cleaned_text(task_id) matches
    for task in tasks:
        task_id = task[config.TASKS_ID_COLUMN]
        text = load_raw_text(task_id)

        # text should not be None
        assert text is not None

        # the text should match the content of the HTML file
        with open(f"{config.WORKING_DIR}/correct_raw_text/{task_id}.txt", "r") as f:
            assert text == f.read()
    
    # 2. Load from a malformed HTML file
    text = load_raw_text("invalid_task_id")
    assert text is None

    # 3. Cleanup
    cleanup()

def test_extract_cleaned_text():
        # 0. Cleanup + Create the db and directories anew
    cleanup()
    initialize_db()
    create_directories()

    # 1. Extract from a well-formed HTML file
    tasks = load_tasks()

    # for each task check that extract_cleaned_text(task_id) matches
    for task in tasks:
        task_id = task[config.TASKS_ID_COLUMN]
        text = extract_cleaned_text(task_id)

        # text should not be None
        assert text is not None

        # the text should match the content of the HTML file
        with open(f"{config.WORKING_DIR}/correct_cleaned_text/{task_id}.txt", "r") as f:
            assert text == f.read()

    # 2. Extract from a malformed HTML file
    text = extract_cleaned_text("invalid_task_id")
    assert text is None

    # 3. Cleanup
    cleanup()

def test_load_cleaned_text():
    # 0. Cleanup + Create the db and directories anew
    cleanup()
    initialize_db()
    create_directories()

    # 1. Load from a well-formed HTML file
    tasks = load_tasks()

    # for each task check that load_cleaned_text(task_id) matches
    for task in tasks:
        task_id = task[config.TASKS_ID_COLUMN]
        text = load_cleaned_text(task_id)

        # text should not be None
        assert text is not None

        # the text should match the content of the HTML file
        with open(f"{config.WORKING_DIR}/correct_cleaned_text/{task_id}.txt", "r") as f:
            assert text == f.read()
    
    # 2. Load from a malformed HTML file
    text = load_cleaned_text("invalid_task_id")
    assert text is None

    # 3. Cleanup
    cleanup()

def test_update_cleaned_text():
    # 0. Cleanup + Create the db and directories anew
    cleanup()
    initialize_db()
    create_directories()

    # 1. Update the cleaned text for a well-formed HTML file
    task1 = load_tasks()[0]

    # Load the cleaned text
    task_id = task1[config.TASKS_ID_COLUMN]
    text = load_cleaned_text(task_id)

    # Update the cleaned text
    new_content = "Test\nTest\nTest"
    update_cleaned_text(task_id, new_content)

    # Load the updated cleaned text
    updated_text = load_cleaned_text(task_id)
    assert updated_text == new_content

    # 2. Update the cleaned text for a malformed HTML file
    update_cleaned_text("invalid_task_id", "Test")
    # No assertion needed, just ensure no exceptions are raised

    # 3. Cleanup
    cleanup()
