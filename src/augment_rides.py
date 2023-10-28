import requests
import json
from config import HEADERS, COOKIES


def augment_rides(input_path, curl_1_output_path, curl_2_output_path, user_name):
    # Load the filtered data
    try:
        with open(input_path, 'r') as f:
            filtered_rides = json.load(f)
    except Exception as e:
        print(f"Error reading from {input_path}: {e}")
        return
    
    print(f"Loaded {len(filtered_rides)} rides from {input_path}")

    user_rides = []
    coordinates = []
    successful_responses = 0

    # Using a session for persistent connections
    with requests.Session() as session:
        session.headers.update(HEADERS)
        session.cookies.update(COOKIES)

        # Iterate over each ride and make the requests
        for idx, ride in enumerate(filtered_rides, 1):
            ride_id = ride['id']
            print(f"Processing ride {idx}/{len(filtered_rides)} with ID: {ride_id}")
            
            try:
                response_1 = session.get(f'https://app.onewheel.com/wp-json/fm/v2/trails/1?trackId={ride_id}')
                response_1.raise_for_status()  # Raise an HTTPError if an error occurred

                response_1_json = response_1.json()

                # If the name matches, append to user_rides
                if response_1_json[0]['name'] == user_name:
                    user_rides.append(response_1_json)
                    
                    response_2 = session.get(f'https://app.onewheel.com/wp-json/fm/v2/trailscoordinates/{ride_id}')
                    response_2.raise_for_status()

                    response_2_json = response_2.json()
                    coordinates.append(response_2_json)
                    successful_responses += 1
                    print(f"Successfully retrieved details for ride ID: {ride_id}")

            except requests.HTTPError as e:
                print(f"HTTP error occurred for ride ID {ride_id}: {e}")
            except requests.RequestException as e:
                print(f"Request error occurred for ride ID {ride_id}: {e}")

    print(f"Successfully retrieved details for {successful_responses} rides out of {len(filtered_rides)}")

    # Save the filtered curl_1 responses to a file
    try:
        with open(curl_1_output_path, 'w') as f:
            json.dump(user_rides, f)
            print(f"Saved the filtered curl_1 responses to {curl_1_output_path}")
    except Exception as e:
        print(f"Error writing to {curl_1_output_path}: {e}")

    # Save the filtered curl_2 responses to a file
    try:
        with open(curl_2_output_path, 'w') as f:
            json.dump(coordinates, f)
            print(f"Saved the filtered curl_2 responses to {curl_2_output_path}")
    except Exception as e:
        print(f"Error writing to {curl_2_output_path}: {e}")

if __name__ == "__main__":
    augment_rides('data/filtered_rides.json', 'data/user_rides.json', 'data/coordinates.json')
