from src.filter_rides import filter_rides
from src.augment_rides import augment_rides
from src.fetch_trails_data import fetch_trails_data
from viz.plot_rides import plot_rides
from utils.geocode import geocode_location
from config import ONEMAP_LOCATION, ONEMAP_MAX_DISTANCE, ONEMAP_NICKNAME


def main():
    fetch_trails_data("data/trails.json")
    lat, lon = geocode_location(ONEMAP_LOCATION)
    filter_rides(
        "data/trails.json", "data/filtered_rides.json", lat, lon, ONEMAP_MAX_DISTANCE
    )
    augment_rides(
        "data/filtered_rides.json",
        "data/user_rides.json",
        "data/coordinates.json",
        ONEMAP_NICKNAME,
    )
    plot_rides("data/coordinates.json", "rides_map_dark.html")


if __name__ == "__main__":
    main()
