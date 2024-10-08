import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

api_key = st.secrets["youtube_key"]

# Function to get YouTube Shorts videos
def get_youtube_short_videos(api_key, channel_id, max_results=100):
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = []
    next_page_token = None
    
    try:
        while len(videos) < max_results:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                videoDuration="short",
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                video = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return pd.DataFrame(videos)
    except HttpError as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("YouTube Shorts Viewer")

# Sidebar
st.sidebar.header("About")
st.sidebar.write("This app fetches and displays YouTube Shorts videos from a specified channel using the YouTube Data API.")

# Calendly
st.sidebar.markdown("""
    <hr />
    <center>
    <div style="border-radius:8px;padding:8px;background:#fff";width:100%;">
    <img src="https://avatars.githubusercontent.com/u/98430977" alt="Oxjdavis" height="100" width="100" border="0" style="border-radius:50%"/>
    <br />
    <span style="height:12px;width:12px;background-color:#77e0b5;border-radius:50%;display:inline-block;"></span> <b style="color:#000000">I'm available for new projects!</b><br />
    <a href="https://calendly.com/0xjdavis" target="_blank"><button style="background:#126ff3;color:#fff;border: 1px #126ff3 solid;border-radius:8px;padding:8px 16px;margin:10px 0">Schedule a call</button></a><br />
    </div>
    </center>
    <br />
""", unsafe_allow_html=True)

# Copyright
st.sidebar.caption("©️ Copyright 2024 J. Davis")


# Input fields
channel_id = st.text_input("YouTube Channel ID", value="UCLRAP5fUb-OpHEiTryypa0g")
max_results = st.number_input("Number of videos to fetch (max 500)", min_value=1, max_value=500, value=100)

if st.button("Fetch YouTube Shorts"):
    if api_key and channel_id:
        with st.spinner(f"Fetching up to {max_results} YouTube Shorts videos..."):
            videos_df = get_youtube_short_videos(api_key, channel_id, max_results)
        
        if not videos_df.empty:
            st.success(f"Found {len(videos_df)} YouTube Shorts videos!")
            
            # Display videos in a grid
            cols = st.columns(3)
            for index, video in videos_df.iterrows():
                with cols[index % 3]:
                    st.image(video['thumbnail'], use_column_width=True)
                    st.write(f"**{video['title']}**")
                    st.write(f"Published: {video['published_at']}")
                    video_url = f"https://www.youtube.com/shorts/{video['video_id']}"
                    st.markdown(f"[Watch Video]({video_url})")
            
            # Download button for CSV
            st.dataframe(videos_df)
            csv = videos_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="youtube_shorts_data.csv",
                mime="text/csv",
            )
        else:
            st.warning("No YouTube Shorts videos found for this channel.")
    else:
        st.warning("Please enter both the API Key and Channel ID.")
