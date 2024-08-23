import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests
import os
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="YouTube Playlist Analyzer", page_icon="📊")

# Function to get playlist items
def get_playlist_items(playlist_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet,contentDetails",
        "maxResults": 50,
        "playlistId": playlist_id,
        "key": api_key
    }
    
    all_items = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            st.error(f"Error: {data['error']['message']}")
            return None
        
        items = data.get("items", [])
        for item in items:
            video_id = item["contentDetails"]["videoId"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]
            all_items.append({"video_id": video_id, "title": title, "published_at": published_at})
        
        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            break
    
    return all_items

# Function to get video statistics
def get_video_statistics(video_ids, api_key):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": st.secrets["youtube_key"]
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        st.error(f"Error: {data['error']['message']}")
        return None
    
    return data.get("items", [])

# Function to parse duration
def parse_duration(duration):
    duration = duration.replace("PT", "")
    hours, minutes, seconds = 0, 0, 0
    if "H" in duration:
        hours, duration = duration.split("H")
        hours = int(hours)
    if "M" in duration:
        minutes, duration = duration.split("M")
        minutes = int(minutes)
    if "S" in duration:
        seconds = int(duration.replace("S", ""))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

# Function to display videos
def display_videos(videos_df):
    st.subheader("Videos in the Playlist")
    
    # Display total number of videos
    st.write(f"Total number of videos: {len(videos_df)}")
    
    # Display videos in a table
    st.dataframe(videos_df[["title", "views", "likes", "comments", "duration"]])
    
    # Create a bar chart of views for top 10 videos
    top_10_videos = videos_df.nlargest(10, "views")
    fig = px.bar(top_10_videos, x="title", y="views", title="Top 10 Videos by Views")
    fig.update_layout(xaxis_title="Video Title", yaxis_title="Views")
    st.plotly_chart(fig)

# Main function
def main():
    st.title("YouTube Playlist Analyzer")
    
    # Input fields for API key and Playlist ID
    api_key = st.text_input("Enter your YouTube API Key")
    playlist_id = st.text_input("Enter the Playlist ID")
    
    if st.button("Analyze Playlist"):
        if api_key and playlist_id:
            with st.spinner("Analyzing playlist..."):
                # Get playlist items
                playlist_items = get_playlist_items(playlist_id, api_key)
                
                if playlist_items:
                    # Get video statistics
                    video_ids = [item["video_id"] for item in playlist_items]
                    video_stats = get_video_statistics(video_ids, api_key)
                    
                    if video_stats:
                        # Create a DataFrame with video information
                        videos_df = pd.DataFrame(playlist_items)
                        videos_df["published_at"] = pd.to_datetime(videos_df["published_at"])
                        
                        # Add statistics to the DataFrame
                        for stat in video_stats:
                            video_id = stat["id"]
                            videos_df.loc[videos_df["video_id"] == video_id, "views"] = int(stat["statistics"].get("viewCount", 0))
                            videos_df.loc[videos_df["video_id"] == video_id, "likes"] = int(stat["statistics"].get("likeCount", 0))
                            videos_df.loc[videos_df["video_id"] == video_id, "comments"] = int(stat["statistics"].get("commentCount", 0))
                            videos_df.loc[videos_df["video_id"] == video_id, "duration"] = parse_duration(stat["contentDetails"]["duration"])
                        
                        # Display videos and statistics
                        display_videos(videos_df)
                        
                        # Additional analysis
                        st.subheader("Playlist Statistics")
                        
                        total_views = videos_df["views"].sum()
                        total_likes = videos_df["likes"].sum()
                        total_comments = videos_df["comments"].sum()
                        total_duration = videos_df["duration"].sum()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total Views", f"{total_views:,}")
                        col2.metric("Total Likes", f"{total_likes:,}")
                        col3.metric("Total Comments", f"{total_comments:,}")
                        col4.metric("Total Duration", str(total_duration))
                        
                        # Correlation heatmap
                        st.subheader("Correlation Heatmap")
                        correlation_df = videos_df[["views", "likes", "comments"]].copy()
                        correlation_df["duration"] = videos_df["duration"].dt.total_seconds()
                        correlation = correlation_df.corr()
                        
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(correlation, annot=True, cmap="coolwarm", ax=ax)
                        st.pyplot(fig)
                        
                        # Scatter plot: Views vs. Likes
                        st.subheader("Views vs. Likes")
                        fig = px.scatter(videos_df, x="views", y="likes", hover_data=["title"], trendline="ols")
                        st.plotly_chart(fig)
                        
                        # Publication date analysis
                        st.subheader("Video Publication Date Analysis")
                        videos_df["published_year"] = videos_df["published_at"].dt.year
                        videos_df["published_month"] = videos_df["published_at"].dt.to_period("M")
                        
                        fig = px.bar(videos_df["published_year"].value_counts().sort_index(), title="Videos per Year")
                        st.plotly_chart(fig)
                        
                        fig = px.line(videos_df.groupby("published_month").size().reset_index(name="count"), 
                                      x="published_month", y="count", title="Videos per Month")
                        fig.update_xaxes(tickformat="%Y-%m")
                        st.plotly_chart(fig)
                    else:
                        st.error("Failed to retrieve video statistics.")
                else:
                    st.error("Failed to retrieve playlist items.")
        else:
            st.warning("Please enter both the API Key and Playlist ID.")

if __name__ == "__main__":
    main()
