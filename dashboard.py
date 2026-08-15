from flask import Flask, render_template
import requests

app = Flask(__name__)

def get_weather():
    LAT = "53.5489"
    LONG = "2.5246"
    api_call_str = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LONG}&current=temperature_2m,relative_humidity_2m,apparent_temperature"
    weather_request = requests.get(api_call_str)
    #print(weather_request.json()["current"]["temperature_2m"])
    return weather_request.json()["current"]["temperature_2m"]

@app.route("/")
def mainpage(temp=None):
    temp = get_weather()
    return render_template("index.html", temperature=temp)
