from googleapiclient.discovery import build
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import googleapiclient.errors
import plotly.express as px


st.set_page_config(page_title='Youtube Analysis',
                   page_icon=':bar_chart:',
                   layout='wide')

st.sidebar.header('Input here')
user_input = st.sidebar.text_input("Enter the channel Handle  Name:")




if user_input:

  api_key ="AIzaSyA8gdudsfXk1YcEDS42CyeSiD7zXA1KWhI"
  youtube = build('youtube','v3',developerKey=api_key)
  search_response = youtube.search().list(
    q=user_input,
    type='channel',
    part='id'
  ).execute()

  channel_id = search_response['items'][0]['id']['channelId']
  
  
  def get_channel_stats(youtube,channel_id):
    request = youtube.channels().list(part="snippet,contentDetails,statistics",id=channel_id)
    response = request.execute()
    return response
  data=get_channel_stats(youtube,channel_id)
  data_dict=[]
  for i in data['items']:
    data_dict.append(dict(Channel_Name=i['snippet']['title'],Description=i['snippet']['description'],subcribers=i['statistics']['subscriberCount'],videoCount=i['statistics']['videoCount'] ,viewCount=i['statistics']['viewCount'],uploads=i['contentDetails']['relatedPlaylists']['uploads'],thumbnail=i['snippet']['thumbnails']['default']['url'],localized=i['snippet']['country']))
  df=pd.DataFrame(data_dict)
  col5,col6,col7=st.columns(3)
  with col5:
    st.image(df.iloc[0,6],caption=None,width=200)
  with col6:
    st.markdown(f'<span style="font-size: 24px">{df.iloc[0,0]}</span>', unsafe_allow_html=True)
    with st.expander('Channel Description'):
      st.write(df.iloc[0,1])
  
  playlistId=df.iloc[0,5]
  df['videoCount']=pd.to_numeric(df['videoCount'])
  df['viewCount']=pd.to_numeric(df['viewCount'])
  df['subcribers']=pd.to_numeric(df['subcribers'])

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
            data=dict(Tilte=i['snippet']['title'],Publishedat=i['snippet']['publishedAt'],Views=i['statistics']['viewCount'] if 'viewCount' in i['statistics'] else 0 ,like=i['statistics']['likeCount'] if 'likeCount' in i['statistics'] else 0 , comment=i['statistics']['commentCount'] if 'commentCount' in i['statistics'] else 0 , topic=i['topicDetails']['topicCategories'] if 'topicDetails' in i else None  )
            video_data.append(data)
    return video_data


  whole_data=get_video_topic(youtube,d)
  whole_data=pd.DataFrame(whole_data)

  whole_data['Views']=pd.to_numeric(whole_data['Views'])
  whole_data['like']=pd.to_numeric(whole_data['like'])
  whole_data['comment']=pd.to_numeric(whole_data['comment'])
  extra_date=whole_data['Publishedat']
  whole_data['Publishedat']=pd.to_datetime(whole_data['Publishedat'])

  
  def million(value):
    if(value <1000):
      if('.0' in str(value)):
        return (str(round(value)))
      return (('{:.2f}'.format(value)))
    if(value<1000000 and value>=1000):
      k=value/1000
      if('.0' in str(k)):
        return (str(round(k))+'K')
      return (('{:.2f}'.format(k))+'K')
    if(value>=1000000 and value<1000000000):
      million=value/1000000
      if('.0' in str(million)):
        return (str(round(million))+'M')
      return (('{:.2f}'.format(million))+'M')
    if(value>=1000000000):
      billion=value/1000000000
      if('.0' in str(billion)):
        return (str(round(billion))+'B')
      return (('{:.2f}'.format(billion))+'B')
    return 's'
  whole_data=whole_data[whole_data['Tilte'].str.contains('shorts')==False]
  whole_data=whole_data[whole_data['Tilte'].str.contains('short')==False]
  top_10_videos=whole_data.head(20)
  top_10_videos=top_10_videos.reset_index()
  top_10_videos=top_10_videos.drop(['index'],axis=1)
    
  st.markdown('### Channel Info')
  col1, col2, col3= st.columns(3)
  col1.metric("Subcribers", million(df.iloc[0,2]))
  col2.metric("Total Views", million(df.iloc[0,4]))
  col3.metric("Total Videos",str(df.iloc[0,3]))
  col8,col9,col10=st.columns(3)
  whole_data['Year']=whole_data['Publishedat'].dt.year
  whole_data['Month']=whole_data['Publishedat'].dt.month
  whole_data['Day']=whole_data['Publishedat'].dt.day
  z=whole_data.groupby('Year')['Views'].sum()
  z=z.reset_index()
  average=(z['Views'].mean())/1000
  col8.metric("Average likes",million(top_10_videos['like'].mean()))
  col9.metric('Country',df.iloc[0,7])
  col10.metric('Yearly Revenue',million(round(average*0.2))+"-"+million(round(average*4.5)))
  
  import numpy as np
  import re
  arr=np.array(whole_data['topic'])
  l=[]
  for x in arr:
    if(x is not None):
        l.append(x[0])
    else:
        l.append('NaN')
  whole_data['Category']=l
  whole_data['Category']=whole_data['Category'].str.extract('([$a-zA-Z0-9_\-\().]+$)')
  
  
  

  options = ["Views", "like", "comment"]


  selected_option = st.selectbox("Overall ", options)
  names=whole_data['Tilte']

  if(selected_option=="Views"):
    plot=go.Figure()
    plot.add_trace(go.Scatter(
      name='Views',
      x=whole_data.iloc[:,1],
      y=whole_data.iloc[:,2],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Views: %{y}<extra></extra>',
      stackgroup='one'
    ))
    st.write(plot)
    options=['Last 20 Videos','Last 30 Videos']
    selectbox=st.selectbox('',options)
    if(selectbox==options[0]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'Views',
      x = whole_data.iloc[0:20,1],
      y = whole_data.iloc[0:20,2],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Views: %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:20,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    if(selectbox==options[1]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'Views',
      x = whole_data.iloc[0:30,1],
      y = whole_data.iloc[0:30,2],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Views: %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:30,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    a=whole_data.groupby('Category')['Views'].sum().sort_values(ascending=False)
    st.markdown('### Top three Category Based on Views')
    a=pd.DataFrame(a)
    a=a.reset_index()
    i=1
    for j in a['Category']:
      st.write(f'{i}. {j}')
      i=i+1
      if(i== 4):
        break
          
  if(selected_option=="like"):
    plot = go.Figure()
    plot.add_trace(go.Scatter(
    name = 'like',
    x = whole_data['Publishedat'],
    y = whole_data['like'],
    text=names,
    hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Likes: %{y}<extra></extra>',
    stackgroup='one'
    ))
    st.write(plot)
    options=['Last 20 Videos','Last 30 Videos']
    selectbox=st.selectbox('',options)
    if(selectbox==options[0]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'like',
      x = whole_data.iloc[0:20,1],
      y = whole_data.iloc[0:20,3],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Likes: %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:20,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    if(selectbox==options[1]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'like',
      x = whole_data.iloc[0:30,1],
      y = whole_data.iloc[0:30,3],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Likes %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:30,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    a=whole_data.groupby('Category')['like'].sum().sort_values(ascending=False)
    st.markdown('### Top three Category Based on Likes')
    a=pd.DataFrame(a)
    a=a.reset_index()
    i=1
    for j in a['Category']:
      st.write(f'{i}. {j}')
      i=i+1
      if(i== 4):
        break
  
  if(selected_option=="comment"):
    plot = go.Figure()
    plot.add_trace(go.Scatter(
    name = 'comment',
    x = whole_data['Publishedat'],
    y = whole_data['comment'],
    stackgroup='one'
    ))
    st.write(plot)
    options=['Last 20 Videos','Last 30 Videos']
    selectbox=st.selectbox('',options)
    if(selectbox==options[0]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'like',
      x = whole_data.iloc[0:20,1],
      y = whole_data.iloc[0:20,4],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Comments: %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:20,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    if(selectbox==options[1]):
      plot = go.Figure()
      plot.add_trace(go.Scatter(
      name = 'Comment',
      x = whole_data.iloc[0:30,1],
      y = whole_data.iloc[0:30,4],
      text=names,
      hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Comments %{y}<extra></extra>',
      stackgroup='one'
      ))
      dataframe=whole_data.iloc[0:30,[0,1,2,3,4]]
      dataframe=dataframe.reset_index(inplace = False)
      dataframe = dataframe.drop('index', axis=1)
      st.write(plot)
      st.dataframe(dataframe)
    a=whole_data.groupby('Category')['comment'].sum().sort_values(ascending=False)
    st.markdown('### Top three Category Based on Comment')
    a=pd.DataFrame(a)
    a=a.reset_index()
    i=1
    for j in a['Category']:
      st.write(f'{i}. {j}')
      i=i+1
      if(i== 4):
        break
  
  st.markdown('### All Time Favourites')
  d=whole_data.sort_values(by=['Views'],ascending=False)
  d=d.reset_index(inplace = False)
  d= d.drop('index', axis=1)
  st.dataframe(d.iloc[:6,[0,1,2,3,4,9]])
  
  
  
  
  
