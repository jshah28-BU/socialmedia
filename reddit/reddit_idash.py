from pymongo import MongoClient
from textblob import TextBlob
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# MongoDB Connection
client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")  # Replace with your actual connection string
db = client["reddit"]

# Sentiment Analysis Functions
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

# Function to add sentiment score and category to each document in MongoDB
def update_document_sentiment(collection):
    comments = collection.find({})
    for comment in comments:
        sentiment_score = analyze_sentiment(comment['comment'])
        sentiment_category = categorize_sentiment(sentiment_score)
        collection.update_one(
            {'_id': comment['_id']},
            {'$set': {
                'sentiment_score': sentiment_score,
                'sentiment_category': sentiment_category
            }}
        )

# This function will be called once when the Dash app starts to update sentiments
def update_all_sentiments():
    for collection_name in db.list_collection_names():
        update_document_sentiment(db[collection_name])

# Call the update function to add sentiments to all documents in all collections
update_all_sentiments()

# Dash App Initialization
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Reddit Sentiment Dashboard"),
    dcc.Graph(id='sentiment-bar-chart'),
    html.H2("Sentiment Time Series Analysis"),
    dcc.Graph(id='sentiment-time-series')
])

# Callback for the subreddit sentiment bar chart
@app.callback(
    Output('sentiment-bar-chart', 'figure'),
    [Input('sentiment-bar-chart', 'id')]  # This input is just a dummy to trigger the callback
)
def update_subreddit_sentiment_chart(_):
    subreddit_stats = {}
    collections = db.list_collection_names()

    for collection_name in collections:
        collection = db[collection_name]
        stats = collection.aggregate([
            {
                "$group": {
                    "_id": "$sentiment_category",
                    "count": {"$sum": 1}
                }
            }
        ])
        subreddit_stats[collection_name] = {item['_id']: item['count'] for item in stats}

    data = [
        go.Bar(name='Positive', x=list(subreddit_stats.keys()), y=[stats.get("Positive", 0) for stats in subreddit_stats.values()]),
        go.Bar(name='Negative', x=list(subreddit_stats.keys()), y=[stats.get("Negative", 0) for stats in subreddit_stats.values()]),
        go.Bar(name='Neutral', x=list(subreddit_stats.keys()), y=[stats.get("Neutral", 0) for stats in subreddit_stats.values()]),
    ]

    figure = go.Figure(data=data)
    figure.update_layout(
        title='Sentiment Analysis Across Subreddits',
        xaxis=dict(title='Subreddit'),
        yaxis=dict(title='Number of Comments'),
        barmode='group'
    )
    return figure

# Callback for the sentiment time series
@app.callback(
    Output('sentiment-time-series', 'figure'),
    [Input('sentiment-time-series', 'id')]  # This input is just a dummy to trigger the callback
)
def update_time_series(_):
    all_comments = []
    collections = db.list_collection_names()

    for collection_name in collections:
        collection = db[collection_name]
        comments = collection.find({}, {"comment": 1, "timestamp": 1, "sentiment_score": 1, "_id": 0})
        for comment in comments:
            all_comments.append(comment)

    df = pd.DataFrame(all_comments)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df.sort_values('timestamp', inplace=True)

    fig = px.line(df, x='timestamp', y='sentiment_score', title='Sentiment Over Time', labels={'timestamp': 'Timestamp', 'sentiment_score': 'Sentiment Score'})
    fig.update_xaxes(rangeslider_visible=True)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8259, host="0.0.0.0")
