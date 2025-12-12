import streamlit as st

def sidebar_content():

    with st.sidebar:
        st.page_link("streamlit_app.py", label="Projects", icon="🏠")

        st.divider()
        st.page_link('pages/1_MMM_Simple.py')