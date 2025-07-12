import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

place_file = "place_details.csv"
train_file = "Train_details.csv"
station_file = "city_station_location.csv"

places_df = pd.read_csv(place_file, encoding='latin1') 
trains_df = pd.read_csv(train_file)
station_df = pd.read_csv(station_file)

city = input("Enter your city : ").strip()
arrival_time = input("Enter your arrival time : ").strip()

station_data = station_df[station_df["City"].str.lower() == city.lower()]
if not station_data.empty:
    user_lat = station_data.iloc[0]["Latitude"]
    user_lon = station_data.iloc[0]["Longitude"]
else:
    print("City station location not found.")
    exit()

places_df["Open Time"] = places_df["Open Time"].replace("Open 24 Hours", "12:00 AM")
places_df["Close Time"] = places_df["Close Time"].replace("Open 24 Hours", "11:59 PM")

places_df["Open Time"] = pd.to_datetime(places_df["Open Time"], format="%I:%M %p").dt.time
places_df["Close Time"] = pd.to_datetime(places_df["Close Time"], format="%I:%M %p").dt.time

places_df["Open Time 12hr"] = places_df["Open Time"].apply(lambda x: x.strftime("%I:%M %p"))
places_df["Close Time 12hr"] = places_df["Close Time"].apply(lambda x: x.strftime("%I:%M %p"))

arrival_time = arrival_time.upper().replace("AM", " AM").replace("PM", " PM").replace("  ", " ")
current_time = datetime.strptime(arrival_time.strip(), "%I:%M %p").time()

filtered_places = places_df[
    (places_df["Location"].str.lower() == city.lower()) &
    (places_df["Close Time"] >= current_time) &
    (places_df["Safety"].str.lower() == "safe")
].copy()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)


filtered_places["Distance (km)"] = filtered_places.apply(
    lambda row: calculate_distance(user_lat, user_lon, row["Latitude"], row["Longitude"]), axis=1
)
filtered_places["Map Link"] = filtered_places.apply(
    lambda row: f"https://www.google.com/maps?q={row['Latitude']},{row['Longitude']}", axis=1
)

filtered_places = filtered_places.sort_values("Distance (km)")

print(f"\n Available Trains to {city.title()}:\n")
train_results = trains_df[trains_df["Destination"].str.lower() == city.lower()][
    ["Train Name", "Source", "Departure Time", "Arrival Time"]
]
if train_results.empty:
    print("No trains found for this destination.")
else:
    print(train_results.to_string(index=False))

if filtered_places.empty:
    print("\n Sorry! No safe and open places found at this time.")
else:
    print(f"\n🗺️ Recommended Itinerary in {city.title()} (starting around {arrival_time}):\n")

    # ---------- Build Smart Itinerary ----------
    itinerary = []
    unseen = filtered_places.copy()
    curr_lat, curr_lon = user_lat, user_lon

    while not unseen.empty:
        idx = ((unseen[["Latitude", "Longitude"]] - [curr_lat, curr_lon])**2).sum(1).idxmin()
        spot = unseen.loc[idx]
        itinerary.append(spot)
        unseen = unseen.drop(idx)

        near = unseen[unseen.apply(
            lambda r: calculate_distance(spot["Latitude"], spot["Longitude"], r["Latitude"], r["Longitude"]) < 0.8,
            axis=1)]
        if not near.empty:
            for _, near_row in near.iterrows():
                itinerary.append(near_row)
            unseen = unseen.drop(near.index)

        curr_lat, curr_lon = itinerary[-1][["Latitude", "Longitude"]]

    # ---------- Show Itinerary ----------
    for i, row in enumerate(itinerary):
        print(f"🔸 {row['Place Name']} (opens at {row['Open Time'].strftime('%I:%M %p')})")
        if i < len(itinerary) - 1:
            next_place = itinerary[i+1]
            dist = calculate_distance(row['Latitude'], row['Longitude'], next_place['Latitude'], next_place['Longitude'])
            if dist < 0.8:
                print(f"   🚶 Walk {int(dist * 1000)}m to {next_place['Place Name']}")
            else:
                print(f"   🚗 Auto to {next_place['Place Name']} ({dist} km)")

    # ---------- All Notable Places ----------
    print(f"\n📍 All Notable Places in {city.title()}:\n")
    for pname in filtered_places["Place Name"].unique():
        print(f"{pname}")
