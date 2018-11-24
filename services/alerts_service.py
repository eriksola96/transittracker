import requests, json, yaml
from services.helpers import consts

alerts_translate = yaml.load(open('services/translations/alert_translations.yml'))


def get_alerts_present(color):
    alerts_endpoint = consts.MBTAENDPOINT.format('alerts/?filter[route]=' + str(color).capitalize())
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