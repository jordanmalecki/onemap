from src.filter_rides import filter_rides
from src.augment_rides import augment_rides
from src.fetch_trails_data import fetch_trails_data
from viz.plot_rides import plot_rides
from viz.plot_stats import plot_statistics
from viz.one_stat import combine_plots
from utils.geocode import geocode_location
from config import update_config_if_missing
import matplotlib.font_manager as fm
from matplotlib import rcParams

def set_default_font():
    arial_font = [
        font
        for font in fm.findSystemFonts(fontpaths=None, fontext="ttf")
        if "arial" in font.lower()
    ]
    if arial_font:
        rcParams["font.family"] = "Arial"
    else:
        rcParams["font.family"] = "DejaVu Sans"

def main():
    set_default_font()
    config = update_config_if_missing()
    
    try:
        fetch_trails_data("data/trails.json")
        lat, lon = geocode_location(config["ONEMAP_LOCATION"])
        
        if lat is None or lon is None:
            raise ValueError("Invalid location specified in configuration.")
        
        filter_rides(
            "data/trails.json",
            "data/filtered_rides.json",
            lat,
            lon,
            config["ONEMAP_MAX_DISTANCE"],
        )
        augment_rides(
            "data/filtered_rides.json",
            "data/user_rides.json",
            "data/coordinates.json",
            config["ONEMAP_NICKNAME"],
        )
        plot_rides("data/coordinates.json", "rides_map_dark.html")
        plot_statistics("data/user_rides.json", "out")
        combine_plots("out")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
