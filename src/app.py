import streamlit as st

# define pages
main_page = st.Page("routes/main.py", title="Annotator")
html_page = st.Page("routes/html.py", title="HTML Preview")

pg = st.navigation([main_page, html_page], position='hidden')

# run
pg.run()