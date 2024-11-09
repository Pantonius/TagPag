from utils.core import *
from utils.config import *
from utils.db import initialize_db

load_environment('.env-test', force=True)
config = Config()

def cleanup():
    # 0. Cleanup: Remove the database file, if it exists
    if os.path.exists(config.ANNOTATIONS_DB):
        os.remove(config.ANNOTATIONS_DB)

def test_highlight_url_with_truncation():
    # Test cases for highlight_url with truncation
    
    # 1. Truncate the URL to 20 characters
    assert highlight_url('https://some.website.com/long/path/to_some_file.html', 20) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python', 20) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python&lang=en', 20) == 'https://<strong>some...</strong>'
    assert highlight_url('https://some.website.com/search?q=python#section', 20) == 'https://<strong>some...</strong>'

    # 2. Truncate the URL to 30 characters
    assert highlight_url('https://some.website.com/long/path/to_some_file.html', 30) == 'https://<strong>some.website.com</strong>/long...'
    assert highlight_url('https://some.website.com/search?q=python', 30) == 'https://<strong>some.website.com</strong>/search...'
    assert highlight_url('https://some.website.com/search?q=python&lang=en', 30) == 'https://<strong>some.website.com</strong>/search...'
    assert highlight_url('https://some.website.com/search?q=python#section', 30) == 'https://<strong>some.website.com</strong>/search...'

def test_reduce_line_breaks():
    assert reduce_line_breaks("Line1\n\n\nLine2\n\nLine3") == "Line1\nLine2\nLine3"
    assert reduce_line_breaks("Line1\n\n\n\n\nLine2") == "Line1\nLine2"
    assert reduce_line_breaks("Line1\n\nLine2\n\n\nLine3") == "Line1\nLine2\nLine3"

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
        assert task[config.TASKS_ID_COLUMN] == i
        assert task["order"] == i + 1
    
    assert tasks[0]["annotations"] == first_task
    assert tasks[1]["annotations"] == second_task

    # 3. Cleanup
    cleanup()

def test_load_tasks():
    tasks = load_tasks()
    assert len(tasks) == 24

def test_update_task_annotations():
    # Mock the config and save_annotation
    config.TASKS_ID_COLUMN = "task_id"
    config.RANDOM_SEED = 42
    save_annotation = lambda *args: None

    task = {"task_id": "1", "order": 1}
    update_task_annotations("annotator_1", task, ["label1", "label2"], "comment")
    # No assertion needed, just ensure no exceptions are raised

def test_download_annotations():
    # Mock the config and load_tasks
    config.TASKS_ID_COLUMN = "task_id"
    config.TASKS_URL_COLUMN = "url"
    tasks_data = [
        {"task_id": "1", "url": "https://example.com"},
        {"task_id": "2", "url": "https://example.com"}
    ]
    load_tasks = lambda: tasks_data
    load_annotations = lambda _: {}

    csv_content = download_annotations()
    assert "task_id,url" in csv_content

def test_get_page_content():
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

def test_extract_raw_text():
    # Mock the config and file reading
    config.RAW_TEXT_DIR = "/path/to/raw_text"
    config.HTML_DIR = "/path/to/html"
    open = lambda *args: open("/path/to/html/1.html", "r")

    text = extract_raw_text("1")
    assert text is not None

def test_extract_cleaned_text():
    # Mock the config and file reading
    config.CLEANED_TEXT_DIR = "/path/to/cleaned_text"
    config.HTML_DIR = "/path/to/html"
    open = lambda *args: open("/path/to/html/1.html", "r")

    text = extract_cleaned_text("1")
    assert text is not None

def test_load_cleaned_text():
    # Mock the config and file reading
    config.CLEANED_TEXT_DIR = "/path/to/cleaned_text"
    open = lambda *args: open("/path/to/cleaned_text/1.txt", "r")

    text = load_cleaned_text("1")
    assert text is not None

def test_update_cleaned_text():
    # Mock the config and file writing
    config.CLEANED_TEXT_DIR = "/path/to/cleaned_text"
    open = lambda *args: open("/path/to/cleaned_text/1.txt", "w")

    update_cleaned_text("1", "cleaned text")
    # No assertion needed, just ensure no exceptions are raised