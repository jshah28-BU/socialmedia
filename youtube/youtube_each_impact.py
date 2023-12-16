

from pymongo import MongoClient
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Connect to MongoDB (Update connection string as needed)
client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db = client["YouTube_db"]  # Replace with your database name
collection = db["videoComments"]  # Replace with your collection name

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Function to analyze sentiment of a comment
def analyze_sentiment(comment):
    # Using NLTK
    nltk_score = sia.polarity_scores(comment)['compound']

    # Using TextBlob
    blob = TextBlob(comment)
    textblob_score = blob.sentiment.polarity

    return nltk_score, textblob_score

# Retrieve and analyze comments
for document in collection.find():
    comment = document['comment']
    nltk_score, textblob_score = analyze_sentiment(comment)
    print(f"Comment: {comment}\nNLTK Score: {nltk_score}, TextBlob Score: {textblob_score}\n")
