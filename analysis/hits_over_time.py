import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
import pytz
from api import fetch_data

# Define PST timezone
PST = pytz.timezone('US/Pacific')

# Function to process log entries and extract the number of hits over time for each tracker
def process_hits(data):
    hits_over_time = defaultdict(list)

    for tracker_id, tracker in data['trackers'].items():
        logs = tracker['log']
        if logs:
            # Extract timestamps and convert to PST
            for log in logs:
                timestamp = datetime.fromtimestamp(log['time']['secs_since_epoch'], tz=None)
                hits_over_time[tracker_id].append(timestamp)

    return hits_over_time

# Function to plot hits over time for each tracker (showing total hits over time)
def plot_hits_over_time(hits_over_time):
    plt.figure(figsize=(10, 6))

    # Define a color map
    cmap = plt.cm.get_cmap('tab10', len(hits_over_time))  # To differentiate each tracker with different colors

    # Create a line graph for each tracker showing total hits over time
    for i, (tracker_id, timestamps) in enumerate(hits_over_time.items()):
        # Count total hits at each time (cumulative sum)
        timestamps.sort()
        hit_counts = [i + 1 for i in range(len(timestamps))]  # Cumulative hits (total hits at each time)

        extended_timestamps = [timestamps[0]] + timestamps
        extended_hit_counts = [0] + hit_counts

        # Create a line graph for each tracker
        plt.step(extended_timestamps, extended_hit_counts, label=f'Tracker {tracker_id}', color=cmap(i), where='post')

    # Format the x-axis for better readability
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45)

    # Add labels and title
    plt.xlabel('Timestamp (PST)')
    plt.ylabel('Total Hits')
    plt.title('Total Hits Over Time for Each Tracker')
    plt.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()

def main():
    api_url = '/track/get_all_tracks'  # Replace with your API URL
    data = fetch_data(api_url)
    # Step 1: Process the hits over time
    hits_over_time = process_hits(data)

    # Step 2: Plot the total hits over time for each tracker
    plot_hits_over_time(hits_over_time)

if __name__ == "__main__":
    main()

