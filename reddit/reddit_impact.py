from pymongo import MongoClient
from textblob import TextBlob

# MongoDB Connection
client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db = client["reddit"]

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def categorize_sentiment(score):
    if score > 0.1:
        return "Positive"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"

def get_subreddit_sentiment_stats(collection_name):
    collection = db[collection_name]
    total_sentiment = 0
    total_comments = 0
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    try:
        comments = collection.find({}, {"comment": 1, "_id": 0})

        for comment in comments:
            text = comment.get("comment", "")
            if text:
                sentiment_score = analyze_sentiment(text)
                sentiment_category = categorize_sentiment(sentiment_score)

                if sentiment_category == "Positive":
                    positive_count += 1
                elif sentiment_category == "Negative":
                    negative_count += 1
                else:
                    neutral_count += 1

                total_sentiment += sentiment_score
                total_comments += 1

        avg_sentiment = total_sentiment / total_comments if total_comments > 0 else None

        return avg_sentiment, total_comments, positive_count, negative_count, neutral_count

    except Exception as e:
        print(f"An error occurred in {collection_name}: {e}")
        return None, 0, 0, 0, 0

def main():
    subreddit_stats = {}
    collections = db.list_collection_names()

    for collection_name in collections:
        avg_sentiment, total_count, pos_count, neg_count, neu_count = get_subreddit_sentiment_stats(collection_name)
        subreddit_stats[collection_name] = {
            "average_sentiment": avg_sentiment,
            "total_comments": total_count,
            "positive_comments": pos_count,
            "negative_comments": neg_count,
            "neutral_comments": neu_count
        }

    # Print and compare subreddit statistics
    for subreddit, stats in subreddit_stats.items():
        print(f"Subreddit '{subreddit}':")
        print(f"  Average Sentiment: {stats['average_sentiment']}")
        print(f"  Total Comments: {stats['total_comments']}")
        print(f"  Positive Comments: {stats['positive_comments']}")
        print(f"  Negative Comments: {stats['negative_comments']}")
        print(f"  Neutral Comments: {stats['neutral_comments']}")
        print()

if __name__ == "__main__":
    main()
