import folium
from geopy.geocoders import Nominatim
from geopy import distance
import json
import os
from flask import Flask, send_from_directory


app = Flask(__name__)


def get_distance(lat1, lon1, lat2, lon2):
    return distance.distance((lat1, lon1), (lat2, lon2)).km


geolocator = Nominatim(user_agent="coffee_locator")


def load_coffeeshops_from_file():
    with open("coffee.json", "r", encoding="CP1251") as file:
        return json.load(file)


address = input("Введите адрес для поиска ближайших кофеен: ")


def generate_map():
    coffeeshops = load_coffeeshops_from_file()
    known_locations = {"метро арбатская": (55.7522, 37.6036)}
    location = geolocator.geocode(f"{address}, Москва, Россия")
    if location:
        user_lat, user_lon = location.latitude, location.longitude
    elif address.lower() in known_locations:
        user_lat, user_lon = known_locations[address.lower()]
    else:
        return
    
    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    coffeeshops_sorted = sorted(
        coffeeshops,
        key=lambda shop: get_distance(user_lat, user_lon, float(shop["Latitude_WGS84"]), float(shop["Longitude_WGS84"]))
    )
    closest_coffeeshops = coffeeshops_sorted[:5]
    for shop in closest_coffeeshops:
        folium.Marker(
            location=[float(shop["Latitude_WGS84"]), float(shop["Longitude_WGS84"])],
            popup=shop["Name"]
        ).add_to(m)
    
    map_file_path = "map.html"
    m.save(map_file_path)
    print(f"http://127.0.0.1:5000/map.html")
    return map_file_path


map_file_path = generate_map()


@app.route('/')
def home():
    return '<a href="/map.html">ссылке</a>.'


@app.route('/map.html')
def map_view():
    return send_from_directory(os.getcwd(), 'map.html')


if __name__ == "__main__":
    app.run()