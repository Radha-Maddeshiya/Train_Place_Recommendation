import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

place_file   = "place_details.csv"
train_file   = "Train_details.csv"
station_file = "city_station_location.csv"

places_df  = pd.read_csv(place_file, encoding='latin1')
trains_df  = pd.read_csv(train_file)
station_df = pd.read_csv(station_file)

city         = input("Enter your city : ").strip()
arrival_text = input("Enter your arrival time (e.g. 06:30 AM) : ").strip()
available_hr = float(input("How many hours can you spare? : ").strip())
time_limit   = int(available_hr * 60)                    

station = station_df[station_df["City"].str.lower() == city.lower()]
if station.empty:
    print("City station location not found."); exit()
user_lat, user_lon = station.iloc[0][["Latitude", "Longitude"]]

places_df["Open Time"]  = places_df["Open Time"].str.strip().str.lower().replace(
    {"open 24 hours": "12:00 AM", "24 hours": "12:00 AM"})
places_df["Close Time"] = places_df["Close Time"].str.strip().str.lower().replace(
    {"open 24 hours": "11:59 PM", "24 hours": "11:59 PM"})

places_df["Open Time"]  = pd.to_datetime(places_df["Open Time"],  format="%I:%M %p").dt.time
places_df["Close Time"] = pd.to_datetime(places_df["Close Time"], format="%I:%M %p").dt.time

arrival_text = arrival_text.strip().upper().replace("AM"," AM").replace("PM"," PM").replace("  "," ")
current_time = datetime.strptime(arrival_text, "%I:%M %p").time()

places = places_df[
    (places_df["Location"].str.lower() == city.lower()) &
    (places_df["Close Time"] >= current_time) &
    (places_df["Safety"].str.lower() == "safe")
].copy()

def haversine(lat1, lon1, lat2, lon2):
    R=6371.0
    lat1,lon1,lat2,lon2 = map(radians,[lat1,lon1,lat2,lon2])
    dlat,dlon = lat2-lat1, lon2-lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R*2*atan2(sqrt(a), sqrt(1-a))

places["Distance (km)"] = places.apply(
    lambda r: round(haversine(user_lat,user_lon,r["Latitude"],r["Longitude"]),2), axis=1)

CAT_VISIT = {
    'Historical':60,'Monument':45,'Religious':45,'Museum':60,'Park':45,
    'Garden':45,'Wildlife':120,'Market':90,'Ghat':30,'Scenic':45,
    'Heritage':60,'Beach':60,'Hill Station':120,'Science':60,'Campus':60
}
DEFAULT_VISIT = 45

def visit_time(cat): return CAT_VISIT.get(cat, DEFAULT_VISIT)

def travel_time(dist_km):
    return max(5, int(dist_km/4*60)) if dist_km<0.8 else int(dist_km/20*60)+5

itinerary, total_min = [], 0
unseen = places.sort_values("Distance (km)").copy()
curr_lat, curr_lon = user_lat, user_lon

while not unseen.empty:
    idx  = ((unseen[["Latitude","Longitude"]] - [curr_lat,curr_lon])**2).sum(1).idxmin()
    spot = unseen.loc[idx]

    move_min  = travel_time(haversine(curr_lat,curr_lon,spot["Latitude"],spot["Longitude"])) if itinerary else 0
    visit_min = visit_time(spot["Category"])

    if total_min + move_min + visit_min > time_limit:
        break

    spot = spot.copy()  
    spot["MoveMin"]  = move_min
    spot["VisitMin"] = visit_min

    itinerary.append(spot)

    total_min += move_min + visit_min
    curr_lat, curr_lon = spot["Latitude"], spot["Longitude"]
    unseen = unseen.drop(idx)

print(f"\n🗺️ Time-bound Itinerary in {city.title()} (you have {available_hr} h):\n")
for i, row in enumerate(itinerary,1):
    print(f"{i}. {row['Place Name']} – {row['VisitMin']} min visit")
    if row['MoveMin']:
        icon = "🚶" if row['MoveMin']<=10 else "🚗"
        print(f"   {icon} {row['MoveMin']} min travel")
print(f"\n ⏱️ Planned time: {total_min} min | Spare: {time_limit-total_min} min")

all_city_places = places_df[places_df["Location"].str.lower() == city.lower()]
shown_names = [p["Place Name"] for p in itinerary]
others = all_city_places[~all_city_places["Place Name"].isin(shown_names)]

print(f"\n📍 All Other Places in {city.title()}:\n")
if others.empty:
    print("No more places to show.")
else:
    for p in others["Place Name"].unique():
        print(p)


print(f"\nAvailable Trains to {city.title()}:\n")
trains = trains_df[trains_df["Destination"].str.lower()==city.lower()][
          ["Train Name","Source","Departure Time","Arrival Time"]]
print("No trains found." if trains.empty else trains.to_string(index=False))
