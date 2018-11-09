from config import config
import requests, json
import yaml

KEY = { 'api_key': config.api_key }
MBTAENDPOINT = 'https://api-v3.mbta.com/{}'

'''
    Helper function to scrape all the stop ids
'''
def get_stop_ids():
    alerts_endpoint = MBTAENDPOINT.format('stops/?filter[route_type]=1')
    r = requests.get(alerts_endpoint, data=KEY)
    res = json.loads(r.text)
    return res['data']


def parse_name_and_ids(all_t_stations):
    # Dictionary of name, id pairs for every T Subway Station
    t_names_and_ids = {}
    for station in all_t_stations:
        station_name = station['attributes']['name']
        station_id = station['id']
        if station_name not in t_names_and_ids:
            t_names_and_ids[station_name] = [station_id]
        else:
            t_names_and_ids[station_name].append(station_id)
    return t_names_and_ids


def write_to_yml(parsed_data):
    with open('t_station_ids.yml', 'w') as outfile:
        yaml.dump(parsed_data, outfile, default_flow_style=False)


data = get_stop_ids()
parsed_data = parse_name_and_ids(data)
write_to_yml(parsed_data)



