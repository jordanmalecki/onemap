import matplotlib.pyplot as plt
import pandas as pd
import json
import seaborn as sns

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

# Load the data from JSON
with open("data/user_rides.json", "r") as file:
    data = json.load(file)
    rides = [ride for sublist in data for ride in sublist]
    df = pd.DataFrame(rides)

# Convert units to more familiar metrics
df["ridingTime"] = df["ridingTime"].apply(lambda x: f"{x // 3600}h {(x % 3600) // 60}m")

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

# Group by date and count the number of rides per day
rides_per_day = df.groupby(df["timestamp"].dt.date).size()

# Create a date range from the minimum to the maximum date in the dataset
all_dates = pd.date_range(
    start=df["timestamp"].min().date(), end=df["timestamp"].max().date()
)

# Reindex the rides_per_day series to include all dates and fill missing values with 0
rides_per_day_reindexed = rides_per_day.reindex(all_dates, fill_value=0)

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
df["efficiency"] = df["distance"] / (
    df["ridingTimeCalculated"] / 3600
)  # miles per hour


dpi_value = 100  # This can be adjusted based on the specific DPI of your target device or output
# Create a 4x3 grid of subplots
fig, axes = plt.subplots(
    5, 3, figsize=(3674 / dpi_value, 2036 / dpi_value), dpi=dpi_value
)

##############################################################################################################

# Plot 0,0: Cumulative Distance Over Time
axes[0, 0].plot(
    df_sorted_by_date["timestamp"],
    df_sorted_by_date["cumulative_distance"],
    color=colors[2],
)
axes[0, 0].set_title("Cumulative Distance Over Time")
axes[0, 0].set_xlabel("Date")
axes[0, 0].set_ylabel("Cumulative Distance (miles)")
axes[0, 0].grid(True, alpha=0.2)


# Plot 4,1: Ride Distance vs. Average Speed
axes[0, 1].scatter(df["averageSpeed"], df["distance"], color=colors[5], alpha=0.7)
axes[0, 1].set_title("Ride Distance vs. Average Speed")
axes[0, 1].set_xlabel("Average Speed (mph)")
axes[0, 1].set_ylabel("Ride Distance (miles)")
axes[0, 1].grid(True, alpha=0.2)

# Plot 4,2: Number of Rides by Hour of the Day
axes[0, 2].bar(hourly_rides.index, hourly_rides.values, color=colors[6])
axes[0, 2].set_title("Number of Rides by Hour of the Day")
axes[0, 2].set_xlabel("Hour of the Day")
axes[0, 2].set_ylabel("Number of Rides")
axes[0, 2].grid(True, alpha=0.2)

##############################################################################################################

# Plot 1,0: Distribution of Ride Distances
sns.histplot(
    df["distance"], bins=30, kde=True, color=colors[4], edgecolor="white", ax=axes[1, 0]
)
axes[1, 0].set_title("Distribution of Ride Distances")
axes[1, 0].set_xlabel("Distance (miles)")
axes[1, 0].set_ylabel("Frequency")
axes[1, 0].grid(True, alpha=0.2)

# Plot 1,1: Ride Distance Over Time
axes[1, 1].scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["distance"], color=colors[8]
)
axes[1, 1].set_title("Ride Distance Over Time")
axes[1, 1].set_xlabel("Date")
axes[1, 1].set_ylabel("Distance (miles)")
axes[1, 1].grid(True, alpha=0.2)

# Plot 1,2: Heatmap of Cumulative Distance by Day of Week and Hour
sns.heatmap(
    cum_distance_heatmap_data,
    cmap=colors,
    linewidths=0.5,
    annot=True,
    fmt="d",
    ax=axes[1, 2],
)
axes[1, 2].set_title("Cumulative Distance by Day of Week and Hour")

##############################################################################################################

# Plot 2,0: Distribution of Top Speeds
axes[2, 0].hist(
    df["topSpeedOw"], bins=30, color=colors[1], edgecolor=colors[0], alpha=0.7
)
axes[2, 0].set_title("Distribution of Top Speeds")
axes[2, 0].set_xlabel("Speed (mph)")
axes[2, 0].set_ylabel("Frequency")
axes[2, 0].grid(True, alpha=0.2)

