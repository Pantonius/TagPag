import streamlit as st
from utils.core import *
from utils.config import *

def return_home():
    st.switch_page("routes/main.py")

# get the task id from the query
if 'task_id' not in st.query_params:
    st.error("No task id was given!", icon="🚨")
    return_home()

task_id = st.query_params.task_id

# parse as number
if not task_id.isdigit():
    st.error("The task id is not numeric", icon="🚨")
    return_home()

task_id = int(task_id)

# load the task
tasks = load_tasks()
task = tasks[task_id]

# get the task id (as given by its _id field)
file_id = task[TASKS_ID_COLUMN]

# load the html file
html = get_page_content(file_id)

# render it to streamlit
st.html(html)