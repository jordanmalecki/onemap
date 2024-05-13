# ./src/augment_rides.py
import requests
import json
from config import HEADERS, COOKIES


def augment_rides(input_path, curl_1_output_path, curl_2_output_path, user_name):
    try:
        with open(input_path, "r") as f:
            filtered_rides = json.load(f)
    except Exception as e:
        print(f"Error reading from {input_path}: {e}")
        return

    try:
        with open(curl_1_output_path, "r") as f:
            user_rides = json.load(f)
    except FileNotFoundError:
        user_rides = []
    except Exception as e:
        print(f"Error reading from {curl_1_output_path}: {e}")
        return

    max_ride_id = max((int(ride[0]["id"]) for ride in user_rides), default=0)
    new_rides = [ride for ride in filtered_rides if int(ride["id"]) > max_ride_id]
    coordinates = []
    successful_responses = 0

    with requests.Session() as session:
        session.headers.update(HEADERS)
        session.cookies.update(COOKIES)
        for idx, ride in enumerate(new_rides, 1):
            ride_id = ride["id"]
            print(f"Processing new ride {idx}/{len(new_rides)} with ID: {ride_id}")
            try:
                response_1 = session.get(
                    f"https://app.onewheel.com/wp-json/fm/v2/trails/1?trackId={ride_id}"
                )
                response_1.raise_for_status()
                response_1_json = response_1.json()
                if response_1_json[0]["name"] == user_name:
                    user_rides.append(response_1_json)
                    response_2 = session.get(
                        f"https://app.onewheel.com/wp-json/fm/v2/trailscoordinates/{ride_id}"
                    )
                    response_2.raise_for_status()
                    response_2_json = response_2.json()
                    coordinates.append(response_2_json)
                    successful_responses += 1
                    print(f"Successfully retrieved details for ride ID: {ride_id}")
            except requests.HTTPError as e:
                print(f"HTTP error occurred for ride ID {ride_id}: {e}")
            except requests.RequestException as e:
                print(f"Request error occurred for ride ID {ride_id}: {e}")

    print(
        f"Successfully retrieved details for {successful_responses} new rides out of {len(new_rides)}"
    )

    try:
        with open(curl_1_output_path, "w") as f:
            json.dump(user_rides, f)
            print(f"Saved the updated curl_1 responses to {curl_1_output_path}")
    except Exception as e:
        print(f"Error writing to {curl_1_output_path}: {e}")

    try:
        with open(curl_2_output_path, "r") as f:
            existing_coordinates = json.load(f)
    except FileNotFoundError:
        existing_coordinates = []
    except json.JSONDecodeError as e:
        print(f"Error reading from {curl_2_output_path}: {e}")
        existing_coordinates = []

    if coordinates:
        existing_coordinates.extend(coordinates)

    try:
        with open(curl_2_output_path, "w") as f:
            json.dump(existing_coordinates, f)
            print(f"Saved the updated coordinates to {curl_2_output_path}")
    except Exception as e:
        print(f"Error writing to {curl_2_output_path}: {e}")


if __name__ == "__main__":
    augment_rides(
        "data/filtered_rides.json", "data/user_rides.json", "data/coordinates.json"
    )
