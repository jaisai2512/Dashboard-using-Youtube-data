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
  data_dict=[]
  for i in data['items']:
    data_dict.append(dict(Channel_Name=i['snippet']['title'],Description=i['snippet']['description'],subcribers=i['statistics']['subscriberCount'],videoCount=i['statistics']['videoCount'],viewCount=i['statistics']['viewCount'],uploads=i['contentDetails']['relatedPlaylists']['uploads']))
  df=pd.DataFrame(data_dict)
  playlistId=df.iloc[0,1]

  def get_video_id(youtube,playlistId):
    request = youtube.playlistItems().list(part="contentDetails",playlistId=playlistId,maxResults=50)
    response = request.execute()
    video_ids=[]
    for i in (response['items']):
        video_ids.append(i['contentDetails']['videoId'])
    next_page_token=response.get('nextPageToken')
    more_pages=True
    while more_pages:
        if next_page_token is None:
            more_pages=False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId =playlistId,
                maxResults=50,
                pageToken=next_page_token)
            response=request.execute()
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page_token=response.get('nextPageToken')
    return video_ids


  d=get_video_id(youtube,playlistId)

  def get_video_topic(youtube,d):
    video_data=[]
    for j in range(0,len(d),50):
        request = youtube.videos().list(part="snippet,statistics,topicDetails",id=",".join(d[j:j+50]))
        response = request.execute()
        for i in response['items']:
            data=dict(Tilte=i['snippet']['title'],Publishedat=i['snippet']['publishedAt'],Views=i['statistics']['viewCount'],like=i['statistics']['likeCount'] if 'likeCount' in i['statistics'] else 0 , comment=i['statistics']['commentCount'] if 'commentCount' in i['statistics'] else 0 , topic=i['topicDetails']['topicCategories'] if 'topicDetails' in i else None  )
            video_data.append(data)
    return video_data


  whole_data=get_video_topic(youtube,d)
  whole_data=pd.DataFrame(whole_data)

  whole_data['Views']=pd.to_numeric(whole_data['Views'])
  whole_data['like']=pd.to_numeric(whole_data['like'])
  whole_data['comment']=pd.to_numeric(whole_data['comment'])
  extra_date=whole_data['Publishedat']
  whole_data['Publishedat']=pd.to_datetime(whole_data['Publishedat'], format= '%Y/%m/%d')

  st.dataframe(whole_data)
  


