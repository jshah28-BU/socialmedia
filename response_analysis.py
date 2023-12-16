import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import pymongo
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Dash app
app = dash.Dash(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/")
db = client["YouTube_db"]  # Replace with your database name
comments_collection = db["videoComments"]  # Replace with your actual collection name

# API Token and URL for ModerateHateSpeech
api_token = "912ec823b2c449eba5410a8d495ab570"
api_url = "https://api.moderatehatespeech.com/api/v1/moderate/"

# Function to analyze comment for hate speech
def analyze_comment_for_hate_speech(comment_text):
    try:
        # Sending request with authentication
        response = requests.post(api_url, json={"token": api_token, "text": comment_text})
        if response.status_code == 200:
            return response.json()  # Adjust based on actual API response format
        else:
            logging.error(f"API request failed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error during API request: {e}")
        return None

# Function to retrieve comments from MongoDB
def get_comments():
    comments = []
    for comment in comments_collection.find():
        comment_text = comment.get("comment")
        if comment_text:
            analysis_result = analyze_comment_for_hate_speech(comment_text)
            if analysis_result:
                comments.append({
                    "Comment": comment_text,
                    "Analysis Result": analysis_result
                })
    return comments

# Layout of the dashboard
app.layout = html.Div([
    html.H1("YouTube Comment Analysis Dashboard"),
    
    dcc.Graph(id="sentiment-pie-chart"),
    dcc.Graph(id="hate-speech-pie-chart"),
    
    html.Div(id="comment-output"),
    html.Button("Update Analysis", id="update-button")
])

# Callback to update sentiment pie chart
@app.callback(
    Output("sentiment-pie-chart", "figure"),
    Output("hate-speech-pie-chart", "figure"),
    Output("comment-output", "children"),
    Input("update-button", "n_clicks")
)
def update_analysis(n_clicks):
    comments = get_comments()
    print(f"Comments for analysis: {comments}")  # Print the comments for analysis

    if comments:
        comments_df = pd.DataFrame(comments)
        
        # Update the pie charts and display the results

    return fig_sentiment, fig_hate_speech, comments_df.to_json()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
