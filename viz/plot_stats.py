import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
import seaborn as sns
import json
from PIL import Image
import calmap
from datetime import datetime

# Set Seaborn darkgrid style
sns.set_style("darkgrid")

# Define a consistent color palette
colors = sns.color_palette("viridis", 10)  # Picking viridis palette with 10 shades

# Adjust matplotlib for dark theme
plt.rcParams["axes.facecolor"] = "#333333"
plt.rcParams["figure.facecolor"] = "#333333"
plt.rcParams["text.color"] = "white"
plt.rcParams["axes.labelcolor"] = "white"
plt.rcParams["xtick.color"] = "white"
plt.rcParams["ytick.color"] = "white"
plt.rcParams["font.family"] = "DejaVu Sans"  # Set default font to DejaVu Sans
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]  # Ensure DejaVu Sans is used

# Create output directory if it doesn't exist
output_dir = "out"
os.makedirs(output_dir, exist_ok=True)

# Load the data from JSON
with open("data/user_rides.json", "r") as file:
    data = json.load(file)
    rides = [ride for sublist in data for ride in sublist]
    df = pd.DataFrame(rides)

# Convert riding time to numeric type for arithmetic operations
df["ridingTime"] = pd.to_numeric(df["ridingTime"], errors="coerce")

# Now convert riding time from seconds to minutes
df["ridingTimeMinutes"] = df["ridingTime"] / 60  # Convert seconds to minutes

# Assuming the distances are in kilometers, convert to miles
km_to_miles_conversion = 0.621371
df["distance"] = df["distance"] * km_to_miles_conversion
df["averageSpeed"] = df["averageSpeed"] * km_to_miles_conversion

# Convert topSpeedOw values to mph using the conversion factor
conversion_factor = 30.91
df["topSpeedOw"] = df["topSpeedOw"] / conversion_factor

# Adjust altitude values based on the provided information
min_alt = df["altLow"].min()
df["altAdjusted"] = df["altLow"].apply(lambda x: (x - min_alt) + 460)
df["altUp"] = df["altUp"] + df["altAdjusted"]
df["altDown"] = df["altDown"] + df["altAdjusted"]

# Explicitly convert the 'timestamp' column to datetime format
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Check if there are any NaT (Not a Timestamp) entries after conversion
if df["timestamp"].isna().any():
    print("Warning: Some timestamp values couldn't be converted to datetime format.")


# Function to remove outliers using the IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]


# Remove outliers for relevant columns
df = remove_outliers(df, "distance")
df = remove_outliers(df, "averageSpeed")
df = remove_outliers(df, "topSpeedOw")
df = remove_outliers(df, "ridingTimeMinutes")

# Group by date and count the number of rides per day
rides_per_day = df.groupby(df["timestamp"].dt.date).size()

# Create a date range from the minimum to the maximum date in the dataset
all_dates = pd.date_range(
    start=df["timestamp"].min().date(), end=datetime.today().date()
)

# Reindex the rides_per_day series to include all dates and fill missing values with 0
rides_per_day_reindexed = rides_per_day.reindex(all_dates, fill_value=0)

# Convert the index to datetime format and ensure values are integers
rides_per_day_reindexed.index = pd.to_datetime(rides_per_day_reindexed.index)
rides_per_day_reindexed = rides_per_day_reindexed.astype(int)

# Extract day of week and hour for heatmaps
df["day_of_week"] = df["timestamp"].dt.day_name()
df["hour"] = df["timestamp"].dt.hour

# Heatmap of Rides by Day of Week and Hour
heatmap_data = df.groupby(["day_of_week", "hour"]).size().unstack().fillna(0)
ordered_days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
heatmap_data = heatmap_data.reindex(ordered_days)

# Cumulative Distance Over Time
df_sorted_by_date = df.sort_values(by="timestamp")
df_sorted_by_date["cumulative_distance"] = df_sorted_by_date["distance"].cumsum()

# Longest and Shortest Rides
longest_ride = df["distance"].max()
shortest_ride = df["distance"].min()

print(f"Longest Ride: {longest_ride:.2f} miles")
print(f"Shortest Ride: {shortest_ride:.2f} miles")

# Calculate cumulative distance by hour of the day
cumulative_distance_by_hour = df.groupby("hour")["distance"].sum()

# Time of Day Analysis
hourly_rides = df.groupby("hour").size()

