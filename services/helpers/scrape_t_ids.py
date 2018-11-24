from config import config
import requests, json
import yaml

KEY = { 'api_key': config.api_key }
MBTAENDPOINT = 'https://api-v3.mbta.com/{}'

LIGHT_RAIL = '0'
HEAVY_RAIL = '1'

def parse_name_and_ids(route_type):
    alerts_endpoint = MBTAENDPOINT.format('stops/?filter[route_type]=' + route_type)
    r = requests.get(alerts_endpoint, data=KEY)
    all_t_stations = json.loads(r.text)['data']

    # Dictionary of name, id pairs for every T Subway Station
    t_names_and_ids = {}
    for station in all_t_stations:
        station_name = station['attributes']['name'].upper()
        station_id = station['id']
        station_string_id = station['relationships']['parent_station']['data']['id']
        if station_name not in t_names_and_ids:
            station_info = [station_id, station_string_id, route_type]
            t_names_and_ids[station_name] = station_info
        else:
            t_names_and_ids[station_name].append(station_id)
    return t_names_and_ids


def write_to_yml(parsed_data):
    with open('t_station_ids.yml', 'w') as outfile:
        yaml.dump(parsed_data, outfile, default_flow_style=False)

light_rail = parse_name_and_ids(LIGHT_RAIL)
heavy_rail = parse_name_and_ids(HEAVY_RAIL)
light_and_heavy = {**light_rail, **heavy_rail}
write_to_yml(light_and_heavy)



