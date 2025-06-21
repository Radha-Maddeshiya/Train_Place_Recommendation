
import pandas as pd

train_data = {
    "Train Name": ["Gorakhpur Express", "Delhi Express", "Mumbai Express", "Kolkata Express", "Lucknow Express"],
    "Source": ["Gorakhpur", "Delhi", "Mumbai", "Kolkata", "Lucknow"],
    "Destination": ["Lucknow", "Bhopal", "Pune", "Delhi", "Varanasi"],
    "Departure Time": ["06:00 AM", "05:15 AM", "08:00 PM", "04:30 PM", "07:45 AM"],
    "Arrival Time": ["10:30 AM", "01:30 PM", "05:00 AM", "10:00 AM", "12:15 PM"]
}

place_data = {
    "Place Name": ["Imambara", "Sanchi Stupa", "Shaniwar Wada", "India Gate", "Kashi Vishwanath Temple"],
    "Location": ["Lucknow", "Bhopal", "Pune", "Delhi", "Varanasi"],
    "Category": ["Historical", "Historical", "Historical", "Monument", "Religious"],
    "Ratings": [4.5, 4.6, 4.3, 4.7, 4.8]
}

df_trains = pd.DataFrame(train_data)
df_places = pd.DataFrame(place_data)

def recommend(destination):
    print(f"\nTrains to {destination}:")
    trains = df_trains[df_trains['Destination'].str.lower() == destination.lower()]
    print(trains[['Train Name', 'Source', 'Departure Time', 'Arrival Time']].to_string(index=False))
    
    print(f"\nPlaces to visit in {destination}:")
    places = df_places[df_places['Location'].str.lower() == destination.lower()]
    print(places[['Place Name', 'Category', 'Ratings']].to_string(index=False))

user_input = input("Enter your destination: ")
recommend(user_input)