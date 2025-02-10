import qrcode

from api import create_tracker, BASE_URL

# Function to generate a QR code for the URL
def generate_qr_code(track_url, file_name):
    img = qrcode.make(track_url)
    img.save(file_name)

def main():
    original_url = input("URL To Track:")
    campaign = input("Name of the power campaign:")

    # Step 1: Create the tracker and get the ID
    
    # Step 2: Generate n QR codes with the track URL (localhost:8000/<id>)
    n = 5  # Number of QR codes to generate (change as needed)
    for i in range(1, n + 1):
        tracker_id = create_tracker(original_url, campaign)
        print(tracker_id)
        print(f"Tracker created with ID: {tracker_id}")
        track_url = f'{BASE_URL}{tracker_id}'  # Track URL to generate QR code for
        file_name = f"qr_code_{i}.png"  # Name of the output file
        generate_qr_code(track_url, file_name)
        print(f"QR code {i} generated and saved as {file_name}")

if __name__ == "__main__":
    main()

