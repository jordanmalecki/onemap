import json
import os

CONFIG_PATH = "config.json"
example_config = {
    "HEADERS": {
        "authority": "app.onewheel.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://app.onewheel.com/rides.html",
        "sec-ch-ua": '"Google Chrome";v="95", " Not A Brand";v="99", "Chromium";v="95"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    },
    "COOKIES": {
        "_orig_referrer": "",
        "_landing_page": "%2F",
    },
    "ONEMAP_LOCATION": "Your_Location_Here",
    "ONEMAP_MAX_DISTANCE": 10.0,
    "ONEMAP_NICKNAME": "Your_Nickname_Here",
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    else:
        config = example_config
        save_config(config)
    return config

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def update_config_if_missing():
    config = load_config()
    updated = False
    
    if "Your_Location_Here" in config["ONEMAP_LOCATION"]:
        config["ONEMAP_LOCATION"] = input(
            "Please enter your location (e.g., 'Buffalo, NY'): "
        )
        updated = True
    
    if config["ONEMAP_MAX_DISTANCE"] == 10.0:
        config["ONEMAP_MAX_DISTANCE"] = float(
            input(
                "Please enter the maximum distance in miles you'd like to search for rides: "
            )
        )
        updated = True
    
    if "Your_Nickname_Here" in config["ONEMAP_NICKNAME"]:
        config["ONEMAP_NICKNAME"] = input(
            "Please enter your OneWheel app Nickname (display name on leaderboards): "
        )
        updated = True
    
    if updated:
        save_config(config)
    return config

if __name__ == "__main__":
    config = update_config_if_missing()
    print(
        "Configuration has been updated. Please ensure the values are correct."
    )
