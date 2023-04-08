from googleapiclient.discovery import build
import pandas as pd
import streamlit as st


st.set_page_config(page_title='Youtube Analysis',
                   page_icon=':bar_chart:',
                   layout='wide')

st.sidebar.header('Input her')
user_input = st.sidebar.text_input("Enter the channel code:")
