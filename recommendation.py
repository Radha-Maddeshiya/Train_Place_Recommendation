import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

place_file = "place_details.csv"
train_file = "Train_details.csv"

places_df = pd.read_csv(place_file)
trains_df = pd.read_csv(train_file)

city = input("Enter your city (e.g., Gorakhpur): ").strip()
arrival_time = input("Enter your arrival time (e.g., 04:30 PM): ").strip()

user_lat = 26.7634
user_lon = 83.3783

places_df["Open Time"] = pd.to_datetime(places_df["Open Time"], format="%I:%M %p").dt.time
places_df["Close Time"] = pd.to_datetime(places_df["Close Time"], format="%I:%M %p").dt.time
if arrival_time.upper().endswith("AM") or arrival_time.upper().endswith("PM"):
    if " " not in arrival_time:
        arrival_time = arrival_time[:-2] + " " + arrival_time[-2:]
current_time = datetime.strptime(arrival_time, "%I:%M %p").time()

filtered_places = places_df[
    (places_df["Location"].str.lower() == city.lower()) &
    (places_df["Open Time"] <= current_time) &
    (places_df["Close Time"] >= current_time) &
    (places_df["Safety"].str.lower() == "safe")
].copy()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

filtered_places["Distance (km)"] = filtered_places.apply(
    lambda row: calculate_distance(user_lat, user_lon, row["Latitude"], row["Longitude"]), axis=1
)

filtered_places = filtered_places.sort_values("Distance (km)")

print(f"\n Available Trains to {city.title()}:\n")
print(trains_df[trains_df["Destination"].str.lower() == city.lower()][
    ["Train Name", "Source", "Departure Time", "Arrival Time"]
].to_string(index=False))

if filtered_places.empty:
    print("\n Sorry! No safe and open places found at this time.")
else:
    print(f"\n Recommended Places in {city.title()} (based on your arrival at {arrival_time}):\n")
    print(filtered_places[
        ["Place Name", "Category", "Ratings", "Distance (km)", "Open Time", "Close Time"]
    ].to_string(index=False))
