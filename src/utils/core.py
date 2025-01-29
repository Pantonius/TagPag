import re
import html
import pandas as pd

from utils.config import *
from utils.db import load_annotations, load_annotation, save_annotation
from selectolax.parser import HTMLParser
from trafilatura import extract

from utils.url_parser import explode_url
from utils.html_truncator import HTMLTruncator

# load the environment variables
config = Config()

def init():
    """
    Initialize the local storage

    Args:
        None
    
    Returns:
        None
    """
    # create the tasks file if it doesn't exist
    try:
        with open(config.TASKS_FILE, 'x') as f:
            pass
    except FileExistsError:
        pass


def reduce_line_breaks(text):
    """
    Reduce multiple line breaks to a single line break
    
    Args:
        text (str): The text to reduce line breaks in
        
    Returns:
        str: The text with reduced line breaks
    """
    
    # Use regular expression to replace multiple line breaks with a single line break
    return re.sub(r'\n\s*\n+', '\n', text.strip())

def load_annotator_tasks(annotator_id: str ):
    """
    Load the tasks from the local storage for the given annotator

    Args:
        annotator_id (str): The id of the annotator.
    
    Returns:
        list[dict]: The tasks with the annotations made by the annotator.
    """
    tasks = pd.read_csv(config.TASKS_FILE, dtype={config.TASKS_ID_COLUMN: str, config.TASKS_URL_COLUMN: str})

    # filter tasks that do not have an id or url
    tasks = tasks[tasks[config.TASKS_ID_COLUMN].notnull() & tasks[config.TASKS_URL_COLUMN].notnull()]

    # add annotations (as json)
    tasks['annotations'] = tasks[config.TASKS_ID_COLUMN].apply(load_annotations)

    # only show the annotator's annotations
    tasks['annotations'] = tasks['annotations'].apply(lambda x: x.get(annotator_id) if x is not None else None)

    # randomize with randomization seed (-1 means no randomization)
    if config.RANDOM_SEED >= 0:
        # randomize
        tasks = tasks.sample(frac=1, random_state=config.RANDOM_SEED);

    # add order field to tasks -- this is the order in which the tasks will be displayed to the annotator (1-indexed)
    tasks['order'] = range(1, len(tasks) + 1)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks

def load_tasks():
    """
    Load the tasks from the local storage (includes all annotations from all annotators)

    Args:
        None
    
    Returns:
        list[dict]: The tasks with all annotations from all annotators.
    """
    tasks = pd.read_csv(config.TASKS_FILE, dtype={config.TASKS_ID_COLUMN: str, config.TASKS_URL_COLUMN: str})

    # filter tasks that do not have an id or url
    tasks = tasks[tasks[config.TASKS_ID_COLUMN].notnull() & tasks[config.TASKS_URL_COLUMN].notnull()]

    # add annotations (as json)
    tasks['annotations'] = tasks[config.TASKS_ID_COLUMN].apply(load_annotations)

    # turn into dict
    tasks = tasks.to_dict(orient='records')

    return tasks
    
def update_task_annotations(annotator_id: str, task: dict, labels: list[str], comment: str):
    """
    Update task annotations for a given annotator and task

    Args:
        annotator_id (str): The id of the annotator.
        task (dict): The task to update.
        labels (list[str]): The labels to add to the task.
        comment (str): The comment to add to the task.
    
    Returns:
        None
    """
    try:
        annotation = load_annotation(task.get(config.TASKS_ID_COLUMN), annotator_id)
        
        # add the selected labels to the annotation
        annotation['labels'] = labels

        # add the comment to the annotation
        annotation['comment'] = comment

        # add random_seed column
        annotation['random_seed'] = config.RANDOM_SEED if config.RANDOM_SEED >= 0 else None

        # add the order in which the task was annotated
        annotation['task_order'] = task.get('order')

        save_annotation(task.get(config.TASKS_ID_COLUMN), annotator_id, annotation)

    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)

