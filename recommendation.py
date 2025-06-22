import pandas as pd
from sklearn.neighbors import NearestNeighbors

df_trains = pd.read_csv("Train_details.csv")
df_places = pd.read_csv("place_details.csv")
df_trains["Destination_Coords"] = df_trains[["Destination_Lat", "Destination_Lon"]].values.tolist()
df_places["Coords"] = df_places[["Latitude", "Longitude"]].values.tolist()

knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
knn.fit(df_places["Coords"].tolist())

def recommend(destination):
    print(f"\n Trains to {destination.title()}:")
    trains = df_trains[df_trains['Destination'].str.lower() == destination.lower()]
    
    if trains.empty:
        print(" No trains found for this destination.")
        return

    print(trains[['Train Name', 'Source', 'Departure Time', 'Arrival Time']].to_string(index=False))
    
    dest_coords = trains.iloc[0][['Destination_Lat', 'Destination_Lon']].tolist()

    print(f"\n Nearby places to visit from {destination.title()}:")
    distances, indices = knn.kneighbors([dest_coords])
    
    for i in indices[0]:
        place = df_places.iloc[i]
        print(f" {place['Place Name']} ({place['Location']}) - {place['Category']} - {place['Ratings']}★")


print("\n Welcome to Train & Place Recommendation System!")
user_input = input(" Please enter your destination: ")
recommend(user_input)
