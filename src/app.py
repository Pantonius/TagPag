
# ===========================================================================
#                            Web Interface
# ===========================================================================

import streamlit.components.v1 as components
import streamlit as st
from utils.database import *
from utils.files import *
from components.welcome import WelcomePage
from dotenv import load_dotenv
import ast
import os

# ================================= CONFIG ================================

load_dotenv()

# database_name = os.getenv("DATABASE_NAME")

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

# Sgow first webpage by default
if 'task_id' not in st.session_state:
    STATE.task_id = 0

# Get tasks
if 'tasks' not in st.session_state:
    with st.spinner('Loding tasks...'):

        # Load environment variables
        query = ast.literal_eval(os.getenv("QUERY"))
        fields = ast.literal_eval(os.getenv("FIELDS"))
        limit = ast.literal_eval(os.getenv("LIMIT"))
        sampling = ast.literal_eval(os.getenv("SAMPLING"))

        try:
            STATE.tasks = fetchTasks(db, query, fields, limit, sampling)
        except Exception as e:
            st.error(f"{str(e)}")
            st.write("Query:")
            st.write(query)
            exit()


# Shorthand variables
tasks = STATE.tasks
task = STATE.tasks[STATE.task_id]
annotator_id = STATE.annotator_id
task_url = STATE.tasks[STATE.task_id]['landing_url']
target_url = STATE.tasks[STATE.task_id]['target_url']

# ================================= FUNCTIONS ===============================


def display_webpage(iframe_content, task):
    """ Display the webpage content in an iframe."""
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
    """Save the annotations in the database for a given task """

    task_obj_id = task.get('_id')

    # TODO: Commented out for testing purposes
    # if task_obj_id:
    #    updateTask(db, task_obj_id, annotator_id, annotations)


def update_annotations():
    """Update the annotations for the current task."""

    try:
        task = STATE.tasks[STATE.task_id]
        annotations = task.setdefault("annotations", {})
        annotations[STATE.annotator_id] = {
            "labels": STATE.selected_tags
        }
        save_annotations(task, STATE.annotator_id, annotations)
    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)


def go_to_next_task():
    """Advance to the next task."""
    update_annotations()
    STATE.task_id += 1


def go_to_prev_task():
    """Go back to the previous task."""
    update_annotations()
    STATE.task_id -= 1


def select_annotation(class_name):
    """Select an annotation for the current task."""
    if class_name not in STATE.selected_tags:
        STATE.selected_tags.append(class_name)
    update_annotations()
    STATE.task_id += 1


# ---------------------------------------------------------------------------
#                            Layout
# ---------------------------------------------------------------------------


# ================================= SETUP SCREEN ===============================

# Ask for annotator ID if not provided
if not STATE.annotator_id or not STATE.tasks:

    WelcomePage(st).show()

# ================================= MAIN SCREEN ===============================

else:

    # # Tabs
    # tab_names = ["Snapshot", "Current", "More Info", "All Tasks"]
    # tab_snapshot, tab_current, tab_info, tab_list = st.tabs(tab_names)

    # # TAB: Display webpage snapshot
    # with tab_snapshot:
    #     container = st.container()
    #     container.warning(
    #         "Please be aware that webpage snapshots may appear distorted.")
    #     container.iframe_content = st.empty()
    #     display_webpage(container.iframe_content, task)

    # # TAB: Display current version of webpage
    # with tab_current:
    #     st.warning(
    #         'If the webpage is not loading properly, please open it in a new tab to ensure proper functionality.')
    #     st.write(
    #         f'<iframe src="{task_url}" width="100%" height="1024px" style="border:none;"></iframe>', unsafe_allow_html=True)

    # Tabs
    tab_names = ["More Info", "All Tasks"]
    tab_info, tab_list = st.tabs(tab_names)

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
        st.sidebar.text_area('Webpage URL:', task_url)
        with st.sidebar.expander("More Infos"):
            st.text_area('Target URL:', target_url)

        STATE.selected_tags = task.get('annotations', {}).get(
            annotator_id, {}).get('labels', [])
        st.sidebar.multiselect(
            'Select tags:', LABELS, key='selected_tags', on_change=update_annotations)

        st.button('Login', use_container_width=True,
                  on_click=select_annotation, args=("Login",))
        st.button('Paywall', use_container_width=True,
                  on_click=select_annotation, args=("Paywall",))
        st.button('Cookie Consent', use_container_width=True,
                  on_click=select_annotation, args=("Cookie consent",))
        st.button('None', use_container_width=True,
                  on_click=select_annotation, args=("None",))

        # Navigation buttons
        with st.sidebar.container():
            col1, col2 = st.columns(2)
            col1.button('Previous', use_container_width=True,
                        on_click=go_to_prev_task)
            col2.button('Next', use_container_width=True,
                        disabled=STATE.selected_tags == [],
                        on_click=go_to_next_task)

            st.warning(
                """
                Please navigate through the list of untagged webpages below and
                classify them using the tag selector. To get started, simply click
                on a webpage in the list to display it in the iframe. Make sure to
                select a tag for each webpage before moving on to the next one.
                You can always go back and edit the tags if you need to.
                Thank you for your help with this annotation task!
                """
            )
