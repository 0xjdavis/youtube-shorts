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
