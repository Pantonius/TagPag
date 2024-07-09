
# ===========================================================================
#                            Web Interface
# ===========================================================================

from streamlit_extras.keyboard_text import key, load_key_css
from components.welcome import WelcomePage
from utils.core import *
from utils.config import *
from utils.url_parser import explode_url
from utils.frontend_scripts import custom_css, custom_html

import streamlit.components.v1 as components
import streamlit as st
import ast
import os

# ------------------------------------------------------------------------------
#                                  Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Webpage Annotations",
    layout="wide",
    page_icon="📄",
    initial_sidebar_state="expanded",
)

load_key_css()

# create the directories if they don't exist
create_directories()


# ------------------------------------------------------------------------------
#                                 Set-up state
# ------------------------------------------------------------------------------

# Extract query parameters
params = st.query_params

# Set annotator ID if ANNOTATOR is not set
if 'annotator_id' not in st.session_state:
    STATE.annotator_id = os.getenv("ANNOTATOR")

# Show first webpage by default
if 'task_id' not in st.session_state:
    STATE.task_id = 0

if 'last_task_reached' not in st.session_state:
    STATE.last_task_reached = False

if 'demo_modus' not in st.session_state:
    STATE.demo_modus = False

if 'news_only' not in st.session_state:
    STATE.news_only = True

if 'reload_tasks' not in st.session_state:
    STATE.reload_tasks = False

# Get tasks
if 'tasks' not in st.session_state or STATE.reload_tasks:
    with st.spinner('Loding tasks...'):

        try:
            STATE.tasks = load_annotator_tasks(STATE.annotator_id)
            STATE.reload_tasks = False

        except Exception as e:
            st.error(f"{str(e)}")
            exit()

if 'cleaned_text' not in st.session_state:
    STATE.cleaned_text = ""

# Shorthand variables
tasks = STATE.tasks
task = STATE.tasks[STATE.task_id]
annotator_id = STATE.annotator_id
task_url = STATE.tasks[STATE.task_id][TASKS_URL_COLUMN]
exploded_url = explode_url(task_url)

# ------------------------------------------------------------------------------
#                                    Functions
# ------------------------------------------------------------------------------


def display_webpage(iframe_content: components.html, task):
    """
    Display the webpage content in an iframe.
    
    Args:
        iframe_content (streamlit.components.v1.html): The iframe component.
        task (dict): The task dictionary.
    
    Returns:
        None
    """

    url = task.get(TASKS_URL_COLUMN)
    file_id = task.get(TASKS_ID_COLUMN)

    if file_id:
        # if there is html content saved in the local storage, display that one directly
        content = get_page_content(file_id)
        iframe_content = components.html(content, height=2048, scrolling=True)
    else:
        # otherwise, display the webpage in an iframe
        iframe_content.write(
            f'<iframe src="{url}" width="100%" height="1024px" style="border:none;"></iframe>', unsafe_allow_html=True)


def display_raw_content():
    """
    Display the webpage text content ("Raw text"; selectolax)

    Args:
        None
    
    Returns:
        None
    """

    file_id = task.get(TASKS_ID_COLUMN)

    text = extract_raw_text(file_id)

    if not text:
        # if no text could be extracted, display a warning message
        st.warning("Couldn't extract any text! :worried:")
    else: 
        # otherwise, display the extracted text in a text area
        st.text_area('Raw text:', value=text, height=550, key='raw_text_area', disabled=True)

def save_cleaned_text():
    """
    Save the cleaned text to the session state.

    Args:
        None
    
    Returns:
        None
    """

    update_cleaned_text(task.get(TASKS_ID_COLUMN), STATE.cleaned_text)

def display_cleaned_content():
    """
    Display the cleaned webpage text content ("Cleaned text"; trafilatura).

    Args:
        None
    
    Returns:
        None
    """

    file_id = task.get(TASKS_ID_COLUMN)

    STATE.cleaned_text = extract_cleaned_text(file_id)

    if not STATE.cleaned_text:
        # if no text could be extracted, display a warning message
        st.warning("Couldn't extract any text! :worried:")
    else:
        # otherwise, display the extracted text in a text area
        st.text_area('Cleaned text:', value=STATE.cleaned_text, height=500, key='cleaned_text_area', on_change=save_cleaned_text)

def update_annotations():
    """
    Update the annotations for the current task.
    
    Args:
        None
    
    Returns:
        None
    """
    update_task_annotations(STATE.annotator_id, STATE.tasks[STATE.task_id], STATE.selected_tags, STATE.current_comment)

