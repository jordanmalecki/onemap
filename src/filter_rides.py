import json
from utils.haversine import haversine_distance


def filter_rides(input_path, output_path, lat, lon, distance_limit):
    # Load the data
    with open(input_path, 'r') as f:
        rides = json.load(f)

    # Filter the data
    filtered_rides = [ride for ride in rides if haversine_distance(lat, lon, float(ride['lat']), float(ride['lon'])) <= distance_limit]

    # Save the filtered data to a new file
    with open(output_path, 'w') as f:
        json.dump(filtered_rides, f)


if __name__ == "__main__":
    filter_rides('data/trails.json', 'data/filtered_rides.json')
