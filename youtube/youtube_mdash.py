import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from wordcloud import WordCloud
import base64
from io import BytesIO

# Fetch data from MongoDB
def fetch_data():
    client = MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
    db = client['YouTube_db']  # Replace with your database name
    collection = db['trendingMusic']  # Replace with your collection name
    documents = collection.find({})
    df = pd.DataFrame(list(documents))
    df['viewCount'] = pd.to_numeric(df['viewCount'], errors='coerce')
    df['likeCount'] = pd.to_numeric(df['likeCount'], errors='coerce')
    df.dropna(subset=['viewCount', 'likeCount'], inplace=True)
    df['engagement_rate'] = (df['likeCount'] / df['viewCount']) * 100
    return df

df = fetch_data()

# Generate a word cloud image
def create_wordcloud(df):
    text = ' '.join(title for title in df['title'] if isinstance(title, str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, 'png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded = base64.b64encode(image_png)
    return "data:image/png;base64,{}".format(encoded.decode())


def fetch_response_data(db_name, collection_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    documents = collection.find({}, {"_id": 0, "comment": 1, "toxicity": 1})
    return pd.DataFrame(list(documents))

db_name = "YouTube_db"
collection_name = "videoComments"
mongo_uri = "mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/"
response_df = fetch_response_data(db_name, collection_name, mongo_uri)


# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("YouTube Trending Videos Dashboard", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='metric-select-dropdown',
        options=[
            {'label': 'Views', 'value': 'viewCount'},
            {'label': 'Likes', 'value': 'likeCount'},
            {'label': 'Engagement Rate', 'value': 'engagement_rate'}
        ],
        value='viewCount',
        style={'width': '50%', 'margin': '10px auto'}
    ),

    dcc.Graph(id='metric-graph'),

    html.Img(id='wordcloud', src=create_wordcloud(df), style={'height': '300px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),

    dcc.Graph(id='correlation-graph'),
    dcc.Graph(id='avg-engagement-rate-graph'),
    dcc.Graph(id='top-channels-by-video-count-graph'),  # Added comma here

    html.H1("YouTube Comments Toxicity Dashboard", style={'textAlign': 'center'}),

    dcc.Graph(id='toxicity-distribution-graph'),
    dcc.Graph(id='top-toxic-comments-graph'),
])


@app.callback(
    Output('metric-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_metric_graph(selected_metric):
    fig = px.bar(df.sort_values(by=selected_metric, ascending=False).head(10),
                 x='title', y=selected_metric, hover_data=['channel'], 
                 labels={'title': 'Title', selected_metric: selected_metric.capitalize()},
                 title=f"Top 10 Videos by {selected_metric.capitalize()}")
    return fig

@app.callback(
    Output('correlation-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_correlation_graph(selected_metric):
    correlation_matrix = df[['viewCount', 'likeCount']].corr()
    fig = px.imshow(correlation_matrix, text_auto=True, title="Correlation between Views and Likes")
    return fig

@app.callback(
    Output('avg-engagement-rate-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_avg_engagement_rate_graph(selected_metric):
    avg_engagement = df.groupby('channel')['engagement_rate'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(avg_engagement, title="Average Engagement Rate by Channel")
    return fig

@app.callback(
    Output('top-channels-by-video-count-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_top_channels_by_video_count_graph(selected_metric):
    top_channels = df['channel'].value_counts().head(10)
    fig = px.bar(top_channels, title="Top 10 Channels by Video Count in Trending")
    return fig

@app.callback(
    Output('toxicity-distribution-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_toxicity_distribution_graph(selected_metric):
    fig = px.histogram(response_df, x='toxicity', nbins=30, title="Distribution of Toxicity Scores")
    return fig

# Callback for top toxic comments graph
@app.callback(
    Output('top-toxic-comments-graph', 'figure'),
    [Input('metric-select-dropdown', 'value')]
)
def update_top_toxic_comments_graph(selected_metric):
    top_toxic_comments = response_df.sort_values(by='toxicity', ascending=False).head(10)
    fig = px.bar(top_toxic_comments, x='comment', y='toxicity', title="Top Toxic Comments")
    return fig



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=8301, host="0.0.0.0")
