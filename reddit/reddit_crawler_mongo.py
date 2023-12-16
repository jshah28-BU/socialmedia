import pymongo
import certifi
from reddit_client import RedditClient  # Ensure this is the correct path to your RedditClient class
from dotenv import load_dotenv
from faktory import Worker
import os
import time

load_dotenv()

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client['reddit_db']
subreddits_collection = db['subreddits']

reddit_client = RedditClient()

def save_to_mongo(data, collection_name):
    if data:
        print(f"Saving data to MongoDB collection: {collection_name}")
        db[collection_name].insert_many(data)
    else:
        print(f"No data to save for collection: {collection_name}")

def crawl_subreddit(subreddit):
    print(f"Crawling subreddit: {subreddit}")
    posts = reddit_client.get_movie_subreddit_data(subreddit)

    if posts:
        processed_posts = [process_post_data(post) for post in posts]
        print(f"Processed posts: {processed_posts}")
        save_to_mongo(processed_posts, subreddit)  # Use subreddit as collection name
        return processed_posts
    else:
        print(f"No posts found for subreddit: {subreddit}")
        return []

def process_post_data(post):
    data = post['data']
    return {
        'id': data['id'],
        'title': data['title'],
        'author': data['author'],
        'upvotes': data['ups'],
        'comments': data['num_comments'],
        'permalink': data['permalink'],
        'created_utc': data['created_utc']
        
    }

# Example usage
if __name__ == "__main__":
    w = Worker(queues=["crawl_subreddit"])
    w.register("crawl_subreddit", crawl_subreddit)
    w.run()
    time.sleep(60)
    
