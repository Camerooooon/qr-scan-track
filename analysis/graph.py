import matplotlib.pyplot as plt
from collections import Counter

from api import fetch_data


# Function to extract relevant data from the response
def extract_data(data, category):
    category_data = []
    print(type(data))

    for tracker_id, tracker in data.get('trackers', {}).items():
        for log_entry in tracker.get('log', []):
            category_data.append(log_entry.get(category))

    return category_data

# Function to plot data using matplotlib
def plot_data(data, category):
    category_counts = Counter(data)

    # Create a bar chart
    plt.bar(category_counts.keys(), category_counts.values())
    plt.xlabel(category)
    plt.ylabel('Count')
    plt.title(f'{category} Distribution')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    api_url = '/track/get_all_tracks'
    
    # Fetch data from the API
    data = fetch_data(api_url)
    
    if not data:
        print("No data to process.")
        return

    print(data)
    
    # Select the category you want to visualize (options: 'user_agent', 'os', 'device', 'campaign')
    category = 'os'  # You can change this to 'user_agent', 'device', etc.
    
    # Extract data for the selected category
    category_data = extract_data(data, category)
    
    if not category_data:
        print(f"No data found for {category}.")
        return
    
    # Plot the extracted data
    plot_data(category_data, category)

if __name__ == "__main__":
    main()