def download_annotations():
    """
    Download all annotations by all annotators for all tasks

    Args:
        None
    
    Returns:
        str: The CSV content such that a file can be downloaded
    """
    annotations = []

    tasks = load_tasks()

    for task in tasks:
        task_id = task.get(config.TASKS_ID_COLUMN)
        task_annotations = load_annotations(task_id)

        url = task.get(config.TASKS_URL_COLUMN)

        if task_annotations is None:
            # empty annotations
            task_annotations = {
                'task_id': task_id,
            }
        else:
            # compose the annotations into a single row
            task_annotations_composite = {
                'task_id': task_id
            }

            # for each annotator, add the labels, comment and order
            for annotator_id, annotation in task_annotations.items():
                labels = None
                comment = ""
                random_seed = config.RANDOM_SEED
                task_order = None

                if annotation is not None:
                    labels = annotation.get('labels')
                    comment = annotation.get('comment')
                    random_seed = annotation.get('random_seed')
                    task_order = annotation.get('task_order')

                if labels == []:
                    labels = None

                task_annotations_composite[f'{annotator_id}_labels'] = labels
                task_annotations_composite[f'{annotator_id}_comment'] = comment
                task_annotations_composite[f'{annotator_id}_order'] = task_order
                task_annotations_composite[f'{annotator_id}_random_seed'] = random_seed

            # update the task annotations to be the composite
            task_annotations = task_annotations_composite
        
        # url should be the last column
        task_annotations['url'] = url

        # append the task annotations to the list of annotations
        annotations.append(task_annotations)

    # save to csv
    annotations = pd.DataFrame(annotations)
    return annotations.to_csv(index=False)

def get_page_content(id: str):
    """
    Get the content of the page with the given id

    Args:
        id (str): The id of the page.
    
    Returns:
        str: The html content of the page.
    """
    try:
        # Read the content of the page
        html_path = os.path.join(config.HTML_DIR, f"{id}.html")
        with open(html_path, "r", encoding="utf8") as f:
            return f.read()
    except FileNotFoundError:
        return None

def extract_raw_text(id: str):
    """
    Extract the text from an HTML document associated with a task (selectolax)

    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """
    # get page content
    html_document = get_page_content(id)

    # if the page content is None, there is nothing to extract
    if html_document is None:
        return None
        
    tree = HTMLParser(html_document)

    # if the body is None, there is nothing to extract
    if tree.body is None:
        return None

    # Remove scripts and styles
    for tag in tree.css('script'):
        tag.decompose()
    for tag in tree.css('style'):
        tag.decompose()

    # Extract the text
    text = reduce_line_breaks(tree.body.text(separator='\n'))

    # Save the parsed selectolax text to a file
    text_path = os.path.join(config.RAW_TEXT_DIR, f"{id}.txt")
    with open(text_path, 'w', encoding="utf8") as f:
        f.write(text)
        
    # Return the extracted text
    return text

def load_raw_text(id: str):
    """
    Load the text from an HTML document associated with a task (selectolax)
    
    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """

    # First check if there already is a parsed version in the selectolax directory
    try:
        # read the file content if it exists
        text_path = os.path.join(config.RAW_TEXT_DIR, f"{id}.txt")
        with open(text_path, 'r') as f:
            # return the content of the file
            return f.read()
    except FileNotFoundError:
        return extract_raw_text(id)

def extract_cleaned_text(id: str):
    """
    Extracts the text from an HTML document associated with a task and cleans it up (trafilatura)
    
    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """

    # read the html content
    html_document = get_page_content(id)
        
    # if the page content is None, there is nothing to extract
    if html_document is None:
        return None
        
    # extract the text
    text = extract(html_document)

    # if the text is None, there is nothing to save
    if text is None:
        return None

    # Save the parsed trafilatura text to a file
    text_path = os.path.join(config.CLEANED_TEXT_DIR, f"{id}.txt")
    with open(text_path, 'w') as f:
        f.write(text)
        
    # Return the extracted text
    return text

def load_cleaned_text(id: str):
    """
    Loads the extracted text of an HTML document associated with a task (trafilatura)
    
    Args:
        id (str): The id of the task.
    
    Returns:
        str: The text extracted from the HTML document.
    """

    # First check if there already is a parsed version in the trafilatura directory
    try:
        # read the file content if it exists
        text_path = os.path.join(config.CLEANED_TEXT_DIR, f"{id}.txt")
        with open(text_path, 'r') as f:
            # return the content of the file
            return f.read()
    except FileNotFoundError:
        # extract the cleaned text
        return extract_cleaned_text(id)

