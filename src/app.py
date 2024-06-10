
# ===========================================================================
#                            Web Interface
# ===========================================================================

from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.keyboard_text import key, load_key_css
from components.welcome import WelcomePage
from dotenv import load_dotenv
from utils.local import *
from utils.files import *
from utils.content import *

import streamlit.components.v1 as components
import streamlit as st
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

load_key_css()

# Remove whitespace from the top of the page and sidebar
st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section > div > div {
            padding-top: 1em !important;
        }

        textarea {
            border: 1px solid rgba(49, 51, 63, 0.2) !important;
        }    

    </style>
    """, unsafe_allow_html=True)

# ================================= CONSTANTS ================================

LABELS = ['None', 'Hollow-Page', 'Listing-Page',
          'Article', "Paywall", "Login", "Cookie-Consent"]
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

# Show first webpage by default
if 'task_id' not in st.session_state:
    STATE.task_id = 0

if 'toggle_demo_modus' not in st.session_state:
    STATE.toggle_demo_modus = False

if 'last_task_reached' not in st.session_state:
    STATE.last_task_reached = False

if 'limit' not in st.session_state:
    STATE.limit = ast.literal_eval(os.getenv("LIMIT"))

if 'query' not in st.session_state:
    STATE.query = ast.literal_eval(os.getenv("QUERY"))

if 'sampling' not in st.session_state:

    param_sampling = params.get('sampling', None)

    if param_sampling:
        STATE.sampling = (param_sampling[0] == 'True')
    else:
        STATE.sampling = ast.literal_eval(os.getenv("SAMPLING"))


if 'fields' not in st.session_state:
    STATE.fields = ast.literal_eval(os.getenv("FIELDS"))

if 'demo_modus' not in st.session_state:
    STATE.demo_modus = False

if 'news_only' not in st.session_state:
    STATE.news_only = True

# Get tasks
if 'tasks' not in st.session_state:
    with st.spinner('Loding tasks...'):

        try:
            # STATE.query, STATE.fields, STATE.limit, STATE.sampling
            STATE.tasks = loadTasks()
            STATE.annotation_count = countAnnotations()
            # print(STATE.annotation_count)

        except Exception as e:
            st.error(f"{str(e)}")
            st.write("Query:")
            st.write(STATE.query)
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
    file_id = task.get('_id')

    if file_id:
        content = getPageContent(file_id)
        iframe_content = components.html(content, height=2048, scrolling=True)
    else:
        iframe_content.write(
            f'<iframe src="{url}" width="100%" height="1024px" style="border:none;"></iframe>', unsafe_allow_html=True)


def display_content():
    """ Display the webpage text content."""

    file_id = task.get('_id')

    text = extractText(file_id)

    if not text:
        st.warning("Couldn't extract any text! :worried:")
    
    st.write(text)

def display_cleaned_content():
    """ Display the cleaned webpage text content (trafilatura)."""

    file_id = task.get('_id')

    text = extractTextTrafilatura(file_id)

    if not text:
        st.warning("Couldn't extract any text! :worried:")
    
    st.write(text)


def save_annotations(task, annotator_id, annotations):
    """Save the annotations in the database for a given task """

    task_obj_id = task.get('_id')

    if not STATE.toggle_demo_modus:
        updateTask(task_obj_id, annotator_id, annotations)


def update_annotations():
    """Update the annotations for the current task."""

    try:
        task = STATE.tasks[STATE.task_id]
        annotations = task.setdefault("annotations", {})
        annotations[STATE.annotator_id] = {
            "comment": STATE.annotator_comment,
            "labels": STATE.selected_tags
        }
        save_annotations(task, STATE.annotator_id, annotations)
    except (KeyError, TypeError) as e:
        print("An error occurred while updating the task annotations:", e)


def go_to_next_task():
    """Advance to the next task."""
    update_annotations()
    if STATE.task_id < len(STATE.tasks) - 1:
        STATE.last_task_reached = False
        STATE.task_id += 1
    else:
        STATE.last_task_reached = True


def go_to_prev_task():
    """Go back to the previous task."""
    update_annotations()
    STATE.last_task_reached = False
    if STATE.task_id > 0:
        STATE.task_id -= 1


def select_annotation(class_name):
    """Select an annotation for the current task."""
    if class_name not in STATE.selected_tags:
        STATE.selected_tags.append(class_name)
    update_annotations()
    if STATE.task_id < len(STATE.tasks) - 1:
        STATE.last_task_reached = False
        STATE.task_id += 1
    else:
        STATE.last_task_reached = True


# ---------------------------------------------------------------------------
#                            Layout
# ---------------------------------------------------------------------------

# ================================= SETUP SCREEN ===============================
# Ask for annotator ID if not provided
if not STATE.annotator_id or not STATE.tasks:
    WelcomePage(st).show()

# ================================= MAIN SCREEN ===============================

else:

    if STATE.toggle_demo_modus:
        st.error("Demo modus is enabled. Annotations are not saved!", icon="🚨")

    if STATE.last_task_reached:
        st.error(
            "You reached the end of the list! To load a new batch of webpages, please refresh the page.", icon="🚨")

    # Tabs
    tab_names = ["Raw Text", "Cleaned Text", "Webpage Snapshot", "Task", "All Tasks"]
    tab_txt, tab_clean_txt, tab_snapshot, tab_info, tab_list = st.tabs(
        tab_names)

    # # Tabs
    # tab_names = ["More Info", "All Tasks"]
    # tab_info, tab_list = st.tabs(tab_names)

    with tab_txt:
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    overflow: hidden;
                }
                """,
        ):
            with st.spinner('Wait for it...'):
                with st.container():
                    display_content()
    
    with tab_clean_txt:
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    overflow: hidden;
                }
                """,
        ):
            with st.spinner('Wait for it...'):
                with st.container():
                    display_cleaned_content()
    
    # TAB: Display webpage snapshot
    with tab_snapshot:
        container = st.container()
        container.warning(
            "Please be aware that webpage snapshots may appear distorted.")
        container.iframe_content = st.empty()
        if st.button("Show Snapshot"):
            display_webpage(container.iframe_content, task)

    # TAB: Display more info about webpage
    with tab_info:
        st.write(task)

    # TAB: Display list of all tasks
    with tab_list:
        st.write(tasks)

    # Sidebar
    with st.sidebar:
        st.title(':pencil2: Webpage Annotations')
        st.warning(
            """
            Please navigate through the list of untagged webpages and
            classify them using the buttons bellow. Thanks!
            """
        )

        with stylable_container(
                key="current_page_info",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            box-shadow: 0 .125rem .25rem rgba(0,0,0,.075)!important;
                            background-color: #ffffff !important;
                        }
                        """,
        ):
            with st.container():
                st.text_area('Webpage URL:', task_url,
                             help="Landing URL of the scraped webpage")
                st.write(
                    f"<div style='text-align: center;'><p> <a href='{task_url}' target='_blank' rel='noopener noreferrer'>Open</a> or <a href='https://web.archive.org/web/{task_url}' target='_blank' rel='noopener noreferrer'>Open (archived)</a></p></div>", unsafe_allow_html=True)

            with st.expander("More about this Webpage"):
                st.text_area('Target URL:', target_url)
                # Navigation buttons
            with st.container():

                col1, col2 = st.columns(2)
                STATE.selected_tags = task.get('annotations', {}).get(
                    annotator_id, {}).get('labels', [])
                col1.button(':blue[Previous]', use_container_width=True,
                            on_click=go_to_prev_task)
                col2.button(':blue[Next]', use_container_width=True,
                            on_click=go_to_next_task)

                st.select_slider("Task:", options=range(
                    0, len(STATE.tasks)), format_func=(lambda x: ""), key="task_id", label_visibility="collapsed", help="Progress")

                count = sum([1 for task in STATE.tasks if task.get(
                    "annotations", {}).get(STATE.annotator_id, {})])
                st.caption(
                    f"Annotations: {STATE.annotation_count} before and {count} new")

        with stylable_container(
                key="tag_selection",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            box-shadow: 0 .125rem .25rem rgba(0,0,0,.075)!important;
                            background-color: #ffffff !important;
                        }
                        """,
        ):
            with st.container():

                STATE.current_comment = task.get('annotations', {}).get(
                    annotator_id, {}).get('comment', "")
                st.text_area('Comment:', value=STATE.current_comment,
                             key='annotator_comment',
                             on_change=update_annotations)
                st.button('Hollow Page', use_container_width=True,
                          on_click=select_annotation, args=("Hollow-Page",))
                st.button('Listing Page', use_container_width=True,
                          on_click=select_annotation, args=("Listing-Page",))
                st.button('Article', use_container_width=True,
                          on_click=select_annotation, args=("Article",))
                # st.button('None', use_container_width=True,
                #          on_click=select_annotation, args=("None",))
                st.multiselect(
                    'Selected Tags:', LABELS, key='selected_tags', on_change=update_annotations)

        with st.expander("Keyboard Shortcuts"):

            st.markdown("_Navigation:_")
            st.markdown(key("right", write=False) +
                        " Next Page", unsafe_allow_html=True)
            st.markdown(key("left", write=False) +
                        " Prev. Page", unsafe_allow_html=True)

            st.markdown("_Tag Selection:_")
            st.markdown(key("1", write=False) +
                        " Hollow Page", unsafe_allow_html=True)
            st.markdown(key("2", write=False) +
                        " Listing Page", unsafe_allow_html=True)
            st.markdown(key("3", write=False) +
                        " Aricle", unsafe_allow_html=True)

        with st.expander("More Options"):
            st.checkbox("Demo Modus", value=False,
                        key="toggle_demo_modus", help="If activated, annotations won't be saved.", label_visibility="visible")


components.html(
    """
    <script>
    var doc = window.parent.document;
    var buttons = doc.querySelectorAll('button > div > p');

    function clickButton(label) {
        buttons.forEach((pElement) => {
            if (pElement.innerText.includes(label)) {
                const buttonElement = pElement.closest("button");
                console.log(buttonElement);
                buttonElement.click();
            }
        });

    }

    doc.addEventListener('keydown', function(e) {
        console.log(e.keyCode); 
        switch (e.keyCode) {
            case 49: // (49 = 1)
                clickButton('Hollow Page');
                break;
            case 50: // (50 = 2)
                clickButton('Listing Page');
                break;
            case 51: // (51 = 3)
                clickButton('Article');
                break;
            case 52: // (52 = 4)
                clickButton('None');
                break;
            case 37: // (37 = left arrow)
                clickButton('Previous');
                break;
            case 39: // (39 = right arrow)
                clickButton('Next');
                break;
        }
    });
    </script>
    """,
    height=0,
    width=0,
)
