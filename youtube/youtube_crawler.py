import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

class YouTubeCrawler:
    def __init__(self, api_key):
        self.api_key = 'AIzaSyDWCtuQa0G-vueGmWK0MtypDzp0QbeDs78'
        self.base_url = "https://www.googleapis.com/youtube/v3/videos"

    def get_trending_music(self):
        params = {
            'part': 'snippet,contentDetails,statistics',
            'chart': 'mostPopular',
            'regionCode': 'US',  # Change to your target region
            'videoCategoryId': '10',  # Category ID for Music
            'maxResults': 50,
            'key': self.api_key
        }

        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            videos = response.json().get('items', [])

            trending_music = []
            for video in videos:
                video_info = {
                    'title': video['snippet']['title'],
                    'id': video['id'],
                    'channel': video['snippet']['channelTitle'],
                    'viewCount': video['statistics']['viewCount'],
                    'likeCount': video['statistics'].get('likeCount'), # Added
                    'commentCount': video['statistics'].get('commentCount'), # Added
                    
                }

               
                trending_music.append(video_info)
                print("videos:", trending_music)

            return trending_music
        else:
            print(f"Error fetching YouTube data: {response.status_code} - {response.text}")
            return []
        
        
    def get_video_comments(self, video_id):
        comments = []
        page_token = ''
        while True:
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'key': self.api_key,
                'maxResults': 100,
                'pageToken': page_token
            }

            response = requests.get(f"https://www.googleapis.com/youtube/v3/commentThreads", params=params)
            if response.status_code != 200:
                print(f"Error fetching comments: {response.status_code} - {response.text}")
                break

            data = response.json()
            for item in data.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'videoId': video_id,
                    'author': comment['authorDisplayName'],
                    'comment': comment['textDisplay'],
                    'likeCount': comment['likeCount'],
                    'dislikeCount': comment['dislikeCount'],
                    'publishedAt': comment['publishedAt']
                })

            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return comments


# Example usage
if __name__ == "__main__":
    youtube_api_key = 'AIzaSyDWCtuQa0G-vueGmWK0MtypDzp0QbeDs78'
    if youtube_api_key:
        youtube_crawler = YouTubeCrawler(api_key=youtube_api_key)
        trending_music = youtube_crawler.get_trending_music()
        print(f"Fetched {len(trending_music)} music videos")
    else:
        print("YouTube API key not found in environment variables.")