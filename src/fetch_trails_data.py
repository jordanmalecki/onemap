import requests
import json
from config import load_config


def fetch_trails_data(output_path):
    config = load_config()
    HEADERS = config.get("HEADERS")
    COOKIES = config.get("COOKIES")

    ENDPOINT = "https://app.onewheel.com/wp-json/fm/v2/trails"
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()

        with open(output_path, "w") as f:
            json.dump(response.json(), f)
            print(f"Data successfully fetched and saved to {output_path}")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    fetch_trails_data("data/trails.json")
