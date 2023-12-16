from pymongo import MongoClient
import pandas as pd

def fetch_data():
    # Connect to MongoDB (update the connection string as per your setup)
    client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
    db = client['YouTube_db']  # Replace with your database name
    collection = db['trendingMusic']  # Replace with your collection name

    # Fetch all data from MongoDB
    documents = collection.find({})

    # Convert to Pandas DataFrame for easier analysis
    df = pd.DataFrame(list(documents))

    return df

def analyze_data(df):
    # Convert 'viewCount' and 'likeCount' to integers
    df['viewCount'] = pd.to_numeric(df['viewCount'], errors='coerce')
    df['likeCount'] = pd.to_numeric(df['likeCount'], errors='coerce')

    # Handling possible NaNs after conversion
    df.dropna(subset=['viewCount', 'likeCount'], inplace=True)

    # Basic Analysis
    print("Basic Statistics:")
    print(df.describe())

    # Engagement Metrics Calculation
    df['engagement_rate'] = (df['likeCount'] / df['viewCount']) * 100

    # Display top 10 videos by engagement rate
    top_videos = df.sort_values(by='engagement_rate', ascending=False).head(10)
    print("\nTop 10 Videos by Engagement Rate:")
    print(top_videos[['title', 'channel', 'viewCount', 'likeCount', 'engagement_rate']])

def main():
    df = fetch_data()
    analyze_data(df)

if __name__ == "__main__":
    main()