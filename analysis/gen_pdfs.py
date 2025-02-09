import qrcode
from PIL import Image
import os

from api import API_KEY, BASE_URL, create_tracker

# Function to generate a QR code and save it as an image
def generate_qr_code(data, qr_filename):
    qr = qrcode.QRCode(
        version=1,  # version 1 is a 21x21 grid
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_filename)

# Function to paste the QR code onto the poster image
def paste_qr_on_poster(poster_path, qr_path, output_path, qr_position, qr_size):
    poster = Image.open(poster_path)
    qr = Image.open(qr_path)

    # Scale the QR code to the desired size
    qr = qr.resize((qr_size, qr_size))

    # Paste the QR code onto the poster at the specified position
    poster.paste(qr, qr_position)

    # Save the output poster with the QR code
    poster.save(output_path)
    print(f"Generated poster saved as: {output_path}")

# Function to generate multiple versions of the poster
def generate_multiple_posters(poster_path, redirect_url, campaign, num_versions, qr_position, qr_size, output_dir="output_posters"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate and save multiple versions of the poster
    for i in range(num_versions):
        id = create_tracker(API_KEY, redirect_url, campaign)
        qr_data = f"{BASE_URL}/{id}"  # Generate unique QR data for each version
        qr_filename = f"qr_code_{i + 1}.png"
        output_filename = os.path.join(output_dir, f"poster_{i + 1}.png")
        
        # Generate QR code
        generate_qr_code(qr_data, qr_filename)
        
        # Paste QR code on the poster and save the version
        paste_qr_on_poster(poster_path, qr_filename, output_filename, qr_position, qr_size)
        
        # Clean up the generated QR code image (optional)
        os.remove(qr_filename)

def main():
    poster_path = "poster_template.png"  # Replace with the path to your poster template
    redirect_url = input("URL To Track:")
    campaign = input("Name of campaign:")
    num_versions = int(input("How many posters to generate?"))  # Number of poster versions to generate
    
    # Define the QR code's position and size on the poster (in pixels)
    qr_position = (1240, 816)  # Example position (x, y) on the poster (top-left corner of the reserved spot)
    qr_size = 1200  # Size of the QR code in pixels
    
    generate_multiple_posters(poster_path, redirect_url, campaign, num_versions, qr_position, qr_size)

if __name__ == "__main__":
    main()