# Heatmap of Cumulative Distance by Day of Week and Hour
cum_distance_heatmap_data = (
    df.groupby(["day_of_week", "hour"])["distance"]
    .sum()
    .round()
    .unstack()
    .fillna(0)
    .astype(int)
).reindex(ordered_days)

# Heatmap of Top Speed by Day of Week and Hour
top_speed_heatmap_data = (
    df.groupby(["day_of_week", "hour"])["topSpeedOw"]
    .max()
    .round()
    .unstack()
    .fillna(0)
    .astype(int)
).reindex(ordered_days)

# Heatmap of Average Speed by Day of Week and Hour
average_speed_heatmap_data = (
    df.groupby(["day_of_week", "hour"])["averageSpeed"]
    .mean()
    .round()
    .unstack()
    .fillna(0)
    .astype(int)
).reindex(ordered_days)

# Duration Between Rides
df_sorted_by_date["duration_between_rides"] = df_sorted_by_date[
    "timestamp"
].diff().dt.total_seconds() / (
    60 * 60 * 24
)  # Convert to days

# Correct the logic to compute riding streaks
df_sorted_by_date["day"] = df_sorted_by_date["timestamp"].dt.floor(
    "d"
)  # Get only the date part
unique_days = df_sorted_by_date["day"].drop_duplicates()  # Unique days with rides

# Check for consecutive days
streaks = (unique_days.diff() == pd.Timedelta(days=1)).astype(int)
streaks = streaks.groupby((streaks == 0).cumsum()).cumsum()

longest_streak = streaks.max()
print(f"Longest Streak of Consecutive Days Riding: {longest_streak} days")

longest_rest = df_sorted_by_date["duration_between_rides"].max()
print(f"Longest Rest Period: {longest_rest:.2f} days")

# Efficiency Analysis
df_sorted_by_date["efficiency"] = df_sorted_by_date["distance"] / (
    df_sorted_by_date["ridingTimeCalculated"] / 3600
)  # miles per hour

# Define DPI for high resolution
dpi_value = 150

# Save plots as separate PNG files

# Plot: Cumulative Distance Over Time
plt.figure(figsize=(12, 6))
plt.plot(
    df_sorted_by_date["timestamp"],
    df_sorted_by_date["cumulative_distance"],
    color=colors[2],
)
plt.title("Cumulative Distance Over Time")
plt.xlabel("Date")
plt.ylabel("Cumulative Distance (miles)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "cumulative_distance_over_time.png"), dpi=dpi_value
)
plt.close()

# Plot: Ride Distance vs. Average Speed
plt.figure(figsize=(12, 6))
plt.scatter(df["averageSpeed"], df["distance"], color=colors[5], alpha=0.7)
plt.title("Ride Distance vs. Average Speed")
plt.xlabel("Average Speed (mph)")
plt.ylabel("Ride Distance (miles)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "ride_distance_vs_average_speed.png"), dpi=dpi_value
)
plt.close()

# Bar Plot for Total Number of Rides per Day of the Week
rides_per_weekday = df["day_of_week"].value_counts().reindex(ordered_days)

plt.figure(figsize=(12, 6))
sns.barplot(x=rides_per_weekday.index, y=rides_per_weekday.values, color=colors[6])
plt.title("Number of Rides by Day of the Week")
plt.xlabel("Day of the Week")
plt.ylabel("Total Number of Rides")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "number_of_rides_by_day_of_week.png"), dpi=dpi_value
)
plt.close()

# Plot: Number of Rides by Hour of the Day
plt.figure(figsize=(12, 6))
plt.bar(hourly_rides.index, hourly_rides.values, color=colors[6])
plt.title("Number of Rides by Hour of the Day")
plt.xlabel("Hour of the Day")
plt.ylabel("Number of Rides")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "number_of_rides_by_hour_of_the_day.png"), dpi=dpi_value
)
plt.close()

# Plot: Distribution of Ride Distances
plt.figure(figsize=(12, 6))
sns.histplot(df["distance"], bins=30, kde=True, color=colors[4], edgecolor="white")
plt.title("Distribution of Ride Distances")
plt.xlabel("Distance (miles)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "distribution_of_ride_distances.png"), dpi=dpi_value
)
plt.close()

