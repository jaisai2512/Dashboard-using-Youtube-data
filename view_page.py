import streamlit as st


class Multiapp():
  def __init__(self):
    self.apps=[]
    
  def add_app(self,title,function):
    self.apps.append({'title':title,'function':function})
    
  def run(self):
    app = st.sidebar.radio(
           'Navigation',
           self.apps,
           format_func=lambda app: app['title'])
    app['function']()