def go_to_next_task():
    """
    Advance to the next unannotated task. Wraps around if the end of the list is reached to look for unannotated tasks at the beginning of the list.
    Does not change the current task if all tasks have been annotated.

    Args:
        None
    
    Returns:
        None
    """

    # update the annotations for the current task
    update_annotations()

    # find the next task that has not been annotated yet
    for i in range(STATE.task_id + 1, len(STATE.tasks)):
        annotation = load_annotation(STATE.tasks[i].get('_id'), STATE.annotator_id)

        if annotation["labels"] == [] and annotation["comment"] == "":
            # if an unannotated task has been found, update the task_id and return
            STATE.task_id = i
            STATE.last_task_reached = False
            return
    
    # No task has been found between the current position and the end of the list
    # Search from the beginning to the current position
    for i in range(STATE.task_id):
        annotation = load_annotation(STATE.tasks[i].get(TASKS_ID_COLUMN), STATE.annotator_id)

        if annotation["labels"] == [] and annotation["comment"] == "":
            # if an unannotated task has been found, update the task_id and return
            STATE.task_id = i
            STATE.last_task_reached = False
            return

    # No task has been found -- all tasks have been annotated
    STATE.last_task_reached = True


def go_to_prev_task():
    """
    Go back to the previous task.
    
    Args:
        None

    Returns:
        None
    """
    
    # update the annotations for the current task
    update_annotations()

    # go back to the previous task
    STATE.last_task_reached = False
    if STATE.task_id > 0:
        STATE.task_id -= 1

def go_to_task():
    """
    Go to the task specified by the task number input.

    Args:
        None
    
    Returns:
        None
    """

    # update the annotations for the current task
    update_annotations()

    # the -1 is because of the offset, the list starts at 0 not at 1
    STATE.task_id = st.session_state.task_number_input - 1


def select_annotation(class_name: str):
    """
    Select an annotation for the current task.
    
    Args:
        class_name (str): The annotation class name.
    
    Returns:
        None
    """

    # toggle the annotation
    if class_name not in STATE.selected_tags:
        # add the class name to the selected tags, if it is not already in the list
        STATE.selected_tags.append(class_name)
    else:
        # otherwise remove the class name from the selected tags
        STATE.selected_tags.remove(class_name)
    
    # update the annotations for the current task
    update_annotations()

    # auto-advance to the next task if the auto-advance option is enabled
    if STATE.auto_advance:
        go_to_next_task()

def truncate_string(string: str, n=100):
    """
    Truncates a given string to a maximum length of n characters.

    Args:
        string (str): The string to truncate.
        n (int): The maximum length of the string.
    
    Returns:
        str: The truncated string
    """

    return string if len(string) < n else string[:n] + '...'


# ------------------------------------------------------------------------------
#                                    Layout
# ------------------------------------------------------------------------------


# ================================= SETUP SCREEN ===============================
# Ask for annotator ID if not provided
if not STATE.annotator_id or not STATE.tasks:
    WelcomePage(st).show()

