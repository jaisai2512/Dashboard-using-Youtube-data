from googleapiclient.discovery import build
import pandas as pd
import streamlit as st


st.set_page_config(page_title='Youtube Analysis',
                   page_icon=':bar_chart:',
                   layout='wide')

st.sidebar.header('Input her')
user_input = st.sidebar.text_input("Enter the channel code:")


if user_input:
  api_key ="AIzaSyA8gdudsfXk1YcEDS42CyeSiD7zXA1KWhI"
  youtube = build('youtube','v3',developerKey=api_key)
  
  
  def get_channel_stats(youtube,channel_id):
    request = youtube.channels().list(part="snippet,contentDetails,statistics",id=channel_id)
    response = request.execute()
    return response
  data=get_channel_stats(youtube,user_input)
  st.write(data)
  


