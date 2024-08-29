# ===========================================================================
#                            Web Interface
# ===========================================================================

from streamlit_extras.keyboard_text import key, load_key_css
from components.welcome import WelcomePage
from utils.core import *
from utils.config import *
from utils.db import initialize_db
from utils.url_parser import explode_url
from utils.frontend_scripts import custom_css, custom_html

import streamlit.components.v1 as components
import streamlit as st
import validators
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

# initialize the database
initialize_db()

# ------------------------------------------------------------------------------
#                                 Set-up state
# ------------------------------------------------------------------------------

# Extract query parameters
params = st.query_params

# Set annotator ID if ANNOTATOR is not set
if 'annotator_id' not in STATE:
    STATE.annotator_id = os.getenv("ANNOTATOR")

# Show first webpage by default
if 'task_id' not in STATE:
    STATE.task_id = 0

if 'last_task_reached' not in STATE:
    STATE.last_task_reached = False

if 'reload_tasks' not in STATE:
    STATE.reload_tasks = False

# Get tasks
if 'tasks' not in STATE or STATE.reload_tasks:
    with st.spinner('Loding tasks...'):

        try:
            STATE.tasks = load_annotator_tasks(STATE.annotator_id)
            STATE.reload_tasks = False

        except Exception as e:
            st.error(f"{str(e)}")
            exit()

if 'cleaned_text' not in STATE:
    STATE.cleaned_text = ""

if 'refresh_counter' not in STATE:
    STATE.refresh_counter = 0

# Shorthand variables
tasks = STATE.tasks
task = STATE.tasks[STATE.task_id]
annotator_id = STATE.annotator_id
task_url = STATE.tasks[STATE.task_id][TASKS_URL_COLUMN]
exploded_url = explode_url(task_url)

# ------------------------------------------------------------------------------
#                                    Functions
# ------------------------------------------------------------------------------

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
    
    STATE.cleaned_text = STATE.cleaned_text_area
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

    STATE.cleaned_text = load_cleaned_text(file_id)

    if not STATE.cleaned_text: # if the cleaned text is still not loaded, signal a problem to the user
        # if no text could be extracted, display a warning message
        st.warning("Couldn't extract any text! :worried:")
    else:
        # otherwise, display the extracted text in a text area
        st.text_area('Cleaned text:', value=STATE.cleaned_text, height=500, key='cleaned_text_area', on_change=save_cleaned_text)

def reset_cleaned_text():
    """
    Reset the cleaned text to the original value.

    Args:
        None
    
    Returns:
        None
    """

    STATE.cleaned_text = extract_cleaned_text(task.get(TASKS_ID_COLUMN)) # update text area and update file (extract_cleaned_text automatically updates the file after extraction)

def copy_raw_text():
    """
    Copy the raw text to the cleaned text area.

    Args:
        None
    
    Returns:
        None
    """

    STATE.cleaned_text = STATE.raw_text_area # update text area
    update_cleaned_text(task.get(TASKS_ID_COLUMN), STATE.cleaned_text) # update file

def update_annotations():
    """
    Update the annotations for the current task.
    
    Args:
        None
    
    Returns:
        None
    """
    STATE.current_comment = STATE.annotator_comment
    update_task_annotations(STATE.annotator_id, STATE.tasks[STATE.task_id], STATE.selected_labels, STATE.current_comment)

def find_next_unannotated_task():
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

def go_to_next_task():
    """
    Go to the next task.

    Args:
        None

    Returns:
        None
    """

    # update the annotations for the current task
    update_annotations()

    # go to the next task
    if STATE.task_id < len(STATE.tasks) - 1:
        STATE.last_task_reached = False
        STATE.task_id += 1
    else:
        STATE.last_task_reached = True


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
    STATE.task_id = STATE.task_number_input - 1


