from src.filter_rides import filter_rides
from src.augment_rides import augment_rides
from src.fetch_trails_data import fetch_trails_data
from viz.plot_rides import plot_rides
from utils.geocode import geocode_location


def main():
    # Step 0: Fetch Data
    fetch_trails_data('data/trails.json')
    
    # Prompt the user for location and distance
    user_location = input("Please enter your location (e.g., 'Buffalo, NY'): ")
    max_distance = float(input("Please enter the maximum distance in miles you'd like to search for rides: "))
    user_name = input("Please enter your OneWheel app Nickname (display name on leaderboards): ")

    # Get latitude and longitude for the provided location
    lat, lon = geocode_location(user_location)

    # Update the filtering function to use the provided location and distance
    filter_rides('data/trails.json', 'data/filtered_rides.json', lat, lon, max_distance)

    # Update the augmentation function to use the provided USER_ID
    augment_rides('data/filtered_rides.json', 'data/user_rides.json', 'data/coordinates.json', user_name)

    # Step 3: Visualize Augmented Rides
    plot_rides('data/coordinates.json', 'rides_map_dark.html')

if __name__ == "__main__":
    main()
