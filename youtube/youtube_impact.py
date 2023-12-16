from pymongo import MongoClient
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from collections import defaultdict

# Connect to MongoDB (Update connection string as needed)
client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db = client["YouTube_db"]  # Replace with your database name
collection = db["videoComments"]  # Replace with your collection name

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Function to analyze sentiment of a comment
def analyze_sentiment(comment):
    nltk_score = sia.polarity_scores(comment)['compound']
    blob = TextBlob(comment)
    textblob_score = blob.sentiment.polarity
    return nltk_score, textblob_score

# Dictionaries to store cumulative sentiment scores and count of comments per video
video_sentiments_nltk = defaultdict(lambda: {'total_score': 0, 'count': 0})
video_sentiments_textblob = defaultdict(lambda: {'total_score': 0, 'count': 0})

# Retrieve and analyze comments
for document in collection.find():
    video_id = document['videoId']
    comment = document['comment']
    nltk_score, textblob_score = analyze_sentiment(comment)

    # Print each comment's score
    print(f"Comment: {comment}\nNLTK Score: {nltk_score}, TextBlob Score: {textblob_score}\n")

    # Aggregate scores for NLTK
    video_sentiments_nltk[video_id]['total_score'] += nltk_score
    video_sentiments_nltk[video_id]['count'] += 1

    # Aggregate scores for TextBlob
    video_sentiments_textblob[video_id]['total_score'] += textblob_score
    video_sentiments_textblob[video_id]['count'] += 1

# Function to determine sentiment category
def categorize_sentiment(score):
    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

# Calculate and display average sentiment per video
for video_id in video_sentiments_nltk:
    avg_nltk_score = video_sentiments_nltk[video_id]['total_score'] / video_sentiments_nltk[video_id]['count']
    avg_textblob_score = video_sentiments_textblob[video_id]['total_score'] / video_sentiments_textblob[video_id]['count']

    sentiment_nltk = categorize_sentiment(avg_nltk_score)
    sentiment_textblob = categorize_sentiment(avg_textblob_score)

    print(f"\nAggregate for Video ID: {video_id}")
    print(f"Average NLTK Sentiment Score: {avg_nltk_score} ({sentiment_nltk})")
    print(f"Average TextBlob Sentiment Score: {avg_textblob_score} ({sentiment_textblob})")

