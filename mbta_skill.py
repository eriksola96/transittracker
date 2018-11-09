import logging
from config import config

import yaml
import requests
import json
from flask import Flask, render_template
from flask_ask import Ask, statement

MBTAENDPOINT = 'https://api-v3.mbta.com/{}'
KEY = { 'api_key': config.api_key }
translate = yaml.load(open('config/translations.yml'))

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()


@ask.launch
def launch():
    return get_alerts()

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


def parse_multiple_alerts(alerts):
    speech_output = "Yeah, there's a few. "
    for alert in alerts:
        cause = alert['attributes']['cause']
        effect = alert['attributes']['effect']
        cause_and_effect = " Alert for %s and it's gonna cause %s." % (translate[cause], translate[effect])
        speech_output += cause_and_effect
    return speech_output


def get_alerts_present(color):
    alerts_endpoint = MBTAENDPOINT.format('alerts/?filter[route]=' + str(color).capitalize())
    r = requests.get(alerts_endpoint, data=KEY)
    res = json.loads(r.text)
    return res['data']