# Plot 2,1: Top Speed Over Time with Gaps
axes[2, 1].scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["topSpeedOw"], color=colors[3]
)
axes[2, 1].set_title("Top Speed Over Time")
axes[2, 1].set_xlabel("Date")
axes[2, 1].set_ylabel("Top Speed (mph)")
axes[2, 1].grid(True, alpha=0.2)

# Plot 2,2: Heatmap of Top Speed by Day of Week and Hour
sns.heatmap(
    top_speed_heatmap_data,
    cmap=colors,
    linewidths=0.5,
    annot=True,
    fmt="d",
    ax=axes[2, 2],
)
axes[2, 2].set_title("Top Speed by Day of Week and Hour")

##############################################################################################################

# Plot 3,0: Distribution of Average Speeds
sns.histplot(
    df["averageSpeed"],
    bins=30,
    kde=True,
    color=colors[2],
    edgecolor=colors[0],
    ax=axes[3, 0],
)
axes[3, 0].set_title("Distribution of Average Speeds")
axes[3, 0].set_xlabel("Average Speed (mph)")
axes[3, 0].set_ylabel("Frequency")
axes[3, 0].grid(True, alpha=0.2)

# Plot 3,1: Average Speed Over Time with Gaps
axes[3, 1].scatter(
    df_sorted_by_date["timestamp"], df_sorted_by_date["averageSpeed"], color=colors[3]
)
axes[3, 1].set_title("Average Speed Over Time")
axes[3, 1].set_xlabel("Date")
axes[3, 1].set_ylabel("Average Speed (mph)")
axes[3, 1].grid(True, alpha=0.2)

# Plot 3,2: Heatmap of Average Speed by Day of Week and Hour
sns.heatmap(
    average_speed_heatmap_data,
    cmap=colors,
    linewidths=0.5,
    annot=True,
    fmt="d",
    ax=axes[3, 2],
)
axes[3, 2].set_title("Average Speed by Day of Week and Hour")

##############################################################################################################

# Plot 4,0: Distribution of Duration Between Rides
sns.histplot(
    df_sorted_by_date["duration_between_rides"],
    bins=30,
    kde=True,
    color=colors[7],
    edgecolor="white",
    ax=axes[4, 0],
)
axes[4, 0].set_title("Duration Between Rides")
axes[4, 0].set_xlabel("Duration (days)")
axes[4, 0].set_ylabel("Frequency")
axes[4, 0].grid(True, alpha=0.2)

# Plot 4,1: Daily Frequency
axes[4, 1].scatter(rides_per_day_reindexed.index, rides_per_day_reindexed.values)
axes[4, 1].set_title("Number of Rides per Day")
axes[4, 1].set_xlabel("Date")
axes[4, 1].set_ylabel("Number of Rides")
axes[4, 1].grid(True)

# Plot 4,2: Heatmap of Rides by Day of Week and Hour
sns.heatmap(
    heatmap_data, cmap=colors, linewidths=0.5, annot=True, fmt=".0f", ax=axes[4, 2]
)
axes[4, 2].set_title("Ride Frequency by Day of Week and Hour")

# Grid, Title, XLabel, YLabel Adjustments
for i in range(4):
    for j in range(3):
        ax = axes[i, j]
        ax.grid(True, alpha=0.2)
        ax.set_title(
            ax.get_title().replace("_", " ").title(), color="white"
        )  # replacing underscores and title casing
        ax.set_xlabel(
            ax.get_xlabel().replace("_", " ").title(), color="white"
        )  # replacing underscores and title casing
        ax.set_ylabel(
            ax.get_ylabel().replace("_", " ").title(), color="white"
        )  # replacing underscores and title casing
        ax.tick_params(colors="white")

# Adjust the layout
plt.tight_layout()
plt.savefig("dashboard.png", dpi=dpi_value)
plt.show()
