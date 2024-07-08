
# ===========================================================================
#                            Web Interface
# ===========================================================================

from streamlit_extras.keyboard_text import key, load_key_css
from components.welcome import WelcomePage
from utils.core import *
from utils.url_parser import explode_url
from utils.frontend_scripts import custom_css, custom_html

import streamlit.components.v1 as components
import streamlit as st
import ast
import os

# ------------------------------------------------------------------------------
#                                  Configuration
# ------------------------------------------------------------------------------

load_environment()

st.set_page_config(
    page_title="Webpage Annotations",
    layout="wide",
    page_icon="📄",
    initial_sidebar_state="expanded",
)

load_key_css()


# ================================= CONSTANTS ================================
LABELS = ['None', 'Hollow-Page', 'Listing-Page',
          'Article', "Paywall", "Login", "Cookie-Consent"]
TASKS = read_json_file("example_data.json")
STATE = st.session_state


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

# Get tasks
if 'tasks' not in st.session_state:
    with st.spinner('Loding tasks...'):

        try:
            STATE.tasks = loadTasks(STATE.annotator_id)

        except Exception as e:
            st.error(f"{str(e)}")
            exit()

# Shorthand variables
tasks = STATE.tasks
task = STATE.tasks[STATE.task_id]
annotator_id = STATE.annotator_id
task_url = STATE.tasks[STATE.task_id]['landing_url']
exploded_url = explode_url(task_url)

# ------------------------------------------------------------------------------
#                                    Functions
# ------------------------------------------------------------------------------


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
    else: 
        st.write(text)

def display_cleaned_content():
    """ Display the cleaned webpage text content (trafilatura)."""

    file_id = task.get('_id')

    text = extractTextTrafilatura(file_id)

    if not text:
        st.warning("Couldn't extract any text! :worried:")
    else:
        st.write(text)

def update_annotations():
    """Update the annotations for the current task."""
    update_task_annotations(STATE.annotator_id, STATE.tasks[STATE.task_id], STATE.selected_tags, STATE.current_comment)

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

def go_to_task():
    update_annotations()

    # the -1 is because of the offset, the list starts at 0 not at 1
    STATE.task_id = st.session_state.task_number_input - 1


def select_annotation(class_name):
    """Select an annotation for the current task."""
    if class_name not in STATE.selected_tags:
        STATE.selected_tags.append(class_name)
    else:
        STATE.selected_tags.remove(class_name)
    
    update_annotations()

    if STATE.auto_advance:
        if STATE.task_id < len(STATE.tasks) - 1:
            STATE.last_task_reached = False
            STATE.task_id += 1
        else:
            STATE.last_task_reached = True

def truncate_string(string, n=100):
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
                with st.container():
                    st.markdown("#### Cleaned")
                    display_cleaned_content()
            with raw_text:
                with st.container():
                    st.markdown("#### Raw")
                    display_content()
    
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
        st.write(task)

    # Sidebar
    with st.sidebar:
        st.title(':pencil2: Webpage Annotations')

        annotation = loadAnnotation(task.get('_id'), STATE.annotator_id)
        if annotation is not None and 'labels' in annotation:
            STATE.selected_tags = annotation['labels']
        else:
            STATE.selected_tags = []
        
        st.markdown(f"<div style='text-align: center'>(Task {STATE.task_id + 1} out of {len(STATE.tasks)})</div>", unsafe_allow_html=True)

        number = st.number_input(f"", value=STATE.task_id + 1, min_value=1, max_value=len(STATE.tasks), on_change=go_to_task, key="task_number_input", label_visibility='collapsed')

        st.button(':blue[Find next incomplete task]', use_container_width=True,
                    on_click=go_to_next_task, disabled=(STATE.selected_tags == []))

        st.divider()

        # get the current annotation
        file_id = task.get('_id')
        annotation = loadAnnotation(file_id, STATE.annotator_id)
        
        if annotation is not None:
            STATE.current_comment = annotation['comment']
            STATE.current_labels = annotation['labels']
        else:
            STATE.current_comment = ""
            STATE.current_labels = []
        
        st.checkbox("Auto-advance", key="auto_advance", value=False,  help="Automatically advance to the next task after selecting a tag.")

        st.toggle('1: Hollow Page', key="1",
                    on_change=select_annotation, args=("Hollow-Page",), value=("Hollow-Page" in STATE.selected_tags))
        st.toggle('2: Listing Page', key="2",
                    on_change=select_annotation, args=("Listing-Page",), value=("Listing-Page" in STATE.selected_tags))
        st.toggle('3: Article', key="3",
                    on_change=select_annotation, args=("Article",), value=("Article" in STATE.selected_tags))
        st.multiselect(
            'Selected Tags:', LABELS, key='selected_tags', on_change=update_annotations)
        
        st.text_area('Comment:', value=STATE.current_comment,
                        key='annotator_comment',
                        on_change=update_annotations)
    
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
                        " Article", unsafe_allow_html=True)

        # st.download_button( "Download Annotations", downloadAnnotations, "annotations.csv", mime="text/csv", key="download_annotations", use_container_width=True)


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
