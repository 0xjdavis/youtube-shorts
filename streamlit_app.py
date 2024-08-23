import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

# Set up YouTube Data API client
API_KEY = st.secrets['youtube_key']  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_playlists(channel_id):
    playlists = []
    next_page_token = None

    while True:
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

    return playlists

def get_playlist_videos(playlist_id):
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        videos.extend(response['items'])
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return videos

st.title('YouTube Channel Playlist Explorer')

channel_id = st.text_input('Enter YouTube Channel ID')

if channel_id:
    playlists = get_channel_playlists(channel_id)

    for playlist in playlists:
        st.header(playlist['snippet']['title'])

        playlist_df = pd.DataFrame({
            'Playlist ID': playlist['id'],
            'Description': playlist['snippet']['description'],
            'Published At': playlist['snippet']['publishedAt'],
            'Item Count': playlist['contentDetails']['itemCount']
        }, index=[0])

        st.subheader('Playlist Details')
        st.dataframe(playlist_df)

        videos = get_playlist_videos(playlist['id'])
        video_data = []

        for video in videos:
            video_data.append({
                'Video Title': video['snippet']['title'],
                'Video ID': video['contentDetails']['videoId'],
                'Published At': video['snippet']['publishedAt'],
                'Description': video['snippet']['description']
            })

        video_df = pd.DataFrame(video_data)

        st.subheader('Videos in Playlist')
        st.dataframe(video_df)

st.sidebar.info('Enter a YouTube Channel ID to explore its playlists and videos.')
