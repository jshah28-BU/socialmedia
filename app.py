import dash
from dash import dcc, html, dependencies
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import base64
from io import BytesIO
import plotly.graph_objs as go
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud


# Function to convert a matplotlib figure to a Dash compatible format
def fig_to_uri(in_fig, close_all=True, **save_args):
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        plt.close('all')
    out_img.seek(0)
    encoded = base64.b64encode(out_img.read()).decode("ascii")
    return "data:image/png;base64,{}".format(encoded)

# MongoDB Connection for Reddit
client_reddit = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db_reddit = client_reddit["reddit"]

# MongoDB Connection for YouTube
client_youtube = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db_youtube = client_youtube['YouTube_db']
collection_youtube = db_youtube['videoComments']

# Sentiment Analysis Functions for Reddit
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

def update_all_sentiments():
    for collection_name in db_reddit.list_collection_names():
        update_document_sentiment(db_reddit[collection_name])

# NLTK Sentiment Analysis for YouTube
sia = SentimentIntensityAnalyzer()

# Retrieve Comments from YouTube
comments_data_youtube = []
for document in collection_youtube.find():
    comment = document.get('comment', '')
    if comment:
        comments_data_youtube.append({
            'videoId': document.get('videoId', ''),
            'comment': comment,
            'nltk_score': sia.polarity_scores(comment)['compound'],
            'textblob_score': analyze_sentiment(comment)
        })

# Convert to DataFrame
df_youtube = pd.DataFrame(comments_data_youtube)

# MongoDB setup and data aggregation for Reddit
client = MongoClient('mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/')
db = client.reddit_db
collections = ["ElectronicMusic", "LetsTalkMusic", "Listentothis", "MusicNews", "WeAreTheMusicMakers", "music"]

#pipeline
def aggregate_data():
    all_data = []
    for collection_name in collections:
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
                "activeUsers": {"$size": "$uniqueAuthors"}
            }}
        ]
        data = list(collection.aggregate(pipeline))
        if data:
            all_data.extend(data)
    return pd.DataFrame(all_data)

df = aggregate_data()

# Exclude 'subreddit' from numeric calculations
numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
scaler = StandardScaler()
scaled_df = scaler.fit_transform(df[numeric_columns])

# KMeans Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
df['Cluster'] = kmeans.fit_predict(scaled_df)

# Calculate Comment to Upvote Ratio and Average Engagement Per Post
df['CommentToUpvoteRatio'] = df['totalComments'] / df['totalUpvotes']
df['AverageEngagementPerPost'] = df['totalComments'] / df['postCount']

# Correlation matrix plot for Reddit Data
corr_matrix = df[numeric_columns].corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f", cbar=False)
plt.title("Subreddit Correlation Matrix")
heatmap = fig_to_uri(plt.gcf())

# Individual Subreddit Plots
subreddit_graphs = []
for subreddit in df['subreddit'].unique():
    subreddit_df = df[df['subreddit'] == subreddit]
    fig = px.bar(subreddit_df, x='subreddit', y=['averageUpvotes', 'averageComments', 'activeUsers', 'postCount', 'CommentToUpvoteRatio', 'AverageEngagementPerPost'], barmode='group', title=f'Metrics for {subreddit}')
    subreddit_graphs.append(dcc.Graph(figure=fig, id=f"subreddit-{subreddit}"))

# Visualizations
fig_scatter = px.scatter(df, x='averageUpvotes', y='totalComments', color='Cluster', title='Cluster Analysis of Subreddits', hover_data=['subreddit'])

# Correlation matrix plot
corr_matrix = df[numeric_columns].corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f", cbar=False)
plt.title("Correlation Matrix")
heatmap = fig_to_uri(plt.gcf())

# Visualization comparing subreddits based on various metrics
fig_comparison = px.bar(df, x='subreddit', y=['totalUpvotes', 'totalComments', 'activeUsers', 'postCount', 'CommentToUpvoteRatio', 'AverageEngagementPerPost'], barmode='group', title='Subreddit Comparison - Metrics')

# Find the most engaging subreddit
most_engaging_subreddit = df.loc[df['totalUpvotes'].idxmax()]['subreddit']
most_engaging_fig = px.bar(df[df['subreddit'] == most_engaging_subreddit], 
                            x='subreddit', 
                            y=['averageUpvotes', 'averageComments', 'activeUsers', 'postCount', 'CommentToUpvoteRatio', 'AverageEngagementPerPost'], 
                            barmode='group', 
                            title=f'Most Engaging Subreddit - {most_engaging_subreddit}')

