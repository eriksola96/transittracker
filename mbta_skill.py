import logging
from config import config
from helpers import helpers as help


import re
from datetime import datetime
import yaml
import requests
import json
from flask import Flask, render_template
from flask_ask import Ask, statement

MBTAENDPOINT = 'https://api-v3.mbta.com/{}'
KEY = { 'api_key': config.api_key }
translate = yaml.load(open('config/translations.yml'))
train_ids = yaml.load(open('helpers/t_station_ids.yml'))

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()


@ask.launch
def launch():
    return get_train_prediction()

@ask.intent('GetAlertForColorIntent', convert={'color': 'color'})
def get_alerts(color):
    alerts_data = get_alerts_present(color)
    if len(alerts_data) == 1:
        cause = alerts_data[0]['attributes']['cause']
        effect = alerts_data[0]['attributes']['effect']
        speech_output = "Yup, there is currently an alert for %s and it's gonna cause %s." % \
                        (translate[cause], translate[effect])
        return statement('<speak>{}</speak>'.format(speech_output))
    elif len(alerts_data) > 1:
        speech_output = parse_multiple_alerts(alerts_data)
        return statement('<speak>{}</speak>'.format(speech_output))
    else:
        speech_output = "Nope, you're in the clear"
        return statement('<speak>{}</speak>'.format(speech_output))


@ask.intent('GetTrainPredictionIntent', convert={'station_name': 'station_name'})
def get_train_prediction(station_name):
    prediction_data = get_predicted_train_departure(station_name)
    if len(prediction_data) == 0:
        speech_output = "Sorry, I can't seems to get any predictions for %s" % station_name
        return help.get_speech_text(speech_output)
    elif len(prediction_data) == 1:
        time_until_departure = translate_time(prediction_data[0]['attributes']['departure_time'])
        speech_output = "There's only one train predicted to leave from %s in %s" % (station_name, time_until_departure)
        return help.get_speech_text(speech_output)
    else:
        first_time_until_departure = translate_time(prediction_data[0]['attributes']['departure_time'])
        second_time_until_departure = translate_time(prediction_data[1]['attributes']['departure_time'])
        first_mins_or_sec = get_mins_or_sec(first_time_until_departure)
        second_mins_or_sec = get_mins_or_sec(second_time_until_departure)

        first_train = "The next train from %s is leaving in %s from now." % (station_name, first_mins_or_sec)
        second_train = " The train after that leaves in %s" % second_mins_or_sec
        speech_output = first_train + second_train
        return help.get_speech_text(speech_output)


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

    if help.isPlural(seconds_time):
        secs += "s"

    if help.isPlural(minutes_time):
        mins += "s"

    if minutes_time == 0 and seconds_time != 0:
        return str(seconds_time) + secs
    elif minutes_time != 0 and seconds_time == 0:
        return str(minutes_time) + mins
    elif minutes_time != 0 and seconds_time != 0:
        return str(minutes_time) + mins + " " + str(seconds_time) + secs
    else:
        return ""


def parse_multiple_alerts(alerts):
    speech_output = "Yeah, there's a few. "
    for alert in alerts:
        cause = alert['attributes']['cause']
        effect = alert['attributes']['effect']
        cause_and_effect = " Alert for %s and it's gonna cause %s." % (translate[cause], translate[effect])
        speech_output += cause_and_effect
    return speech_output


def get_predicted_train_departure(station_name):
    # Do a check if the station id is not there
    station_id = train_ids[station_name.upper()][1]
    prediction_endpoint = MBTAENDPOINT.format(
        '/predictions?filter%5Bstop%5D=' + station_id + '&filter%5Bdirection_id%5D=0&include=stop,trip&filter[route_type]=1')
    r = requests.get(prediction_endpoint, data=KEY)
    res = json.loads(r.text)
    return res['data']

def get_alerts_present(color):
    alerts_endpoint = MBTAENDPOINT.format('alerts/?filter[route]=' + str(color).capitalize())
    r = requests.get(alerts_endpoint, data=KEY)
    res = json.loads(r.text)
    return res['data']

