import logging

import requests
import json
from flask import Flask
from flask_ask import Ask, statement

MBTAENDPOINT = 'https://api-v3.mbta.com/{}'

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
        speech_output = "Yup, there's an alert for %s and it's gonna cause a %s." % (cause, effect)
        return statement('<speak>{}</speak>'.format(speech_output))
    else:
        speech_output = "Nope, you're in the clear"
        return statement('<speak>{}</speak>'.format(speech_output))


def alerts_present(color):
    alerts_endpoint = MBTAENDPOINT.format('alerts/?filter[route]=' + str(color).capitalize())
    r = requests.get(alerts_endpoint)
    res = json.loads(r.text)
    return res['data']

