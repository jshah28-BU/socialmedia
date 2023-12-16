import pymongo
import pandas as pd
import matplotlib.pyplot as plt

# Connect to your MongoDB database
client = pymongo.MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db = client.politics
collection = db.data

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

# Group the data by date and count the number of submissions for each day
daily_submissions = df.groupby(df['timestamp'].dt.date).size().reset_index()
daily_submissions.columns = ['Date', 'Number of Submissions']

# Create the scatter plot
# ... (previous code)

# Create the scatter plot
plt.figure(figsize=(12, 6))
plt.scatter(daily_submissions['Date'], daily_submissions['Number of Submissions'], color='blue')
plt.title('Daily Submissions in r/politics (Nov 1 - Nov 14, 2023)')
plt.xlabel('Date')
plt.ylabel('Number of Submissions')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the scatter plot as an image file (e.g., PNG)
plt.savefig("daily_submissions_scatter_plot.png")

# Close the plot
plt.close()
