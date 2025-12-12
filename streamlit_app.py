import streamlit as st
import pandas as pd
import altair as alt

from shared_components import sidebar_content

sidebar_content()
with st.container(border=True):

    # To center a button, you still need the columns method or custom CSS
    left_col, center_col, right_col = st.columns([1, 8, 1], vertical_alignment='center')
    with center_col:
        st.markdown(
            """
            #### MMM Projects

            1. MMM Simple - Small dataset with Facebook, Google Ads and TikTok channels.
            """
        )
