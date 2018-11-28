import requests, json, yaml
from services.helpers import consts

alerts_translate = yaml.load(open('services/translations/alert_translations.yml'))
train_info = yaml.load(open('services/translations/t_station_ids.yml'))


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