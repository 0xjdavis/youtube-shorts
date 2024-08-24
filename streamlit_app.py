import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# Function to get SHORT videos from the YouTube channel
def get_youtube_short_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = []
    next_page_token = None
    
    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Maximum allowed value
            order="date",
            type="video",
            videoType="short",
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_data = {
                "Title": item['snippet']['title'],
                "Published At": item['snippet']['publishedAt'],
                "Video ID": item['id']['videoId'],
                "Video Type": "SHORT"
            }
            videos.append(video_data)
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return pd.DataFrame(videos)

# Setting page layout
st.set_page_config(
    page_title="YouTube Channel Short Videos List",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar for API Key and User Info
st.sidebar.header("About App")
st.sidebar.markdown('This app queries the YouTube API and returns a list of all SHORT videos for a particular YouTube channel. Created by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Calendly
st.sidebar.markdown("""
    <hr />
    <center>
    <div style="border-radius:8px;padding:8px;background:#fff";width:100%;">
    <img src="https://avatars.githubusercontent.com/u/98430977" alt="Oxjdavis" height="100" width="100" border="0" style="border-radius:50%"/>
    <br />
    <span style="height:12px;width:12px;background-color:#77e0b5;border-radius:50%;display:inline-block;"></span> <b>I'm available for new projects!</b><br />
    <a href="https://calendly.com/0xjdavis" target="_blank"><button style="background:#126ff3;color:#fff;border: 1px #126ff3 solid;border-radius:8px;padding:8px 16px;margin:10px 0">Schedule a call</button></a><br />
    </div>
    </center>
    <br />
""", unsafe_allow_html=True)

# Copyright
st.sidebar.caption("©️ Copyright 2024 J. Davis")

st.title("YouTube Channel Short Videos List")

api_key = st.secrets["youtube_key"]
channel_id = st.text_input("YouTube Channel ID", value="UCLRAP5fUb-OpHEiTryypa0g")

if st.button("Get Short Videos"):
    if api_key and channel_id:
        videos_df = get_youtube_short_videos(api_key, channel_id)
        st.dataframe(videos_df)
        csv = videos_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="youtube_short_videos.csv",
            mime="text/csv",
        )
    else:
        st.error("Please provide both API Key and Channel ID.")
