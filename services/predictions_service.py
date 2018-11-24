import re, requests, json, yaml
from datetime import datetime
from services.helpers import consts

train_ids = yaml.load(open('services/translations/t_station_ids.yml'))
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

    if isPlural(seconds_time):
        secs += "s"

    if isPlural(minutes_time):
        mins += "s"

    if minutes_time == 0 and seconds_time != 0:
        return str(seconds_time) + secs
    elif minutes_time != 0 and seconds_time == 0:
        return str(minutes_time) + mins
    elif minutes_time != 0 and seconds_time != 0:
        return str(minutes_time) + mins + " " + str(seconds_time) + secs
    else:
        return ""


def get_predicted_train_departure(station_name, direction):
    # Do a check if the station id is not there
    station_id = train_ids[station_name.upper()][1]
    route_type = train_ids[station_name.upper()][2]

    #### NEED TO DO ERROR CHECKING ON DIRECTIONS ####
    translated_direction = direction_translations[direction.upper()]
    prediction_endpoint = consts.MBTAENDPOINT.format(
        '/predictions?filter%5Bstop%5D=' + station_id + '&filter%5Bdirection_id%5D='
                                + translated_direction + '&include=stop,trip&filter[route_type]=' + route_type)
    r = requests.get(prediction_endpoint, data=consts.KEY)
    res = json.loads(r.text)
    return res['data']


def isPlural(num):
    return num > 1
