from pymongo import MongoClient
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# MongoDB setup
client = MongoClient('mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/')
db = client.reddit_db

# List of collections (each representing a subreddit)
collections = ["ElectronicMusic", "LetsTalkMusic", "Listentothis", "MusicNews", "WeAreTheMusicMakers", "music"]

# Function to aggregate data for a collection
def aggregate_data(collection_name):
    collection = db[collection_name]
    pipeline = [
        {"$group": {
            "_id": None,
            "averageUpvotes": {"$avg": "$upvotes"},
            "totalUpvotes": {"$sum": "$upvotes"},
            "averageComments": {"$avg": "$comments"},
            "totalComments": {"$sum": "$comments"},
            "postCount": {"$sum": 1},
            "uniqueAuthors": {"$addToSet": "$author"}
        }},
        {"$project": {
            "_id": 0,
            "subreddit": collection_name,
            "averageUpvotes": 1,
            "totalUpvotes": 1,
            "averageComments": 1,
            "totalComments": 1,
            "postCount": 1,
            "activeUsers": {"$size": "$uniqueAuthors"},
            "averageEngagement": {
                "$avg": {"$sum": ["$upvotes", "$comments"]}
            },
            "totalEngagement": {
                "$sum": {"$sum": ["$upvotes", "$comments"]}
            }
        }}
    ]
    return list(collection.aggregate(pipeline))

# Aggregating data for each collection
all_data = []
for collection_name in collections:
    data = aggregate_data(collection_name)
    if data:
        all_data.extend(data)

# Creating a DataFrame from the aggregated data
df = pd.DataFrame(all_data)

# Drop 'subreddit' column before clustering
df_no_subreddit = df.drop(['subreddit'], axis=1)

# Standardizing the data for cluster analysis
scaler = StandardScaler()
scaled_df = scaler.fit_transform(df_no_subreddit)

# KMeans Clustering
kmeans = KMeans(n_clusters=2, random_state=42)  # You can change the number of clusters
df['Cluster'] = kmeans.fit_predict(scaled_df)

# Print cluster centers and labels for further analysis
print("Cluster Centers:")
print(kmeans.cluster_centers_)

print("\nSubreddits and their Cluster Labels:")
print(df[['subreddit', 'Cluster']])

# Print total and average engagement for each subreddit
print("\nTotal and Average Engagement:")
print(df[['subreddit', 'totalEngagement', 'averageEngagement']])
