import requests
import qrcode
import json

from api import BASE_URL

# Function to call the API and create a new tracker
def create_tracker(api_key, url):
    headers = {'X-API-Key': api_key}
    response = requests.put(BASE_URL + "/track/new_track", data=url, headers=headers)
    
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

# Function to generate a QR code for the URL
def generate_qr_code(track_url, file_name):
    img = qrcode.make(track_url)
    img.save(file_name)

def main():
    api_key = '123'  # Replace with your actual API key
    original_url = input("URL To Track:")

    # Step 1: Create the tracker and get the ID
    

    # Step 2: Generate n QR codes with the track URL (localhost:8000/<id>)
    n = 5  # Number of QR codes to generate (change as needed)
    for i in range(1, n+1):
        tracker_id = create_tracker(api_key, original_url)
        print(f"Tracker created with ID: {tracker_id}")
        track_url = f'http://localhost:8000/{tracker_id}'  # Track URL to generate QR code for
        file_name = f"qr_code_{i}.png"  # Name of the output file
        generate_qr_code(track_url, file_name)
        print(f"QR code {i} generated and saved as {file_name}")

if __name__ == "__main__":
    main()

