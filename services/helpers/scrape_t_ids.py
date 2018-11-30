from config import config
import requests, json
import yaml, re
import copy

KEY = { 'api_key': config.api_key }
MBTAENDPOINT = 'https://api-v3.mbta.com/{}'

# YML Keys
STATION_ID     = 'station_id'
PLACE_ID       = 'place_id'
ROUTE_TYPE     = 'route_type'
DIRECTION_TYPE = 'direction_type'
STATION_LINE   = 'station_line'

#List of Supported Lines
SUPPORTED_LINES = ['Orange Line', 'Red Line', 'Blue Line', 'Green Line', 'Mattapan Trolley']

# Directions per line
NORTH_SOUTH      = ['Orange Line', 'Red Line']
EAST_WEST        = ['Blue Line', 'Green Line']
INBOUND_OUTBOUND = ['Mattapan Trolley']

# Type of rail - green should be the only light rail
LIGHT_RAIL = '0'
HEAVY_RAIL = '1'


'''
    Helper to parse description which contains the color of the station.
    The color then tells us the direction type. North-South or East-West
'''
def get_train_direction_type(description):
    north_south      = ['north', 'south']
    east_west        = ['east', 'west']
    inbound_outbound = ['inbound', 'outbound']
    for color in SUPPORTED_LINES:
        pattern = re.compile(color)
        found_color = re.findall(pattern, description)
        if found_color:
            the_color = found_color[0]
            if the_color in NORTH_SOUTH:
                return the_color.split()[0], north_south
            elif the_color in EAST_WEST:
                return the_color.split()[0], east_west
            elif the_color in INBOUND_OUTBOUND:
                return the_color.split()[0], inbound_outbound
            else:
                raise ValueError('Couldn\'t find a matching supported color.')
    raise ValueError('Couldn\'t find the color type for this description')


def parse_name_and_ids(route_type):
    alerts_endpoint = MBTAENDPOINT.format('stops/?filter[route_type]=' + route_type)
    r = requests.get(alerts_endpoint, data=KEY)
    all_t_stations = json.loads(r.text)['data']

    # Dictionary of name, id pairs for every T Subway Station
    t_names_and_ids = {}
    for station in all_t_stations:
        # Strange case where / in name JFK/UMASS we have to duplicate the entry
        first_half = ''
        second_half = ''
        station_name = station['attributes']['name'].upper()
        duplicate_entry = True if '/' in station_name else False
        if duplicate_entry:
            first_half = station['attributes']['name'].upper().split('/')[0]
            second_half = station['attributes']['name'].upper().split('/')[1]

        station_line, station_direction = get_train_direction_type(station['attributes']['description'])
        station_id = station['id']
        station_string_id = station['relationships']['parent_station']['data']['id']
        if station_name not in t_names_and_ids:
            #Doesn't exist yet, create it
            station_info = {STATION_ID: station_id, PLACE_ID: station_string_id,
                            DIRECTION_TYPE: station_direction.copy(),
                            STATION_LINE: station_line,
                            ROUTE_TYPE: route_type}
            t_names_and_ids[station_name] = station_info

            if duplicate_entry:
                t_names_and_ids[first_half] = copy.deepcopy(station_info)
                t_names_and_ids[second_half] = copy.deepcopy(station_info)

        else:
            if isinstance(t_names_and_ids[station_name][STATION_ID], list):
                new_list_of_station_ids = t_names_and_ids[station_name][STATION_ID]
                new_list_of_station_ids.append(station_id)
                t_names_and_ids[station_name][STATION_ID] = new_list_of_station_ids

                if duplicate_entry:
                    t_names_and_ids[first_half][STATION_ID] = copy.deepcopy(new_list_of_station_ids)
                    t_names_and_ids[second_half][STATION_ID] = new_list_of_station_ids.copy()
            else:
                list_of_station_ids = [t_names_and_ids[station_name][STATION_ID]]
                list_of_station_ids.append(station_id)
                t_names_and_ids[station_name][STATION_ID] = list_of_station_ids

                if duplicate_entry:
                    t_names_and_ids[first_half][STATION_ID] = copy.deepcopy(list_of_station_ids)
                    t_names_and_ids[second_half][STATION_ID] = copy.deepcopy(list_of_station_ids)
    return t_names_and_ids


def write_to_yml(parsed_data):
    with open('t_station_ids.yml', 'w') as outfile:
        yaml.dump(parsed_data, outfile, default_flow_style=False)

light_rail = parse_name_and_ids(LIGHT_RAIL)
heavy_rail = parse_name_and_ids(HEAVY_RAIL)
light_and_heavy = {**light_rail, **heavy_rail}
write_to_yml(light_and_heavy)



