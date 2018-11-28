import re, requests, json, yaml
from datetime import datetime
from services.helpers import consts

train_info = yaml.load(open('services/translations/t_station_ids.yml'))
direction_translations = yaml.load(open('services/translations/direction_translations.yml'))

def translate_time(departure_time):
    time_format = '%H:%M:%S'
    current_time = datetime.now().time().strftime(time_format)
    parsed_time = re.search('(.*)T(.*)-(.*)', departure_time)
    parsed_time = parsed_time.group(2)
    tdelta = datetime.strptime(parsed_time, time_format) - datetime.strptime(current_time, time_format)
    return str(tdelta)


'''
    Helper function to get a delta timestamp and return either mins of seconds for the phrase
'''
def get_mins_or_sec(time_until_departure):

    mins = " minute"
    secs = " second"

    parsed_time = re.search('(.*):(.*):(.*)', time_until_departure)
    minutes_time = int(parsed_time.group(2))
    seconds_time = int(parsed_time.group(3))

    if is_plural(seconds_time):
        secs += "s"

    if is_plural(minutes_time):
        mins += "s"

    if minutes_time == 0 and seconds_time != 0:
        return str(seconds_time) + secs
    elif minutes_time != 0 and seconds_time == 0:
        return str(minutes_time) + mins
    elif minutes_time != 0 and seconds_time != 0:
        return str(minutes_time) + mins + " " + str(seconds_time) + secs
    else:
        return ""


def get_predicted_train_departure(station_name, requested_direction):
    translated_station_name = station_name.upper()
    # Do a check if the station id is not there
    station_id = train_info[translated_station_name]['place_id']
    route_type = train_info[translated_station_name]['route_type']
    valid_directions_for_station = train_info[translated_station_name]['direction_type']

    # The station doesn't go in the direction the user has requested so we'll ask a for a valid one
    if requested_direction not in valid_directions_for_station:
        return False, valid_directions_for_station

    translated_direction = direction_translations[requested_direction.upper()]
    prediction_endpoint = consts.MBTAENDPOINT.format(
        '/predictions?filter%5Bstop%5D=' + station_id + '&filter%5Bdirection_id%5D='
                                + translated_direction + '&include=stop,trip&filter[route_type]=' + route_type)
    r = requests.get(prediction_endpoint, data=consts.KEY)
    res = json.loads(r.text)

    # Only return the first 5 train times
    prediction_data = res['data'][:5]

    # API doesn't reliably return the timestamps sorted, so we do it here
    sorted_prediction_data = sorted(prediction_data, key=lambda k: k['attributes']['departure_time'])

    return True, sorted_prediction_data


def is_plural(num):
    return num > 1

