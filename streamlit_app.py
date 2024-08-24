import streamlit as stimport os
import json
from googleapiclient.discovery import build

# Replace with your API credentials and project ID
API_KEY = st.secrets["youtube_key]
#PROJECT_ID = 'your_project_id'

# Set up the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Prepare the video metadata
video_title = 'My Short Title'
video_description = 'My short video description'
video_tags = ['tag1', 'tag2']
video_categories = ['category1']

# Create the video
request_body = {
    'snippet': {
        'title': video_title,
        'description': video_description,
        'tags': video_tags,
        'categories': video_categories
    },
    'status': {
        'privacyStatus': 'public',
        'publicStatsViewable': True
    },
    'id': {
        'kind': 'youtube#video',
        'videoId': 'your_video_id'
    },
    'videoType': 'SHORT'
}

response = youtube.videos().insert(
    part='snippet,status,id',
    body=request_body
).execute()

print(response)
