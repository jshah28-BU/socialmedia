import pymongo
from pymongo import MongoClient
import pandas as pd
import json
import logging
from youtube_crawler import YouTubeCrawler

logging.basicConfig(level=logging.INFO)

class YouTubeClient:
    def __init__(self, mongo_uri, database_name, video_collection, comment_collection, api_key):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.video_collection = video_collection
        self.comment_collection = comment_collection
        self.crawler = YouTubeCrawler(api_key)

    def connect_db(self):
        client = MongoClient(self.mongo_uri)
        return client

    def insert_in_db(self, json_response, collection_name):
        try:
            myclient = self.connect_db()
            db = myclient.get_database(self.database_name)
            collection = db[collection_name]

            if isinstance(json_response, list):
                collection.insert_many(json_response)
            else:
                collection.insert_one(json_response)
        except Exception as e:
            logging.error(f"Error inserting in DB: {e}")

    def convert_dataframe_to_json(self, data_frame, collection_name):
        for i in range(len(data_frame)):
            json_df = data_frame.iloc[i].to_json()
            js = json.loads(json_df)
            self.insert_in_db(js, collection_name)

    def process_comments(self, video_id):
        try:
            response = self.crawler.get_video_comments(video_id)

            # Assuming get_video_comments returns a tuple (video_info, comments)
            if response and len(response) == 2:
                video_info, comments = response
                if comments:
                    enhanced_comments = [{'title': video_info['title'], 'videoId': video_info['videoId'], **comment} for comment in comments]
                    self.insert_in_db(enhanced_comments, self.comment_collection)
            else:
                logging.warning(f"Unexpected response format for video ID {video_id}")
        except Exception as e:
            logging.error(f"Error processing comments for video ID {video_id}: {e}")
    
    def main(self):
        try:
            trending_music = self.crawler.get_trending_music()
            if trending_music:
                df = pd.DataFrame(trending_music)
                self.convert_dataframe_to_json(df, self.video_collection)

                for video in trending_music:
                    self.process_comments(video['id'])
        except Exception as e:
            logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    youtube_api_key = 'AIzaSyDWCtuQa0G-vueGmWK0MtypDzp0QbeDs78'
    mongo_uri = 'mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/'
    database_name = 'YouTube_db'
    video_collection = 'trendingMusic'
    comment_collection = 'videoComments'

    youtube_client = YouTubeClient(mongo_uri, database_name, video_collection, comment_collection, youtube_api_key)
    youtube_client.main()
