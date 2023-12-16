from pymongo import MongoClient
import requests

# Function to get toxicity score from HateModerateSpeech API
def get_toxicity_score(comment, api_url, api_key):
    payload = {'token': api_key, 'text': comment}
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API request failed: {response.status_code}, {response.text}")
        return None

# Function to retrieve and store comments
def analyze_and_store_comments(db_name, collection_name, api_url, api_key, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    comments_data = list(collection.find({}, {"_id": 0, "comment": 1}))

    for data in comments_data:
        comment = data.get('comment', '')
        if comment:
            analysis_result = get_toxicity_score(comment, api_url, api_key)
            if analysis_result and analysis_result.get('response') == 'Success':
                # Convert confidence to float
                confidence = float(analysis_result['confidence'])

                # Calculate toxicity score
                toxicity_score = confidence if analysis_result['class'] == 'toxic' else 1 - confidence
                collection.update_one({"comment": comment}, {"$set": {"toxicity": toxicity_score}})
                print(f"Comment: {comment}")
                print(f"Toxicity Score: {toxicity_score}")
                print("---------------------------------------------------")

# Example usage
db_name = "YouTube_db"
collection_name = "videoComments"
api_url = "https://api.moderatehatespeech.com/api/v1/moderate/"
api_key = "dc1ef15aeac103dc92bd00eceb7aa800"
mongo_uri = "mongodb+srv://socialmediadatahunters:DataHunterhai3jan@cluster0.xjnw24k.mongodb.net/"
analyze_and_store_comments(db_name, collection_name, api_url, api_key, mongo_uri)

