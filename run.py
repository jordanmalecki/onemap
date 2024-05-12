from src.filter_rides import filter_rides
from src.augment_rides import augment_rides
from src.fetch_trails_data import fetch_trails_data
from viz.plot_rides import plot_rides
from utils.geocode import geocode_location


def main():
    fetch_trails_data("data/trails.json")
    user_location = input("Please enter your location (e.g., 'Buffalo, NY'): ")
    max_distance = float(
        input(
            "Please enter the maximum distance in miles you'd like to search for rides: "
        )
    )
    user_name = input(
        "Please enter your OneWheel app Nickname (display name on leaderboards): "
    )
    lat, lon = geocode_location(user_location)
    filter_rides("data/trails.json", "data/filtered_rides.json", lat, lon, max_distance)
    augment_rides(
        "data/filtered_rides.json",
        "data/user_rides.json",
        "data/coordinates.json",
        user_name,
    )
    plot_rides("data/coordinates.json", "rides_map_dark.html")


if __name__ == "__main__":
    main()