def select_annotation(class_name: str, key: str):
    """
    Select an annotation for the current task.
    
    Args:
        class_name (str): The annotation class name.
        key (str): The key of the annotation.
    
    Returns:
        None
    """

    # toggle the annotation
    if class_name not in STATE.selected_labels:
        # add the class name to the selected labels, if it is not already in the list
        STATE.selected_labels.append(class_name)
    else:
        # otherwise remove the class name from the selected labels
        STATE.selected_labels.remove(class_name)
    
    # update the annotations for the current task
    update_annotations()


    # auto-advance to the next task if the auto-advance option is enabled
    if STATE.auto_advance:

        go_to_next_task()

        # delete the key from the session state to avoid odd behaviours
        del STATE[key]

        # Increment the counter when you want to refresh: %2 is enough, but %10 would allow
        # for oddities
        STATE.refresh_counter = (STATE.refresh_counter + 1) % 10

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
            "You reached the end of the list!", icon="🚨")

    if not validators.url(task_url):
        st.error(f"Invalid URL! :worried: Please check that the URLs in your file are well formed. The scheme (http:// or https://) is required.")
        st.error(f'**URL**: {task_url[:500]}')

    else:
        fancy_url = highlight_url(exploded_url, 400)

        links = f'**:link: [Open link]({task_url})** | **[Open archive.org link](https://web.archive.org/web/{task_url})** | **[Open saved version](/html?task_id={STATE.task_id})**'
        
        st.info(f"[{fancy_url}]({task_url}) \n\n {links}")

    # Tabs
    tab_names = ["Text", "URL Anatomy", "Task"]
    tab_txt, tab_url, tab_info = st.tabs(
        tab_names)

    ## TAB: Text Splitscreen (Cleaned Text, Raw Text)
    with tab_txt:
        with st.spinner('Wait for it...'):
            cleaned_text, raw_text = st.columns(2)

            with cleaned_text:
                display_cleaned_content()
                col1, col2 = st.columns([1,1])
                with col1:
                    st.button("Reset Clean Text", key="reset_cleaned_text", use_container_width=True, on_click=reset_cleaned_text)
                with col2:
                    st.button("Copy Raw Text", key="copy_raw_text", use_container_width=True, on_click=copy_raw_text)
            with raw_text:
                display_raw_content()

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
            STATE.selected_labels = annotation['labels']
        else:
            STATE.selected_labels = []
        
        st.markdown(f"<div style='text-align: center'>(Task {STATE.task_id + 1} out of {len(STATE.tasks)})</div>", unsafe_allow_html=True)

        st.number_input(
            "Task number",
            value=STATE.task_id + 1,
            min_value=1,
            max_value=len(STATE.tasks),
            on_change=go_to_task,
            key="task_number_input",
            label_visibility="collapsed",
        )
        
        st.button(
            "Find next incomplete task",
            use_container_width=True,
            on_click=find_next_unannotated_task,
            disabled=not STATE.selected_labels,
            key="find_next_task",
            help=(
                "Current task has not been annotated yet." if not STATE.selected_labels else
                "Find the next task that has not been annotated yet."
            ),
        )


        # get the current annotation
        file_id = task.get(TASKS_ID_COLUMN)
        annotation = load_annotation(file_id, STATE.annotator_id)
        
        if annotation is not None:
            # try to get the current comment and labels from the annotation
            STATE.current_comment = annotation['comment'] if 'comment' in annotation else ""
            STATE.current_labels = annotation['labels'] if 'labels' in annotation else []
        else:
            # if no annotation is found, set the current comment and labels to be empty
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
                st.toggle(f"{number + 1}: {label}", key=f"{number + 1}_{STATE.refresh_counter}",
                            on_change=select_annotation, args=(label, f"{number + 1}_{STATE.refresh_counter}"), 
                            value=(label in STATE.selected_labels))
        with col2:
            # display a togle button for each label in the second half of _LABELs, they must start with a number followed by a colon
            for number, label in enumerate(_LABELS[(len(_LABELS) + 1)//2:], (len(_LABELS) + 1)//2):
                st.toggle(f"{str(number + 1)[-1]}: {label}", key=f"{str(number + 1)[-1]}_{STATE.refresh_counter}",
                            on_change=select_annotation, args=(label, f"{number + 1}_{STATE.refresh_counter}"), 
                            value=(label in STATE.selected_labels))


        st.multiselect(
            'Selected Labels:', LABELS, key='selected_labels', on_change=update_annotations)
        
        st.text_area('Comment:', value=STATE.current_comment,
                        key='annotator_comment',
                        on_change=update_annotations)
    
        with st.expander("Keyboard shortcuts"):

            st.caption("Disabled if keyboard focus is on a text area field.")
            
            st.markdown("_Navigation:_")

            st.markdown(key("w | . | + | ] | Enter", write=False) +
                        " Next", unsafe_allow_html=True)
            st.markdown(key("q | , | - | [ | Backspace", write=False) +
                        " Previous", unsafe_allow_html=True)

            st.markdown(key("F | f | =", write=False) +
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