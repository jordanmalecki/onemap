import folium
import json

def plot_rides(input_path, output_path):
    # Load the data from the JSON file
    with open(input_path, 'r') as f:
        rides = json.load(f)

    # Initialize a map centered around a starting point of a ride
    m = folium.Map(location=[float(rides[0][0]['lat']), float(rides[0][0]['lon'])], zoom_start=13, tiles=None)  # Set tiles=None to prevent loading default tiles

    # Applying the dark theme
    tile_url = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    tile_layer = folium.TileLayer(tiles=tile_url, attr='CartoDB dark_matter', name='CartoDB dark_matter')
    tile_layer.add_to(m)

    # For each ride in the data
    for ride in rides:
        ride_coords = [(float(point['lat']), float(point['lon'])) for point in ride]
    
        # Add a polyline for the ride
        folium.PolyLine(ride_coords, color='#B388FF', weight=3.5, opacity=0.16).add_to(m)

    # Save map to HTML
    m.save(output_path)

if __name__ == "__main__":
    plot_rides('data/coordinates.json', 'rides_map_dark.html')
