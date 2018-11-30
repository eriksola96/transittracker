import requests, json, yaml
from services.helpers import consts

alerts_translate = yaml.load(open('services/translations/alert_translations.yml'))
train_info = yaml.load(open('services/translations/t_station_ids.yml'))
line_info = yaml.load(open('services/translations/t_routes.yml'))


def get_alerts_present_for_station(station_name):
    station_line = train_info[station_name.upper()]['station_line']
    station_place = train_info[station_name.upper()]['place_id']
    alerts_endpoint = consts.MBTAENDPOINT.format('alerts/?filter[route]=' + station_line +
                                                 '&filter[stop]=' + station_place)
    r = requests.get(alerts_endpoint, data=consts.KEY)
    res = json.loads(r.text)
    return res['data']


def parse_multiple_alerts(alerts):
    speech_output = "Yeah, there's a few. "
    for alert in alerts:
        cause = alert['attributes']['cause']
        effect = alert['attributes']['effect']
        cause_and_effect = " Alert for %s and it's gonna cause %s." % (alerts_translate[cause], alerts_translate[effect])
        speech_output += cause_and_effect
    return speech_output


'''
    Returns speech output for alerts in between stops, only supports same line at the moment
'''
def get_alerts_in_between_stops(from_station, to_station):
    # These are known alerts that could more commonly effect a user
    delay_alerts = ['DELAY', 'CANCELLATION', 'NO_SERVICE', 'PARKING_CLOSURE', 'PARKING_ISSUE',
                    'STATION_CLOSURE', 'TRACK_CHANGE']
    from_station, to_station = from_station.upper(), to_station.upper()
    speech_output = "Sorry, only same line stations are supported at the moment."
    from_line_color = train_info[from_station]['station_line']
    to_line_color = train_info[to_station]['station_line']
    if from_line_color != to_line_color:
        return speech_output

    stations_in_between = get_in_between(from_station, to_station, to_line_color)

    # Endpoint that retrieves all stops at a given station
    get_stops_endpoint = build_alerts_endpoints(stations_in_between, to_line_color)

    r = requests.get(get_stops_endpoint, data=consts.KEY)
    res = json.loads(r.text)

    alerts_data = res['data']
    announce_alerts = [alert for alert in alerts_data if alert['attributes']['effect'] in delay_alerts]

    # No alerts that we care about
    if not announce_alerts:
        speech_output = "There aren't any alerts that would cause you trouble from " + from_station + " to " + to_station + "."
    else:
        speech_output = parse_alerts_and_get_locations(announce_alerts, stations_in_between)
    return speech_output


def get_in_between(from_station, to_station, line):
    station_list = line_info[line]
    from_station_index = station_list.index(from_station)
    to_station_index = station_list.index(to_station)

    return station_list[from_station_index : to_station_index + 1]


def build_alerts_endpoints(stations_in_between, line):
    place_ids = [train_info[station]['place_id'] for station in stations_in_between]
    endpoint = consts.MBTAENDPOINT.format('alerts?filter[route]=' + line +
                            '&filter%5Bstop%5D=' + ','.join(place_ids))
    return endpoint


def parse_alerts_and_get_locations(alerts, stations_traveled):
    place_ids = [train_info[station]['place_id'] for station in stations_traveled]
    speech_output = ""
    for alert in alerts:
        cause = alert['attributes']['cause']
        effect = alert['attributes']['effect']
        stations_effected = []
        stations_traveled_and_effected = ''
        for place in alert['attributes']['informed_entity']:
            if place['stop'] in place_ids:
                stations_effected.append(place['stop'])

            stations_traveled_and_effected = [station for station in stations_traveled
                                                    if train_info[station]['place_id'] in stations_effected]
        cause_and_effect = " Alert at %s for %s and it's gonna cause %s." % (
        ', '.join(stations_traveled_and_effected), alerts_translate[cause], alerts_translate[effect])
        speech_output += cause_and_effect
    return speech_output

print(get_alerts_in_between_stops("Ashmont", "broadway"))