def update_cleaned_text(task_id: str, text: str):
    """
    Update the cleaned text for the task with the given id

    Args:
        id (str): The id of the task.
        text (str): The cleaned text for the task.
    
    Returns:
        None
    """
    
    text_path = os.path.join(config.CLEANED_TEXT_DIR, f"{task_id}.txt")
    with open(text_path, 'w') as f:
        f.write(text)

def truncate_string(string: str, n=100):
    """
    Truncates a given string to a maximum length of n characters.

    Args:
        string (str): The string to truncate.
        n (int): The maximum length of the string. No truncation if set to 0. (Default: 100)
    
    Returns:
        str: The truncated string
    """

    # if the maximum length n is lower than one or no truncation is needed to meet the given length limit, return the entire string
    if n <= 0 or len(string) <= n:
        return string

    # otherwise truncate
    return string[:n] + '...'

def truncate_html(html: str, limit: int):
    """
    Truncates the given HTML content to a specified character limit while preserving HTML structure.

    Args:
        html (str): The HTML content to be truncated.
        limit (int): The maximum number of characters to retain in the truncated HTML.

    Returns:
        str: The truncated HTML content with all tags properly closed.
    """
    # create an HTML parser
    parser = HTMLTruncator(limit)

    # feed the HTML content to the parser
    parser.feed(html)

    # return the truncated HTML content
    return parser.get_truncated_html()


def highlight_substring(substring: str, string: str):
    """
    Highlights the substring part of a given string

    Args:
        substring (str): The substring to highlight
        string (str): The string containing the substring
    
    Returns:
        str: The highlighted string
    """
    
    # if the substring is not part of the string, return the string
    if substring not in string or substring == "":
        return html.escape(string)

    # get the index of the substring in the string
    start = string.index(substring)
    end = start + len(substring)

    # make the substring html safe
    substring = html.escape(substring)

    # return the highlighted string
    return f'{html.escape(string[:start])}<strong>{substring}</strong>{html.escape(string[end:])}'


def highlight_query_param(param: str, query: str):
    """
    Highlights the values of a given parameter in a query string

    Args:
        param (str): The parameter whose values to highlight
        query (str): The query string
    
    Returns:
        str: The query string with highlighted values
    """
    
    # Define a regex pattern to find the parameter and its value
    pattern = re.compile(r'({}=)([^&]*)'.format(re.escape(param)))
    
    # Function to replace the matched value with highlighted value
    def replace_func(match):
        key = match.group(1)
        value = match.group(2)
        highlighted_value = f'<strong>{html.escape(value)}</strong>'
        return f'{key}{highlighted_value}'
    
    # Use re.sub to replace all occurrences of the parameter's value
    highlighted_query = pattern.sub(replace_func, query)
    
    return highlighted_query


def highlight_url(exploded_url: dict | str, n=0):
    """
    Highlights the *"main part"* of a given url (meaning the fqdn and path) and truncates it to a maximum length of n characters

    Args:
        exploded_url (dict | str): The exploded version of the url to make fancy (dict) or the plain text url (str)
        n (int): The maximum length of the string. No truncation if set to 0. (Default: 0)
    
    Returns:
        str: The highlighted string
    """

    # ensure that the exploded_url is indeed exploded (check for string)
    if isinstance(exploded_url, str):
        exploded_url = explode_url(exploded_url)

    # format query
    _query = ""

    if exploded_url["query"]:
        _query = f'?{exploded_url["query"]}'

    # format
    scheme = f'{exploded_url["scheme"]}://'
    fqdn = highlight_substring(exploded_url["hostname"], exploded_url["fqdn"])
    path = highlight_substring(exploded_url["title"], exploded_url["path"])
    query = exploded_url["query"]
    fragment = exploded_url["fragment"]

    query = html.escape(query)
    if exploded_url["search_terms"]:    
        for param in config.URL_QUERY_PARAMS:
            query = highlight_query_param(param, query)
    
    # add ? if query is not empty
    if query:
        query = f'?{query}'

    # add # if fragment is not empty
    if fragment:
        fragment = f'#{fragment}'
    
    # return the highlighted url
    return truncate_html(f'{scheme}{fqdn}{path}{query}{fragment}', n)
