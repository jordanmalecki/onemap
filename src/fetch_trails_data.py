import requests
import json
from config import HEADERS, COOKIES


def fetch_trails_data(output_path):
    ENDPOINT = "https://app.onewheel.com/wp-json/fm/v2/trails"

    response = requests.get(ENDPOINT, headers=HEADERS, cookies=COOKIES)

    # Check if the request was successful
    if response.status_code == 200:
        with open(output_path, "w") as f:
            json.dump(response.json(), f)
    else:
        print(
            f"Failed to fetch data from {ENDPOINT}. Status code: {response.status_code}"
        )
