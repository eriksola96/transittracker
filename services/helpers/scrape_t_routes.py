from config import config
import requests, json
import yaml

KEY = { 'api_key': config.api_key }
MBTAENDPOINT = 'https://api-v3.mbta.com/{}'

# Type of rail - green should be the only light rail
LIGHT_RAIL = '0'
HEAVY_RAIL = '1'

def parse_station_routes(route_type, lines):
    t_names_and_routes = {}

    for line in lines:
        list_of_stations_in_line = []
        alerts_endpoint = MBTAENDPOINT.format('stops/?filter[type]=' + route_type +
                                          '&filter[route]=' + line)

        r = requests.get(alerts_endpoint, data=KEY)
        all_t_stations = json.loads(r.text)['data']

        # Dictionary of Line Name, and a list of all Stations in its route
        for station in all_t_stations:
            station_name = station['attributes']['name']
            list_of_stations_in_line.append(station_name)

        t_names_and_routes[line] = list_of_stations_in_line

    return t_names_and_routes


def write_to_yml(parsed_data):
    with open('t_routes.yml', 'w') as outfile:
        yaml.dump(parsed_data, outfile, default_flow_style=False)

heavy_rails = ['Orange', 'Red', 'Blue']
light_rails = ['Mattapan', 'Green-B', 'Green-C', 'Green-D', 'Green-E']


light = parse_station_routes(LIGHT_RAIL, light_rails)
heavy = parse_station_routes(HEAVY_RAIL, heavy_rails)

light_and_heavy = {**light, **heavy}
write_to_yml(light_and_heavy)



