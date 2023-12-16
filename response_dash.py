from pymongo import MongoClient
import requests
import pandas as pd
import dash
from dash import html, dcc
import plotly.express as px

# Function to get toxicity score
def get_toxicity_score(comment, api_url, api_key):
    payload = {'token': api_key, 'text': comment}
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('score', 0)  # Assuming 'score' is in the response
    else:
        print(f"API request failed: {response.status_code}, {response.text}")
        return 0

# Function to retrieve comments from MongoDB
def fetch_comments_from_mongo(db_name, collection_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    return list(collection.find({}, {"_id": 0, "comment": 1}))

# Function to analyze comments
def analyze_comments(db_name, collection_name, api_url, api_key, mongo_uri):
    comments_data = fetch_comments_from_mongo(db_name, collection_name, mongo_uri)
    analysis_results = []

    for data in comments_data:
        comment = data.get('comment', '')
        if comment:
            score = get_toxicity_score(comment, api_url, api_key)
            analysis_results.append({'comment': comment, 'score': score})

    return analysis_results

# Dash app setup
app = dash.Dash(__name__)

# Fetch and analyze data
db_name = "YouTube_db"
collection_name = "videoComments"
api_url = "https://api.moderatehatespeech.com/api/v1/moderate/"
api_key = "dc1ef15aeac103dc92bd00eceb7aa800"
mongo_uri = "mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/"  # Replace with your MongoDB URI

results = analyze_comments(db_name, collection_name, api_url, api_key, mongo_uri)
df = pd.DataFrame(results)

# App layout
app.layout = html.Div([
    html.H1("Comments Toxicity Analysis"),
    dcc.Graph(
        id='toxicity-graph',
        figure=px.histogram(df, x='score', nbins=20, title="Distribution of Toxicity Scores")
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=8101)
