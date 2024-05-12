import folium
import json


def plot_rides(input_path, output_path):
    # Load the data from the JSON file
    with open(input_path, "r") as f:
        rides = json.load(f)

    # Initialize a map centered around the starting point of the first ride
    # Using a plain dark background without any tiles
    m = folium.Map(
        location=[float(rides[0][0]["lat"]), float(rides[0][0]["lon"])],
        zoom_start=13,
        tiles="CartoDB dark_matter",
    )

    # Plot each ride as a polyline
    for ride in rides:
        ride_coords = [(float(point["lat"]), float(point["lon"])) for point in ride]
        folium.PolyLine(ride_coords, color="#F50057", weight=6, opacity=0.02).add_to(m)

    # Save the map to an HTML file
    m.save(output_path)


if __name__ == "__main__":
    plot_rides("data/coordinates.json", "rides_map_dark.html")
