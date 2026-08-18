from flask import Flask, render_template
import requests
import os


GOAL_API_KEY = os.environ["GOAL_API_KEY"]
GEOCODE_API_KEY = os.environ["GEOCODE_API_KEY"]
LAT = 53.5484398
LONG = -2.522554

app = Flask(__name__)

def get_weather():
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
    api_call_str = f"http://api.openweathermap.org/geo/1.0/reverse?lat={LAT}&lon={LONG}&limit=2&appid={GEOCODE_API_KEY}"
    geocode_request = requests.get(api_call_str)
    return (geocode_request.json()[0]["name"], geocode_request.json()[0]["state"])


def call_goal_api(api_url):
    headers = {
        "Authorization" : GOAL_API_KEY
    }
    response = requests.get(api_url, headers=headers)
    return response.json()['data']


def get_next_match(api_response):
    next_match = [match for match in api_response if match['matchStatus'] == "SCHEDULED"][-1]
    return {"date": next_match['matchDate'],
            "time": next_match['matchTime'],
            "home_team": next_match['homeTeam']['name'],
            "away_team": next_match['awayTeam']['name']}


def get_last_match(api_response):
    last_match = [match for match in api_response if match['matchStatus'] == "FINISHED"][0]
    return {"date": last_match['matchDate'],
            "time": last_match['matchTime'],
            "home_team": last_match['homeTeam']['name'],
            "away_team": last_match['awayTeam']['name'],
            "score": f"{last_match['homeTeamFtScore']}:{last_match['awayTeamFtScore']}"}


def get_standings_table_piece(api_response):
    formated_standings_table = [{
        "team_position": team["overallLeaguePosition"],
        "team_name": team["team"]["name"],
        "matches_played": team["overallLeaguePlayed"],
        "points": team["overallLeaguePTS"]
    } for team in api_response]
    formated_standings_table = [formated_standings_table[0]] + formated_standings_table[10:] + formated_standings_table[1:10]
    pogon_szczecin_position = int(next(filter(lambda team: team["team_name"] == "Pogoń Szczecin", formated_standings_table))["team_position"])

    if pogon_szczecin_position == 1 or pogon_szczecin_position == 2 or pogon_szczecin_position == 3:
        return formated_standings_table[:5]
    elif pogon_szczecin_position == 16 or pogon_szczecin_position == 17 or pogon_szczecin_position == 18:
        return formated_standings_table[13:]
    else:
        return formated_standings_table[pogon_szczecin_position-3:pogon_szczecin_position+2]


def call_zditm_api():
    url = "https://www.zditm.szczecin.pl/api/v2/departure-boards/15111?limit=6&format=json"
    stop_departures_table = requests.get(url)
    stop_departures_table = stop_departures_table.json()['data']['departures']
    formatted_departures_table = [{
        "bus_number": departure['line']['number'],
        "bus_direction": departure['trip']['headsign']['short'],
        "estimated_departure_time": departure['departure_time']['estimated'].split('T')[-1][:5]
    } for departure in stop_departures_table]
    return formatted_departures_table


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


    goal_fixtures_api_response = call_goal_api("https://api.goal-api.com/v1/teams/cmri4pc28d2lclb07pr43de75/fixtures")
    api_last_match_data = get_last_match(goal_fixtures_api_response)
    api_next_match_data = get_next_match(goal_fixtures_api_response)


    goal_standings_api_response = call_goal_api("https://api.goal-api.com/v1/standings/cmr77dw8j00gerx06xvshbkow")
    api_standings_table_piece = get_standings_table_piece(goal_standings_api_response)


    api_stop_departures_table = call_zditm_api()
    
    return render_template("index.html",
                           weather_data=api_weather_data,
                           stop_departures_table=api_stop_departures_table,
                           last_match_data=api_last_match_data,
                           next_match_data=api_next_match_data,
                           standings_table_piece=api_standings_table_piece)
