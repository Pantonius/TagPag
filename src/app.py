
# ===========================================================================
#                            Web Interface
# ===========================================================================

from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.keyboard_text import key, load_key_css
from components.welcome import WelcomePage
from utils.environment import load
from utils.local import *
from utils.files import *
from utils.content import *
from utils.url_parser import explode_url

import streamlit.components.v1 as components
import streamlit as st
import ast
import os

# ===========================================================================
#                               Config
# ===========================================================================

load()

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

# ================================= INIT STATE ===============================

# Extract query parameters
params = st.query_params

# Set annotator ID if ANNOTATOR is not set
if 'annotator_id' not in st.session_state:
    STATE.annotator_id = os.getenv("ANNOTATOR")
    print("Annotator ID:", STATE.annotator_id)

# Set task mongodb object ID
if 'task_object_id' not in st.session_state:
    STATE.task_object_id = "63e6b1425b2943de553ee687"

# Show first webpage by default
if 'task_id' not in st.session_state:
    STATE.task_id = 0

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


def save_annotation(task, annotator_id, annotation):
    """Save the annotations for a given task """

    task_obj_id = task.get('_id')

    updateTask(task_obj_id, annotator_id, annotation)


def update_annotations():
    """Update the annotations for the current task."""

    try:
        task = STATE.tasks[STATE.task_id]
        annotation = loadAnnotation(task.get('_id'), STATE.annotator_id)

        if annotation is None:
            annotation = {
                'annotator_id': STATE.annotator_id,
                'labels': [],
                'comment': ""
            }
        
        # add the selected tags to the annotation
        annotation['labels'] = STATE.selected_tags

        # add the comment to the annotation
        annotation['comment'] = STATE.current_comment

        save_annotation(task, STATE.annotator_id, annotation)
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

    if STATE.auto_advance:
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

    if STATE.last_task_reached:
        st.error(
            "You reached the end of the list! To load a new batch of webpages, please refresh the page.", icon="🚨")
        

    with st.container():
        st.info(f'**Webpage URL**: [{(task_url if len(task_url) < 500 else task_url[:500] + "..." )}]({task_url})  \n **:link: [Open link]({task_url})** | **[Open archive.org link](https://web.archive.org/web/{task_url})**')

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
                    st.header("Cleaned Text")
                    display_cleaned_content()
            with raw_text:
                with st.container():
                    st.header("Raw Text")
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
            st.header("URL Anatomy")
            st.write(explode_url(task_url))

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

        # Create a beta container to hold components in a horizontal layout
        row1_col1, row1_col2, row1_col3 = st.columns([1, 3, 1])

        # Components in the first row
        with row1_col1:
            st.button('&lt;', on_click=go_to_prev_task)

        with row1_col2:
            st.select_slider("Task:", options=range(
                0, len(STATE.tasks)), format_func=(lambda x: ""), key="task_id", label_visibility="collapsed", help="Progress")

        with row1_col3:
            st.button('&gt;', on_click=go_to_next_task)

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

        st.button('1: Hollow Page', use_container_width=True,
                    on_click=select_annotation, args=("Hollow-Page",))
        st.button('2: Listing Page', use_container_width=True,
                    on_click=select_annotation, args=("Listing-Page",))
        st.button('3: Article', use_container_width=True,
                    on_click=select_annotation, args=("Article",))
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

        st.download_button( "Download Annotations", downloadAnnotations(), "annotations.csv", mime="text/csv", key="download_annotations", use_container_width=True)

components.html(
    """
    <script>
    var doc = window.parent.document;
    var buttons = doc.querySelectorAll('button > div > p');

    function clickButton(label) {
        buttons.forEach((pElement) => {
            console.log(label)
            console.log(pElement.innerText)
            if (pElement.innerText.startsWith(label)) {
                const buttonElement = pElement.closest("button");
                console.log(buttonElement);
                buttonElement.click();
            }
        });

    }

    doc.addEventListener('keydown', function(e) {
    
        // Check if the key code is between 49 (key '1') and 59 (key ':')
        if (e.keyCode >= 49 && e.keyCode <= 59) {
            // Calculate the corresponding button string
            const keyChar = String.fromCharCode(e.keyCode);
            clickButton(`${keyChar}:`);
        }

        switch (e.keyCode) {
            case 37: // (37 = left arrow)
                clickButton('<');
                break;
            case 39: // (39 = right arrow)
                clickButton('>');
                break;
        }
    });
    </script>
    """,
    height=0,
    width=0,
)



# Define your custom CSS
custom_css = """
<style>
header, footer, [data-testid="stSidebarHeader"] {
  visibility: hidden;
  display: none;
}
.main .block-container {
  padding: 0rem 2rem 0rem 2rem;
}
#root > div:nth-child(1) > div.withScreencast > div > div > div > section > div > div {
  padding-top: 0em !important;
}
.stAlert a {
word-break: break-all;
}
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)