# ================================= MAIN SCREEN ===============================
else:

    if STATE.last_task_reached:
        st.error(
            "You reached the end of the list! To load a new batch of webpages, please refresh the page.", icon="🚨")

    # Create a beta container to hold components in a horizontal layout
    row1_col1, row1_col2, = st.columns([1, 2]) 

    with row1_col1:

        _fqdn = f"**Domain**: {truncate_string(exploded_url['fqdn'])}"
        _path = f"  \n**Path**: {truncate_string(exploded_url['path'])}"
        _search_terms = f"  \n**Search terms**: {truncate_string(exploded_url['search_terms'])}" if exploded_url['search_terms'] != "" else ""

        st.info(f'{_fqdn}{_path}{_search_terms}  \n **:link: [Open link]({task_url})** | **[Open archive.org link](https://web.archive.org/web/{task_url})**')

    with row1_col2:
        st.info(f'**Full URL**: [{(task_url if len(task_url) < 450 else task_url[:450] + "..." )}]({task_url})')


    # Tabs
    tab_names = ["Text", "Webpage Snapshot", "URL Anatomy", "Task"]
    tab_txt, tab_snapshot, tab_url, tab_info = st.tabs(
        tab_names)

    ## TAB: Text Splitscreen (Cleaned Text, Raw Text)
    with tab_txt:
        with st.spinner('Wait for it...'):
            cleaned_text, raw_text = st.columns(2)

            with cleaned_text:
                display_cleaned_content()
                col1, col2, _ = st.columns([1,1,2])
                with col1:
                    st.button("Reset clean text", key="reset_cleaned_text", use_container_width=True)
                with col2:
                    st.button("Copy raw text", key="copy_raw_text", use_container_width=True)
            with raw_text:
                display_raw_content()
    
    # TAB: Display webpage snapshot
    with tab_snapshot:
        container = st.container()
        container.warning(
            "Please be aware that webpage snapshots may appear distorted.")
        container.iframe_content = st.empty()
        if st.button("Show Snapshot"):
            display_webpage(container.iframe_content, task)

    # TAB: Display URL Anatomy
    with tab_url:
        with st.container():
            st.write(exploded_url)

    # TAB: Display more info about webpage
    with tab_info:
        STATE.reload_tasks = True

        # update annotations in task
        st.write(task)

    # Sidebar
    with st.sidebar:
        st.title(':pencil2: Webpage Annotations')

        annotation = load_annotation(task.get(TASKS_ID_COLUMN), STATE.annotator_id)
        if annotation is not None and 'labels' in annotation:
            STATE.selected_tags = annotation['labels']
        else:
            STATE.selected_tags = []
        
        st.markdown(f"<div style='text-align: center'>(Task {STATE.task_id + 1} out of {len(STATE.tasks)})</div>", unsafe_allow_html=True)

        number = st.number_input("task_number", value=STATE.task_id + 1, min_value=1, max_value=len(STATE.tasks), on_change=go_to_task, key="task_number_input", label_visibility='collapsed')

        st.button(':blue[Find next incomplete task]', use_container_width=True,
                    on_click=go_to_next_task, disabled=(STATE.selected_tags == []), help="Find the next task that has not been annotated yet.")


        # get the current annotation
        file_id = task.get(TASKS_ID_COLUMN)
        annotation = load_annotation(file_id, STATE.annotator_id)
        
        if annotation is not None:
            STATE.current_comment = annotation['comment']
            STATE.current_labels = annotation['labels']
        else:
            STATE.current_comment = ""
            STATE.current_labels = []
        
        st.checkbox("Auto-advance", key="auto_advance", value=False,  help="Automatically advance to the next task after selecting a tag.")

        # create the streamlit columns
        col1, col2 = st.columns(2)

        # create a variable _LABELS with maximum 10 labels
        _LABELS = LABELS[:10]

        with col1:
            # display a togle button for each label in the first half of LABELs, they must start with a number followed by a colon
            for number, label in enumerate(_LABELS[:(len(_LABELS) + 1)//2]):
                st.toggle(f"{number + 1}: {label}", key=f"{number + 1}",
                            on_change=select_annotation, args=(label,), value=(label in STATE.selected_tags))
        with col2:
            # display a togle button for each label in the second half of _LABELs, they must start with a number followed by a colon
            for number, label in enumerate(_LABELS[(len(_LABELS) + 1)//2:], (len(_LABELS) + 1)//2):
                st.toggle(f"{str(number + 1)[-1]}: {label}", key=f"{str(number + 1)[-1]}",
                            on_change=select_annotation, args=(label,), value=(label in STATE.selected_tags))


        st.multiselect(
            'Selected Tags:', LABELS, key='selected_tags', on_change=update_annotations)
        
        st.text_area('Comment:', value=STATE.current_comment,
                        key='annotator_comment',
                        on_change=update_annotations)
    
        with st.expander("Keyboard Shortcuts"):

            st.markdown("_Navigation:_")

            # create two streamlit columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(key("right", write=False) +
                            " Next Page", unsafe_allow_html=True)
            with col2:
                st.markdown(key("left", write=False) +
                            " Prev. Page", unsafe_allow_html=True)

            st.markdown(key("F | f", write=False) +
                        " Find next incomplete task", unsafe_allow_html=True)

            st.markdown("_Tag Selection:_")

            # create two streamlit columns
            col1, col2 = st.columns(2)

            with col1:
                # display a markdown label for each label in the first half of LABELs
                for number, label in enumerate(_LABELS[:(len(_LABELS) + 1)//2]):
                    st.markdown(key(str(number + 1), write=False) +
                                f" {label}", unsafe_allow_html=True)
                    
            with col2:
                # display a markdown label for each label in the second half of LABELs
                for number, label in enumerate(_LABELS[(len(_LABELS) + 1)//2:], (len(_LABELS) + 1)//2):
                    st.markdown(key(str(number + 1)[-1], write=False) +
                                f" {label}", unsafe_allow_html=True)

        st.download_button( "Download Annotations", download_annotations(), "annotations.csv", mime="text/csv", key="download_annotations", use_container_width=True)


# ------------------------------------------------------------------------------
#                              Front-end injections
# ------------------------------------------------------------------------------

# HTML injections
components.html(
    custom_html,
    height=0,
    width=0,
)


# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)
