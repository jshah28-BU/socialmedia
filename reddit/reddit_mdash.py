import dash
from dash import html
from dash import dcc
import dash_html_components as html
import dash_core_components as dcc

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Function to convert a matplotlib figure to a dash compatible format
def fig_to_uri(in_fig, close_all=True, **save_args):
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        plt.close('all')
    out_img.seek(0)
    encoded = base64.b64encode(out_img.read()).decode("ascii")
    return "data:image/png;base64,{}".format(encoded)

# MongoDB setup and data aggregation
client = MongoClient('mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/')
db = client.reddit_db
collections = ["ElectronicMusic", "LetsTalkMusic", "Listentothis", "MusicNews", "WeAreTheMusicMakers", "music"]

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

# Create a Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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

# App layout
app.layout = dbc.Container([
    html.H1("Subreddit Engagement Dashboard", className="display-4"),
    
    dbc.Row([
        dbc.Col(html.Div(subreddit_graphs), width=12),
    ]),
    
    html.Hr(),
    
    dbc.Row([
        dbc.Col(html.Img(src=heatmap, style={'height':'70%', 'width':'70%'}), width=12),
    ]),
    
    html.Hr(),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_scatter), width=12),
    ]),
    
    html.Hr(),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_comparison), width=12),
    ]),
    
    html.Hr(),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=most_engaging_fig), width=12),
    ]),
    
    html.Hr(),
    
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='subreddit-dropdown',
                options=[{'label': subreddit, 'value': subreddit} for subreddit in df['subreddit'].unique()],
                multi=True,
                value=df['subreddit'].unique(),
                style={'color': '#2e2e2e'}
            ),
            width=12
        )
    ]),
], fluid=True)

# Callback to update the dropdown selection
@app.callback(
    dash.dependencies.Output('subreddit-dropdown', 'options'),
    [dash.dependencies.Input('subreddit-dropdown', 'value')]
)
def update_dropdown(selected_subreddits):
    options = [{'label': subreddit, 'value': subreddit} for subreddit in df['subreddit'].unique() if subreddit not in selected_subreddits]
    return options

# Callback to update the displayed graphs based on dropdown selection
@app.callback(
    dash.dependencies.Output('subreddit-dropdown', 'value'),
    [dash.dependencies.Input('subreddit-dropdown', 'options')]
)
def update_dropdown_value(options):
    return [option['value'] for option in options]

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True,port=8299)
