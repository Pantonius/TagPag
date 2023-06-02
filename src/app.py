
# ===========================================================================
#                            Web Interface
# ===========================================================================

import streamlit.components.v1 as components
import streamlit as st
from utils.database import *
from utils.files import *

# ================================= CONFIG ================================

st.set_page_config(
    page_title="Webpage Annotations",
    layout="wide",
    page_icon="📄",
    initial_sidebar_state="expanded",
    # menu_items={
    #      'Get Help': 'https://www.extremelycoolapp.com/help',
    #      'Report a bug': "https://www.extremelycoolapp.com/bug",
    #      'About': "# This is a header. This is an *extremely* cool app!"
    #  }
)

# ================================= DATABASE ================================

fs, db = getConnection(use_dotenv=True)

# ================================= CONSTANTS ================================

LABELS = ['None', 'Login', 'Paywall', 'Cookie consent']
TASKS = read_json_file("example_data.json")
STATE = st.session_state

# ================================= INIT STATE ===============================

# Extract query parameters
params = st.experimental_get_query_params()

# Set annotator ID
if 'annotator_id' not in st.session_state:
    annotator_id = params.get('annotator_id', None)
    STATE.annotator_id = annotator_id[0] if annotator_id else None
    print("Annotator ID:", STATE.annotator_id)

# Set task mongodb object ID
if 'task_object_id' not in st.session_state:
    STATE.task_object_id = "63e6b1425b2943de553ee687"

# Set webpage ID
if 'task_id' not in st.session_state:
    STATE.task_id = 0

# Get tasks
if 'tasks' not in st.session_state:
    # if not STATE.task_object_id:
    with st.spinner('Loding tasks...'):
        tasks = fetchTasks(db, 1, "PROCESSED-STATIC", 100,
                           {"_id": 1, "landing_url": 1, "content_requests": 1, "status_code": 1, "annotations": 1})
    STATE.tasks = tasks
    # else:
    #    ...
    # print(len(TASKS), end="\n\n")

# Shorthand variables
tasks = STATE.tasks
task = STATE.tasks[STATE.task_id]
annotator_id = STATE.annotator_id
task_url = STATE.tasks[STATE.task_id]['landing_url']
task_labels_current = task.get('annotations', {}).get(
    annotator_id, {}).get('labels', [])

# ================================= FUNCTIONS ===============================


def set_user_id():
    """
    Set the user ID and update the annotator ID in the STATE object.

    This function retrieves the user ID from the STATE object and sets it as the annotator ID.
    It also updates the query parameters with the annotator ID using st.experimental_set_query_params().

    """
    user_id = STATE.input_user_id
    STATE.annotator_id = user_id
    st.experimental_set_query_params(annotator_id=user_id)


def display_webpage(iframe_content, task):
    """
    Display the webpage content in an iframe based on the task information.

    This function takes the iframe_content and task information as input.
    If the task has a valid file_id, it retrieves the page content from the database/file system and displays it in the iframe.
    Otherwise, it constructs an iframe with the landing_url from the task and displays it.

    Args:
        iframe_content (object): The object to display the webpage content.
        task (dict): The task containing the webpage information.

    """
    url = task.get('landing_url')
    file_id = task.get('content_requests')

    if file_id:
        info = getPageContentInfo(db, file_id)
        content = getPageContent(fs, file_id)
        iframe_content = components.html(content, height=2048, scrolling=True)
    else:
        iframe_content.write(
            f'<iframe src="{url}" width="100%" height="1024px" style="border:none;"></iframe>', unsafe_allow_html=True)


def save_annotations(task, annotator_id, annotations):
    """
    Save the annotations for a given task and display a confirmation message.

    This function saves the annotations for a specific task in a database or file.
    It then displays a confirmation message with the tags that were saved.

    Args:
        task (dict): The task to save the annotations for.
        annotator_id (str): The ID of the annotator.
        annotations (dict): The annotations to be saved.

    """
    task_obj_id = task.get('_id')

    # TODO: Commented out for testing purposes
    # if task_obj_id:
    #    updateTask(db, task_obj_id, annotator_id, annotations)

    tag_labels = ', '.join(annotations.get("labels", []))
    st.success(f'Annotation saved! Webpage tagged as "{tag_labels}"')


def go_to_next_task():
    """
    Update the task annotations for the current task and move to the next task.

    This function updates the annotations for the current task based on the selected tags in the STATE object.
    It catches and handles potential errors such as KeyError and TypeError that may occur during the update.
    After successfully updating the annotations, it increments the task ID in the STATE object to move to the next task.
    """

    try:
        task = STATE.tasks[STATE.task_id]
        annotations = task.setdefault("annotations", {})
        annotations[STATE.annotator_id] = {
            "labels": STATE.selected_tags
        }
    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)
    else:
        STATE.task_id += 1


def go_to_prev_task():
    try:
        task = STATE.tasks[STATE.task_id]
        annotations = task.setdefault("annotations", {})
        annotations[STATE.annotator_id] = {
            "labels": STATE.selected_tags
        }
    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)
    else:
        STATE.task_id -= 1

# ---------------------------------------------------------------------------
#                            Layout
# ---------------------------------------------------------------------------


# ================================= SETUP SCREEN ===============================

# Ask for annotator ID if not provided
if not STATE.annotator_id:
    with st.form("form_user_id"):

        # Display warning message if no user ID is provided
        st.error('No user ID detected. Please enter a user ID below.', icon="🚨")
        user_id = st.text_input("User ID", key='input_user_id')
        submit_button = st.form_submit_button("Submit", on_click=set_user_id)

        # Handle form submission
        if submit_button:
            if user_id:
                st.success(f"User ID '{user_id}' submitted successfully!")
            else:
                st.warning("Please enter a User ID.")

# ================================= MAIN SCREEN ===============================

else:

    # Tabs
    tab_names = ["Snapshot", "Current", "More Info", "All Tasks"]
    tab_snapshot, tab_current, tab_info, tab_list = st.tabs(tab_names)

    # TAB: Display webpage snapshot
    with tab_snapshot:
        container = st.container()
        container.warning(
            "Please be aware that webpage snapshots may appear distorted.")
        container.iframe_content = st.empty()
        display_webpage(container.iframe_content, task)

    # TAB: Display current version of webpage
    with tab_current:
        st.warning(
            'If the webpage is not loading properly, please open it in a new tab to ensure proper functionality.')
        st.write(
            f'<iframe src="{task_url}" width="100%" height="1024px" style="border:none;"></iframe>', unsafe_allow_html=True)

    # TAB: Display more info about webpage
    with tab_info:
        st.write(task)
        # infost.write()

    # TAB: Display list of all tasks
    with tab_list:
        st.write(tasks)

    # Sidebar
    with st.sidebar:
        st.title('Webpage Annotations')
        st.sidebar.text_input('Webpage URL:', task_url)
        st.sidebar.multiselect('Select tags:', LABELS,
                               default=task_labels_current, key='selected_tags')

        # Navigation buttons
        with st.sidebar.container():
            col1, col2 = st.columns(2)
            col1.button('Previous', use_container_width=True,
                        on_click=go_to_prev_task)
            col2.button('Next', use_container_width=True,
                        on_click=go_to_next_task)

            st.sidebar.warning(
                """
                Please navigate through the list of untagged webpages below and
                classify them using the tag selector. To get started, simply click
                on a webpage in the list to display it in the iframe. Make sure to
                select a tag for each webpage before moving on to the next one.
                You can always go back and edit the tags if you need to.
                Thank you for your help with this annotation task!
                """
            )