#subreddit wordcloud functions
def fetch_subreddit_titles():
    titles = []
    for collection_name in collections:
        collection = db[collection_name]
        documents = collection.find({}, {'title': 1})
        titles.extend([doc['title'] for doc in documents if 'title' in doc])
    return titles

def create_subreddit_wordcloud():
    titles = fetch_subreddit_titles()
    text = ' '.join(titles)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, 'png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded = base64.b64encode(image_png)
    return "data:image/png;base64,{}".format(encoded.decode("ascii"))


# Fetch data from MongoDB for YouTube
def fetch_data2():
    client2 = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
    db2 = client2['YouTube_db']
    collection2 = db2['trendingMusic']
    documents = collection2.find({})
    df2 = pd.DataFrame(list(documents))
    df2['viewCount'] = pd.to_numeric(df2['viewCount'], errors='coerce')
    df2['likeCount'] = pd.to_numeric(df2['likeCount'], errors='coerce')
    df2.dropna(subset=['viewCount', 'likeCount'], inplace=True)
    df2['engagement_rate'] = (df2['likeCount'] / df2['viewCount']) * 100
    return df2

df2 = fetch_data2()

def fetch_video_comments_data():
    # MongoDB Client Setup
    client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
    db = client['YouTube_db']

    # Fetch data from the 'videoComments' collection
    collection = db['videoComments']
    documents = collection.find({}, {"_id": 0, "comment": 1, "toxicity": 1, "videoId": 1})
    df_video_comments = pd.DataFrame(list(documents))

    return df_video_comments

# Call the function and store the DataFrame
df_video_comments = fetch_video_comments_data()

