import os
from PIL import Image

def combine_plots(output_dir):# Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the order of the plots
    plot_files = [
        "calendar_heatmap_total_distance.png",
        "number_of_rides_by_day_of_week.png",
        "number_of_rides_by_hour_of_the_day.png",
        "histogram_of_riding_time_distribution.png",
        "cumulative_distance_over_time.png",
        "ride_distance_vs_average_speed.png",
        "distribution_of_ride_distances.png",
        "cumulative_distance_by_day_of_week_and_hour.png",
        "cumulative_distance_by_hour.png",
        "cumulative_distance_by_day_of_week.png",
        "ride_distance_over_time.png",
        "distribution_of_average_speeds.png",
        "average_speed_over_time.png",
        "average_speed_by_day_of_week_and_hour.png",
        "distribution_of_top_speeds.png",
        "top_speed_over_time.png",
        "top_speed_by_day_of_week_and_hour.png",
        "speed_distribution_comparison_by_ride_type.png",
        "top_speed_distribution_comparison_by_ride_type.png",
        "riding_time_variability_by_day_of_week.png",
        "riding_time_variability_by_hour.png",
        "duration_between_rides.png"
    ]

    # Load images and get total height
    images = [Image.open(os.path.join(output_dir, file)) for file in plot_files]
    widths, heights = zip(*(img.size for img in images))
    total_height = sum(heights)
    max_width = max(widths)

    # Create a new image with the total height and max width
    combined_image = Image.new('RGB', (max_width, total_height))

    # Paste images one below the other
    y_offset = 0
    for img in images:
        combined_image.paste(img, (0, y_offset))
        y_offset += img.height

    # Save the combined image
    combined_image.save(os.path.join(output_dir, "combined_plots.png"))