# Plot: Ride Distance Over Time
plt.figure(figsize=(12, 6))
plt.scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["distance"], color=colors[8]
)
plt.title("Ride Distance Over Time")
plt.xlabel("Date")
plt.ylabel("Distance (miles)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "ride_distance_over_time.png"), dpi=dpi_value)
plt.close()

# Plot: Heatmap of Cumulative Distance by Day of Week and Hour
plt.figure(figsize=(12, 6))
sns.heatmap(
    cum_distance_heatmap_data,
    cmap="viridis",
    linewidths=0.5,
    annot=True,
    fmt="d",
)
plt.title("Cumulative Distance by Day of Week and Hour")
plt.xlabel("Hour")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "cumulative_distance_by_day_of_week_and_hour.png"),
    dpi=dpi_value,
)
plt.close()

# Total distance by hour of the day
distance_by_hour = df.groupby("hour")["distance"].sum()

# Plot: Total Distance by Hour of the Day
plt.figure(figsize=(12, 6))
plt.bar(distance_by_hour.index, distance_by_hour.values, color=colors[5])
plt.title("Cumulative Distance by Hour of the Day")
plt.xlabel("Hour of the Day")
plt.ylabel("Total Distance (miles)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.xticks(range(0, 24))  # Show all hours on the x-axis
plt.savefig(os.path.join(output_dir, "cumulative_distance_by_hour.png"), dpi=dpi_value)
plt.close()

# Total distance by day of the week
distance_by_day = df.groupby("day_of_week")["distance"].sum().reindex(ordered_days)

# Plot: Total Distance by Day of the Week
plt.figure(figsize=(12, 6))
plt.bar(distance_by_day.index, distance_by_day.values, color=colors[6])
plt.title("Cumulative Distance by Day of the Week")
plt.xlabel("Day of the Week")
plt.ylabel("Total Distance (miles)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "cumulative_distance_by_day_of_week.png"), dpi=dpi_value
)
plt.close()


# Plot: Distribution of Top Speeds
plt.figure(figsize=(12, 6))
plt.hist(df["topSpeedOw"], bins=30, color=colors[1], edgecolor=colors[0], alpha=0.7)
plt.title("Distribution of Top Speeds")
plt.xlabel("Speed (mph)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "distribution_of_top_speeds.png"), dpi=dpi_value)
plt.close()

# Plot: Top Speed Over Time
plt.figure(figsize=(12, 6))
plt.scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["topSpeedOw"], color=colors[3]
)
plt.title("Top Speed Over Time")
plt.xlabel("Date")
plt.ylabel("Top Speed (mph)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "top_speed_over_time.png"), dpi=dpi_value)
plt.close()

# Plot: Heatmap of Top Speed by Day of Week and Hour
plt.figure(figsize=(12, 6))
sns.heatmap(
    top_speed_heatmap_data,
    cmap="viridis",
    linewidths=0.5,
    annot=True,
    fmt="d",
)
plt.title("Top Speed by Day of Week and Hour")
plt.xlabel("Hour")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "top_speed_by_day_of_week_and_hour.png"), dpi=dpi_value
)
plt.close()

# Plot: Distribution of Average Speeds
plt.figure(figsize=(12, 6))
sns.histplot(
    df["averageSpeed"],
    bins=30,
    kde=True,
    color=colors[2],
    edgecolor=colors[0],
)
plt.title("Distribution of Average Speeds")
plt.xlabel("Average Speed (mph)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "distribution_of_average_speeds.png"), dpi=dpi_value
)
plt.close()

# Plot: Average Speed Over Time
plt.figure(figsize=(12, 6))
plt.scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["averageSpeed"], color=colors[3]
)
plt.title("Average Speed Over Time")
plt.xlabel("Date")
plt.ylabel("Average Speed (mph)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "average_speed_over_time.png"), dpi=dpi_value)
plt.close()

# Plot: Heatmap of Average Speed by Day of Week and Hour
plt.figure(figsize=(12, 6))
sns.heatmap(
    average_speed_heatmap_data,
    cmap="viridis",
    linewidths=0.5,
    annot=True,
    fmt="d",
)
plt.title("Average Speed by Day of Week and Hour")
plt.xlabel("Hour")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "average_speed_by_day_of_week_and_hour.png"), dpi=dpi_value
)
plt.close()

