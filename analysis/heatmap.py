import requests
import json
import hashlib
import folium
from folium.plugins import HeatMap
from collections import defaultdict
from api import fetch_data

# Predefined set of colors in Folium
FOLIUM_COLORS = ['lightblue', 'red', 'darkred', 'blue', 'pink', 'beige', 'darkpurple', 'black', 'cadetblue', 'darkblue', 'orange', 'gray', 'darkgreen', 'lightgreen', 'purple', 'green', 'lightred', 'lightgray', 'white']

# Function to extract latitudes, longitudes, and hits
def extract_locations_and_hits(data):
    locations = []
    hits = defaultdict(int)  # A dictionary to store the count of hits per (lat, lon)
    campaign = defaultdict(str)

    for tracker_id, tracker in data.get('trackers', {}).items():
        logs = tracker.get('log', [])
        loc = tracker.get('loc', {})
        if loc is None:
            continue

        lat = loc.get('lat')
        lon = loc.get('lon')
        campaign[(lat, lon)] = tracker.get('campaign')
        for log in logs:
            if loc:
                if lat is not None and lon is not None:
                    # Count the number of hits for this location
                    hits[(lat, lon)] += 1
                    locations.append((lat, lon, tracker_id))  # Store tracker_id along with lat and lon

    return locations, hits, campaign

# Function to generate a random color for each marker
def get_color_for_tracker(string):
    return FOLIUM_COLORS[int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16) % len(FOLIUM_COLORS)]  # Loop through colors if there are more trackers than colors

# Function to create the heatmap with OpenStreetMap as the background
def create_heatmap(locations, hits, campaign):
    # Initialize the map centered around a specific location
    map_center = [locations[0][0] / 1_000_000, locations[0][1] / 1_000_000] if locations else [0, 0]
    m = folium.Map(location=map_center, zoom_start=12, tiles="OpenStreetMap")

    # Create a list of locations with their respective hit counts
    heatmap_data = [[lat / 1_000_000, lon / 1_000_000, hits[(lat, lon)]] for lat, lon, _ in locations]
    
    # Add HeatMap layer to the map
    HeatMap(heatmap_data).add_to(m)

    # Add markers for each tracker with unique colors and tracker IDs in the callouts
    for i, (lat, lon, tracker_id) in enumerate(locations):
        color = get_color_for_tracker(campaign[(lat, lon)])  # Assign a unique color based on name of campaign
        
        # Add a marker with the tracker ID and hit count in the popup
        folium.Marker(
            location=[lat / 1_000_000, lon / 1_000_000], 
            popup=f'{tracker_id}<br>Hits: {hits[(lat, lon)]}<br>Campaign: {campaign[(lat, lon)]}',
            icon=folium.Icon(color=color)  # Set a unique color for each tracker
        ).add_to(m)

    # Save the map to an HTML file
    m.save("heatmap_with_osm_and_markers.html")
    print("Heatmap with markers saved as 'heatmap_with_osm_and_markers.html'")

def main():
    api_url = '/track/get_all_tracks'  # Replace with your API URL
    
    # Fetch data from the API
    data = fetch_data(api_url)
    
    if not data:
        print("No data to process.")
        return
    
    # Extract locations and hits
    locations, hits, campaign = extract_locations_and_hits(data)
    print(data)
    
    if not locations:
        print("No locations found.")
        return
    
    # Create and display the heatmap
    create_heatmap(locations, hits, campaign)

if __name__ == "__main__":
    main()

