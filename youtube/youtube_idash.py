import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from pymongo import MongoClient
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# MongoDB Connection
mongo_uri = 'mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/'
client = MongoClient(mongo_uri)
db = client['YouTube_db']
collection = db['videoComments']

# Retrieve Comments
comments_data = []
for document in collection.find():
    comment = document.get('comment', '')
    if comment:  # Ensure there is a comment to analyze
        comments_data.append({
            'videoId': document.get('videoId', ''),
            'comment': comment
        })

# Convert to DataFrame
df = pd.DataFrame(comments_data)

# Sentiment Analysis Setup
sia = SentimentIntensityAnalyzer()
df['nltk_score'] = df['comment'].apply(lambda x: sia.polarity_scores(x)['compound'])

def textblob_sentiment(comment):
    blob = TextBlob(comment)
    return blob.sentiment.polarity

df['textblob_score'] = df['comment'].apply(textblob_sentiment)

# Initialize Dash App
app = dash.Dash(__name__)

# App Layout
app.layout = html.Div([
    html.H1("YouTube Comments Sentiment Analysis"),
    dcc.Dropdown(
        id='video-dropdown',
        options=[
            {'label': video_id, 'value': video_id} for video_id in df['videoId'].unique()
        ],
        value=df['videoId'][0] if not df.empty else None
    ),
    dcc.Graph(id='sentiment-graph')
])

# Callback for Updating Graph
@app.callback(
    Output('sentiment-graph', 'figure'),
    [Input('video-dropdown', 'value')]
)
def update_graph(selected_video_id):
    if selected_video_id:
        filtered_df = df[df['videoId'] == selected_video_id]
        return {
            'data': [
                go.Bar(name='NLTK', x=['NLTK'], y=[filtered_df['nltk_score'].mean()]),
                go.Bar(name='TextBlob', x=['TextBlob'], y=[filtered_df['textblob_score'].mean()])
            ],
            'layout': go.Layout(
                title=f'Sentiment Scores for Video {selected_video_id}',
                yaxis={'title': 'Average Sentiment Score'},
                barmode='group'
            )
        }
    return {}

# Run the Dash App
if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