# Generate a word cloud image for YouTube Data
def create_wordcloud(df):
    text = ' '.join(title for title in df['title'] if isinstance(title, str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, 'png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded = base64.b64encode(image_png)
    return "data:image/png;base64,{}".format(encoded.decode("ascii"))



#app Layout

app = dash.Dash(__name__,external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

app.layout = html.Div([
    html.H1("Dashboard", className="display-4", style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Engagement Analysis', value='tab-1', children=[
            html.Div([
                html.H2("YouTube Engagement Analysis", style={'textAlign': 'center'}),
                # YouTube engagement components
                dcc.Dropdown(
                    id='youtube-metric-select-dropdown',
                    options=[
                        {'label': 'Views', 'value': 'viewCount'},
                        {'label': 'Likes', 'value': 'likeCount'},
                        {'label': 'Engagement Rate', 'value': 'engagement_rate'}
                    ],
                    value='viewCount',
                    style={'width': '50%', 'margin': '10px auto'}
                ),
                dcc.Graph(id='youtube-metric-graph'),
                # ... other YouTube engagement graphs and components
                dcc.Graph(id='correlation-graph'),
                dcc.Graph(id='avg-engagement-rate-graph'),
                dcc.Graph(id='top-channels-by-video-count-graph'),
                dcc.Graph(id='toxicity-distribution-graph'),
                dcc.Graph(id='top-toxic-comments-graph'),html.Hr(),html.Hr(),
                html.Img(id='wordcloud-img', src=create_wordcloud(df2), style={'height': '300px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),

                html.Hr(),
                html.H2("Reddit Engagement Analysis", style={'textAlign': 'center'}),
                # Reddit engagement components
                dcc.Graph(
                    figure=px.scatter(
                        df, x='averageUpvotes', y='totalComments', 
                        color='Cluster', title='Cluster Analysis of Subreddits', 
                        hover_data=['subreddit']
                    )
                ),
               
                html.Img(src=heatmap, style={'height': '70%', 'width': '70%'}),
                html.Div(subreddit_graphs),
                dcc.Graph(figure=fig_comparison),
                dcc.Graph(figure=most_engaging_fig),html.Hr(),
            
                html.Img(id='subreddit-wordcloud-img', src=create_subreddit_wordcloud(), style={'height': '300px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
                html.Hr(),html.Hr(),
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='Sentiment Analysis', value='tab-2', children=[
            html.Div([
                html.H2("YouTube Sentiment Analysis", style={'textAlign': 'center'}),
                # YouTube sentiment analysis components
                dcc.Dropdown(
                    id='video-dropdown',
                    options=[
                        {'label': video_id, 'value': video_id} for video_id in df_youtube['videoId'].unique()
                    ],
                    value=df_youtube['videoId'][0] if not df_youtube.empty else None
                ),
                dcc.Graph(id='sentiment-graph'),

                html.Hr(),
                html.H2("Reddit Sentiment Analysis", style={'textAlign': 'center'}),
                # Reddit sentiment analysis components
                dcc.Graph(id='sentiment-bar-chart'),
                dcc.Graph(id='sentiment-time-series'),
            ], style={'padding': '20px'})
        ]),
    ]),
    html.Div(id='tabs-content')
], style={'fontFamily': 'Arial, sans-serif'})


# Callbacks for  application


# Callbacks for  YouTube engagment data

@app.callback(
    dependencies.Output('youtube-metric-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_youtube_metric_graph(selected_metric):
    fig = px.bar(df2.sort_values(by=selected_metric, ascending=False).head(10),
                 x='title', y=selected_metric, hover_data=['channel'],
                 labels={'title': 'Title', selected_metric: selected_metric.capitalize()},
                 title=f"Top 10 Videos by {selected_metric.capitalize()}")
    return fig

@app.callback(
    dependencies.Output('correlation-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_correlation_graph(selected_metric):
    correlation_matrix = df2[['viewCount', 'likeCount']].corr()
    fig = px.imshow(correlation_matrix, text_auto=True, title="Correlation between Views and Likes")
    return fig

@app.callback(
    dependencies.Output('avg-engagement-rate-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_avg_engagement_rate_graph(selected_metric):
    avg_engagement = df2.groupby('channel')['engagement_rate'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(avg_engagement, title="Average Engagement Rate by Channel")
    return fig

@app.callback(
    dependencies.Output('top-channels-by-video-count-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_top_channels_by_video_count_graph(selected_metric):
    top_channels = df2['channel'].value_counts().head(10)
    fig = px.bar(top_channels, title="Top 10 Channels by Video Count in Trending")
    return fig

# Callback for top toxic comments graph
@app.callback(
    dependencies.Output('toxicity-distribution-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_toxicity_distribution_graph(selected_metric):
    fig = px.histogram(df_video_comments, x='toxicity', nbins=30, title="Distribution of Toxicity Scores")
    return fig

@app.callback(
    dependencies.Output('top-toxic-comments-graph', 'figure'),
    [dependencies.Input('youtube-metric-select-dropdown', 'value')]
)
def update_top_toxic_comments_graph(selected_metric):
    top_toxic_comments = df_video_comments.sort_values(by='toxicity', ascending=False).head(10)
    fig = px.bar(top_toxic_comments, x='comment', y='toxicity', title="Top Toxic Comments")
    return fig 

# Callbacks for Reddit sentiment
@app.callback(
    dependencies.Output('sentiment-bar-chart', 'figure'),
    [dependencies.Input('sentiment-bar-chart', 'id')]
)
def update_subreddit_sentiment_chart(_):
    subreddit_stats = {}
    collections = db_reddit.list_collection_names()

    for collection_name in collections:
        collection = db_reddit[collection_name]
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

@app.callback(
    dependencies.Output('sentiment-time-series', 'figure'),
    [dependencies.Input('sentiment-time-series', 'id')]
)
def update_time_series(_):
    all_comments = []
    collections = db_reddit.list_collection_names()

    for collection_name in collections:
        collection = db_reddit[collection_name]
        comments = collection.find({}, {"comment": 1, "timestamp": 1, "sentiment_score": 1, "_id": 0})
        for comment in comments:
            all_comments.append(comment)

    df = pd.DataFrame(all_comments)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df.sort_values('timestamp', inplace=True)

    fig = px.line(df, x='timestamp', y='sentiment_score', title='Sentiment Over Time', labels={'timestamp': 'Timestamp', 'sentiment_score': 'Sentiment Score'})
    fig.update_xaxes(rangeslider_visible=True)
    return fig

# Callbacks for YouTube sentiment
@app.callback(
    dependencies.Output('sentiment-graph', 'figure'),
    [dependencies.Input('video-dropdown', 'value')]
)
def update_graph(selected_video_id):
    if selected_video_id:
        filtered_df = df_youtube[df_youtube['videoId'] == selected_video_id]
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

if __name__ == '__main__':
    app.run_server(debug=True,port=8707)