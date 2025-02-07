import json
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "123"


# Function to query the API and fetch data
def fetch_data(api_url):
    headers = {
        'X-API-Key': API_KEY
    }
    response = requests.get(BASE_URL + api_url, headers=headers)
    print(response.headers['content-type'])
    
    # Check if the response is successful
    if response.status_code == 200:
        try:
            # Attempt to parse the JSON response manually
            return json.loads(response.json())
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}
    else:
        print(f"Error fetching data: {response.status_code}")
        return {}
