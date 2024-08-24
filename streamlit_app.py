import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

api_key = st.secrets["youtube_key"] #st.text_input("Enter your YouTube API Key")

# Function to get YouTube Shorts videos
def get_youtube_short_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    search = []
    next_page_token = None
    
    try:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            videoDuration="short",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        search.extend(response['items'])
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break
        #except HttpError as e:
            #st.error(f'An error occurred: {e}')
            #break

        return search

        videos = []
        for item in response['items']:
            video = {
                'title': item['snippet']['title'],
                'video_id': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'published_at': item['snippet']['publishedAt']
            }
            videos.append(video)

        return pd.DataFrame(videos)
    except HttpError as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("YouTube Shorts Viewer")

# Input field
channel_id = st.text_input("YouTube Channel ID", value="UCLRAP5fUb-OpHEiTryypa0g")

if st.button("Fetch YouTube Shorts"):
    if api_key and channel_id:
        videos_df = get_youtube_short_videos(api_key, channel_id)
        
        if not videos_df.empty:
            st.success(f"Found {len(videos_df)} YouTube Shorts videos!")

            st.dataframe(videos_df)
            csv = videos_df.to_csv(index=False).encode('utf-8')
            
            # Display videos in a grid
            cols = st.columns(3)
            for index, video in videos_df.iterrows():
                with cols[index % 3]:
                    st.image(video['thumbnail'], use_column_width=True)
                    st.write(f"**{video['title']}**")
                    st.write(f"Published: {video['published_at']}")
                    video_url = f"https://www.youtube.com/shorts/{video['video_id']}"
                    st.markdown(f"[Watch Video]({video_url})")

        
        else:
            st.warning("No YouTube Shorts videos found for this channel.")
    else:
        st.warning("Please enter both the API Key and Channel ID.")

st.sidebar.header("About")
st.sidebar.info("This app fetches and displays YouTube Shorts videos from a specified channel using the YouTube Data API.")
