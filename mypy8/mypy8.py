import folium
from flask import Flask, render_template_string, request
from geopy.geocoders import Nominatim
from geopy import distance
import json

app = Flask(__name__)

def get_distance(lat1, lon1, lat2, lon2):
    return distance.distance((lat1, lon1), (lat2, lon2)).km

geolocator = Nominatim(user_agent="coffee_locator")

def load_coffeeshops_from_file():
    with open("coffee.json", "r", encoding="CP1251") as file:
        return json.load(file)

@app.route("/", methods=["GET", "POST"])
def show_map():
    coffeeshops = load_coffeeshops_from_file()
    user_lat, user_lon = 55.7558, 37.6173

    if request.method == "POST":
        address = request.form["address"]
        location = geolocator.geocode(address)
        if location:
            user_lat, user_lon = location.latitude, location.longitude
        else:
            return "Адрес не найден"

    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    coffeeshops_sorted = sorted(
        coffeeshops,
        key=lambda shop: get_distance(
            user_lat, user_lon, float(shop["Latitude_WGS84"]), float(shop["Longitude_WGS84"])
        )
    )[:5]

    for shop in coffeeshops_sorted:
        folium.Marker(
            location=[float(shop["Latitude_WGS84"]), float(shop["Longitude_WGS84"])],
            popup=shop["Name"]
        ).add_to(m)

    map_html = m._repr_html_()
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Карта кофеен</title>
        </head>
        <body>
            <h1>Карта кофеен</h1>
            <form method="POST">
                <input type="text" name="address" placeholder="Введите адрес" required>
                <input type="submit" value="Найти">
            </form>
            <div>{{ map_html|safe }}</div>
        </body>
        </html>
    """, map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True)