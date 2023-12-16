import requests
import os
from dotenv import load_dotenv
import pymongo
from datetime import datetime

# Load environment variables
load_dotenv()

class RedditClient:
    def __init__(self):
        self.client_id = 'ybbMEhdt1hG6K7HESV1ElQ'
        self.secret_key = 'nqvrDAfJjk71T-QUBEa3fIzVJVHEkQ'
        self.username = 'Separate-Access-7934'
        self.password = 'Datahunters@88'
        self.user_agent = 'MyBot vs 0.0.1'
        self.token = self.get_reddit_auth()



    def get_reddit_auth(self):
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.secret_key)
            data = {'grant_type': 'password', 'username': self.username, 'password': self.password}
            headers = {'User-Agent': self.user_agent}
            res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)

            #print("Response Status Code:", res.status_code)
            #print("Response Body:", res.text)

            if res.status_code != 200:
                raise Exception("Failed to authenticate with Reddit API.")

            return res.json()['access_token']


    def get_music_subreddit_data(self, subreddit):
        headers = {'User-Agent': self.user_agent}
        url = f'https://www.reddit.com/r/{subreddit}/top.json?limit=10'  # Adjust limit as needed
        response = requests.get(url, headers=headers)
        print(f"Fetching data from subreddit: {subreddit}")
        print(f"Response Status Code: {response.status_code}")

        if response.status_code != 200:
            print("Error fetching subreddit data:")
            print("Response Body:", response.text)
            return None

        try:
            data = response.json()
            print(f"Data fetched: {data}")
            return data['data']['children']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            print("Response JSON:", response.json())
            return None

# Example usage
reddit_client = RedditClient()
data = reddit_client.get_music_subreddit_data('music')