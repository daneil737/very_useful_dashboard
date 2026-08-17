from flask import Flask, render_template
import requests
import os


GOAL_API_KEY = os.environ["GOAL_API_KEY"]
GEOCODE_API_KEY = os.environ["GEOCODE_API_KEY"]


app = Flask(__name__)

def get_weather():
    LAT = "53.5484398"
    LONG = "-2.522554"
    api_call_str = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LONG}&current=temperature_2m,rain,wind_speed_10m,wind_direction_10m&wind_speed_unit=ms"
    weather_request = requests.get(api_call_str)
    temperature = weather_request.json()["current"]["temperature_2m"]
    rain = weather_request.json()["current"]["rain"]
    wind = weather_request.json()["current"]["wind_speed_10m"]
    wind_direction_deg = weather_request.json()["current"]["wind_direction_10m"]

    if wind_direction_deg >=337  or wind_direction_deg < 22: wind_direction = "North"
    elif wind_direction_deg < 67: wind_direction = "North-East"
    elif wind_direction_deg < 112: wind_direction = "East"
    elif wind_direction_deg < 157: wind_direction = "South-East"
    elif wind_direction_deg < 202: wind_direction = "Sout"
    elif wind_direction_deg < 247: wind_direction = "South-West"
    elif wind_direction_deg < 292: wind_direction = "West"
    elif wind_direction_deg < 337: wind_direction = "North-West"
    return (temperature, rain, wind, wind_direction)


def get_city():
    LAT = 53.5484398
    LONG = -2.522554
    api_call_str = f"http://api.openweathermap.org/geo/1.0/reverse?lat={LAT}&lon={LONG}&limit=2&appid={GEOCODE_API_KEY}"
    geocode_request = requests.get(api_call_str)
    return (geocode_request.json()[0]["name"], geocode_request.json()[0]["state"])


@app.route("/")
def mainpage():
    api_temperature, api_rain, api_wind, api_wind_dir = get_weather()
    api_city, api_state = get_city()

    api_weather_data = {
        "city": api_city,
        "state": api_state,
        "temperature": api_temperature,
        "rain": api_rain,
        "wind": api_wind,
        "wind_direction": api_wind_dir
    }
    
    return render_template("index.html", weather_data=api_weather_data)
