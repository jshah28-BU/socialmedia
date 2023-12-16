from pymongo import MongoClient
import requests

# Function to get toxicity score from HateModerateSpeech API
def get_toxicity_score(comment, api_url, api_key):
    payload = {'comment': comment}
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.post(api_url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    
    if response.status_code == 200:
        return response.json().get('toxicity_score', 0)
    else:
        # Handle error or invalid response
        return 0

# Function to retrieve comments from MongoDB
def fetch_comments_from_mongo(db_name, collection_name, mongo_uri="mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/"):
    client = MongoClient(mongo_uri)
    db = client["YouTube_db"]
    collection = db["videoComments"]
    return list(collection.find({}, {"_id": 0, "comment": 1}))

# Main function to analyze comments
def analyze_comments(db_name, collection_name, api_url, api_key):
    comments_data = fetch_comments_from_mongo(db_name, collection_name)
    
    report = {'comments_analysis': []}

    for data in comments_data:
        comment = data.get('comment', '')
        toxicity_score = get_toxicity_score(comment, api_url, api_key)
        
        report['comments_analysis'].append({
            'comment': comment,
            'toxicity_score': toxicity_score
        })

    return report

# Example usage
db_name = "YouTube_db"
collection_name = "videoComments"
api_url = "https://api.moderatehatespeech.com/api/v1/moderate/"  # Replace with actual API endpoint
api_key = "c24affc5e2a54a1117d22019051e9d32"  # Replace with your API key
report = analyze_comments(db_name, collection_name, api_url, api_key)
print(report)
