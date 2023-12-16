import pymongo
import pandas as pd
import matplotlib.pyplot as plt

# Connect to your MongoDB database
client = pymongo.MongoClient("mongodb://your_mongodb_uri")
db = client.your_database_name
collection = db.your_collection_name

# Define the date range
start_date = "2023-11-01"
end_date = "2023-11-14"

# Query MongoDB to retrieve relevant data within the date range
query = {
    "subreddit": "politics",
    "timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }
}
data = list(collection.find(query))

# Create a DataFrame from the retrieved data
df = pd.DataFrame(data)

# Convert the timestamp column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Group the data by hour and count the number of comments for each hour
hourly_comments = df.groupby(df['timestamp'].dt.to_period('H')).size().reset_index()
hourly_comments.columns = ['Hour', 'Number of Comments']

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(hourly_comments['Hour'], hourly_comments['Number of Comments'], marker='o', linestyle='-')
plt.title('Hourly Comments in r/politics (Nov 1 - Nov 14, 2023)')
plt.xlabel('Hour')
plt.ylabel('Number of Comments')
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()
