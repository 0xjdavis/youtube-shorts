import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set up YouTube API client
API_KEY = st.secrets["youtube_key"]  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_playlists(channel_id):
    playlists = []
    next_page_token = None

    while True:
        try:
            request = youtube.playlists().list(
                part='snippet,contentDetails',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            playlists.extend(response['items'])
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break
        except HttpError as e:
            st.error(f'An error occurred: {e}')
            break

    return playlists

def get_playlist_videos(playlist_id):
    videos = []
    next_page_token = None

    while True:
        try:
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            videos.extend(response['items'])
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break
        except HttpError as e:
            st.error(f'An error occurred: {e}')
            break

    return videos


# Setting page layout
st.set_page_config(
    page_title="YouTube Playlist Explorer",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar for API Key and User Info
st.sidebar.header("About App")
st.sidebar.markdown('This is an app that queries the YouTube API and returns playlist for particular YouTube channel created by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

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

st.title('YouTube Playlist Explorer')

channel_id = st.text_input('Enter YouTube Channel ID')

if channel_id:
    playlists = get_playlists(channel_id)

    if playlists:
        st.write(f'Found {len(playlists)} playlists')

        for playlist in playlists:
            st.subheader(playlist['snippet']['title'])

            playlist_details = {
                'Playlist ID': playlist['id'],
                'Description': playlist['snippet']['description'],
                'Published At': playlist['snippet']['publishedAt'],
                'Item Count': playlist['contentDetails']['itemCount']
            }

            st.write('Playlist Details:')
            st.dataframe(pd.DataFrame([playlist_details]))

            videos = get_playlist_videos(playlist['id'])
            st.write(videos)
            
            if videos:
                video_data = [
                    {
                        'Video Title': video['snippet']['title'],
                        'Video ID': video['snippet']['resourceId']['videoId'],
                        'Published At': video['snippet']['publishedAt']
                    }
                    for video in videos
                ]

                st.write('Videos in this playlist:')
                st.dataframe(pd.DataFrame(video_data))
            else:
                st.write('No videos found in this playlist.')
    else:
        st.write('No playlists found for this channel.')
else:
    st.write('Please enter a YouTube Channel ID to explore its playlists and videos.')
