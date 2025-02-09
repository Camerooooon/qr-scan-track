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
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return {}

# Function to call the API and create a new tracker
def create_tracker(api_key, url, campaign):
    headers = {'X-API-Key': api_key}
    response = requests.put(BASE_URL + "/track/new_track?campaign=" + campaign, data=url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['tracker']['id']
        else:
            print("Error: Tracker creation failed.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None
