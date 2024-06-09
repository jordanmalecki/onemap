# run.py
from src.filter_rides import filter_rides
from src.augment_rides import augment_rides
from src.fetch_trails_data import fetch_trails_data
from viz.plot_rides import plot_rides
from viz.plot_stats import plot_statistics  # Import plot_statistics function
from viz.one_stat import combine_plots  # Import combine_plots function
from utils.geocode import geocode_location
from config import ONEMAP_LOCATION, ONEMAP_MAX_DISTANCE, ONEMAP_NICKNAME
import matplotlib.font_manager as fm
from matplotlib import rcParams

def set_default_font():
    # Check for Arial and set DejaVu Sans if not found
    arial_font = [font for font in fm.findSystemFonts(fontpaths=None, fontext='ttf') if 'arial' in font.lower()]
    if arial_font:
        rcParams['font.family'] = 'Arial'
    else:
        rcParams['font.family'] = 'DejaVu Sans'

def main():
    set_default_font()
    
    try:
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

        # Call the plot_statistics function from plot_stats.py
        plot_statistics("data/user_rides.json", "out")

        # Call the combine_plots function from one_stat.py
        combine_plots("out")  # Assuming combine_plots has this parameter
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