# Plot: Distribution of Duration Between Rides
plt.figure(figsize=(12, 6))
sns.histplot(
    df_sorted_by_date["duration_between_rides"],
    bins=30,
    kde=True,
    color=colors[7],
    edgecolor="white",
)
plt.title("Duration Between Rides")
plt.xlabel("Duration (days)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "duration_between_rides.png"), dpi=dpi_value)
plt.close()

# Convert the rides_per_day_reindexed index to datetime if not already
rides_per_day_reindexed.index = pd.to_datetime(rides_per_day_reindexed.index)

# Ensure rides_per_day_reindexed values are integers
rides_per_day_reindexed = rides_per_day_reindexed.astype(int)

calmap.calendarplot(
    rides_per_day_reindexed,
    cmap="viridis",
    fillcolor="white",
    linewidth=0.5,
    yearlabels=True,
    daylabels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    dayticks=[0, 1, 2, 3, 4, 5, 6],
    monthticks=range(1, 13),
    monthly_border=True,
)

plt.title("Calendar Heatmap of Ride Frequency")
plt.savefig(os.path.join(output_dir, "calendar_heatmap_ride_frequency.png"), dpi=281)
plt.close()
# Box Plot for Ride Frequency by Hour
# Calculate the number of rides for each hour
rides_per_hour = df.groupby("hour").size()

# Speed Distribution Comparison by Ride Type
plt.figure(figsize=(12, 6))
sns.violinplot(
    data=df,
    x="ow_type",
    y="averageSpeed",
    hue="ow_type",
    palette="viridis",
    dodge=False,
    legend=False,
)
plt.title("Speed Distribution Comparison by Ride Type")
plt.xlabel("Ride Type")
plt.ylabel("Average Speed (mph)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "speed_distribution_comparison_by_ride_type.png"),
    dpi=dpi_value,
)
plt.close()

# Top Speed Distribution Comparison by Ride Type
plt.figure(figsize=(12, 6))
sns.violinplot(
    data=df,
    x="ow_type",
    y="topSpeedOw",
    hue="ow_type",
    palette="viridis",
    dodge=False,
    legend=False,
)
plt.title("Top Speed Distribution Comparison by Ride Type")
plt.xlabel("Ride Type")
plt.ylabel("Top Speed (mph)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "top_speed_distribution_comparison_by_ride_type.png"),
    dpi=dpi_value,
)
plt.close()

# Riding Time Variability by Hour of the Day with white whiskers
plt.figure(figsize=(12, 6))
ax = sns.boxplot(
    data=df,
    x="day_of_week",
    y="ridingTimeMinutes",
    color=colors[4],
    order=ordered_days,
    dodge=False,
)
# Customize the whiskers to be white
for whisker in ax.artists:
    whisker.set_edgecolor("white")  # This sets the color of the box edges to white

# We need to loop over the Line2D objects in the plot to set their color to white
for line in ax.lines:
    line.set_color("white")  # This sets the color of the whiskers and caps to white

plt.title("Riding Time Variability by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Riding Time (minutes)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "riding_time_variability_by_day_of_week.png"),
    dpi=dpi_value,
)
plt.close()

# Riding Time Variability by Hour of the Day with white whiskers
plt.figure(figsize=(12, 6))
ax = sns.boxplot(data=df, x="hour", y="ridingTimeMinutes", color=colors[4], dodge=False)

# Customize the whiskers to be white
for whisker in ax.artists:
    whisker.set_edgecolor("white")  # This sets the color of the box edges to white

# We need to loop over the Line2D objects in the plot to set their color to white
for line in ax.lines:
    line.set_color("white")  # This sets the color of the whiskers and caps to white

plt.title("Riding Time Variability by Hour of the Day")
plt.xlabel("Hour of the Day")
plt.ylabel("Riding Time (minutes)")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.xticks(range(0, 24))  # Show all hours on the x-axis
plt.savefig(
    os.path.join(output_dir, "riding_time_variability_by_hour.png"), dpi=dpi_value
)
plt.close()


# Histogram of Riding Time Distribution
plt.figure(figsize=(12, 6))
sns.histplot(df["ridingTimeMinutes"], bins=30, kde=True, color=colors[4])
plt.title("Histogram of Riding Time Distribution")
plt.xlabel("Riding Time (minutes)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, "histogram_of_riding_time_distribution.png"), dpi=dpi_value
)
plt.close()
