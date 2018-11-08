import logging
from config import config

import yaml
import requests
import json
from flask import Flask, render_template
from flask_ask import Ask, statement

MBTAENDPOINT = 'https://api-v3.mbta.com/{}'
KEY = { 'api_key' : config.api_key }
human_readable=yaml.load(open('config/human_readable.yml'))

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()


@ask.launch
def launch():
    return get_alerts()

@ask.intent('GetAlertForColorIntent', convert={'color': 'color'})
def get_alerts(color):
    alerts_data = alerts_present(color)
    if len(alerts_data) > 0:
        cause = alerts_data[0]['attributes']['cause']
        effect = alerts_data[0]['attributes']['effect']
        translate_effect = human_readable[effect]
        speech_output = "Yup, there is currently an alert for %s and it's gonna cause a %s." % (cause, translate_effect)
        return statement('<speak>{}</speak>'.format(speech_output))
    else:
        speech_output = "Nope, you're in the clear"
        return statement('<speak>{}</speak>'.format(speech_output))


def alerts_present(color):
    alerts_endpoint = MBTAENDPOINT.format('alerts/?filter[route]=' + str(color).capitalize())
    r = requests.get(alerts_endpoint, data=KEY)
    res = json.loads(r.text)
    return res['data']

