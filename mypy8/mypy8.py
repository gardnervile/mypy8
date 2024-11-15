import folium
from geopy import distance
import json
import os
from flask import Flask, send_from_directory
import requests
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

def get_distance(lat1, lon1, lat2, lon2):
    return distance.distance((lat1, lon1), (lat2, lon2)).km


def load_coffeeshops_from_file():
    with open("coffee.json", "r", encoding="CP1251") as file:
        return json.load(file)


def fetch_coordinates(address):
    apikey = os.getenv("YANDEX_API_KEY")
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def generate_map():
    address = input("Введите адрес для поиска ближайших кофеен: ")
    coffeeshops = load_coffeeshops_from_file()

    coordinates = fetch_coordinates(f"{address}, Москва, Россия")

    if not coordinates:
        return

    user_lat, user_lon = coordinates

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
    print("Карта доступна по адресу: http://127.0.0.1:5000/map.html")
    return map_file_path


map_file_path = generate_map()


@app.route('/')
def home():
    return '<a href="/map.html">Открыть карту</a>.'


@app.route('/map.html')
def map_view():
    return send_from_directory(os.getcwd(), 'map.html')


if __name__ == "__main__":
    app.run()