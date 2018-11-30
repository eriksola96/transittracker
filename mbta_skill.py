import logging, yaml
from services.helpers import helpers as helper
from services import alerts_service as alerts_helper
from services import predictions_service as prediction_helper
from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

SESSION_STATION = "station"
alerts_translate = yaml.load(open('services/translations/alert_translations.yml'))

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()


@ask.launch
def launch():
    welcome_text = render_template('welcome')
    help_text = render_template('help')
    return question(welcome_text).reprompt(help_text)


@ask.intent('GetAlertForStationIntent', convert={'station_name': 'station_name'})
def get_alerts_for_station(station_name):
    alerts_data = alerts_helper.get_alerts_present_for_station(station_name)
    if len(alerts_data) == 1:
        cause = alerts_data[0]['attributes']['cause']
        effect = alerts_data[0]['attributes']['effect']
        speech_output = "Yup, there is currently an alert for %s and it's gonna cause %s." % \
                        (alerts_translate[cause], alerts_translate[effect])
        return statement('<speak>{}</speak>'.format(speech_output))
    elif len(alerts_data) > 1:
        speech_output = alerts_helper.parse_multiple_alerts(alerts_data)
        return statement('<speak>{}</speak>'.format(speech_output))
    else:
        speech_output = "no alerts, you're in the clear"
        return statement('<speak>{}</speak>'.format(speech_output))


@ask.intent('AlertForTripIntent', convert={'from_station': 'from_station', 'to_station': 'to_station'})
def get_alerts_for_trip(from_station, to_station):
    speech_output = alerts_helper.get_alerts_in_between_stops(from_station, to_station)
    return statement('<speak>{}</speak>'.format(speech_output))

@ask.intent('GetTrainPredictionIntent', convert={'station_name': 'station_name', 'direction': 'direction'})
def get_train_prediction(station_name, direction):
    is_valid, prediction_data = prediction_helper.get_predicted_train_departure(station_name, direction)

    # Invalid request prompt
    if not is_valid:
        invalid_request_prompt = render_template('invalid_direction', station=station_name, requested_direction=direction,
                                                    valid_directions=prediction_data)
        return statement(invalid_request_prompt)

    if len(prediction_data) == 0:
        speech_output = "Sorry, I can't seem to get any predictions for %s" % station_name
        return helper.get_speech_text(speech_output)
    elif len(prediction_data) == 1:
        time_until_departure = prediction_helper.translate_time(prediction_data[0]['attributes']['departure_time'])
        speech_output = "There's only one train predicted to head %s from %s in %s" % (direction, station_name, time_until_departure)
        return helper.get_speech_text(speech_output)
    else:
        first_time_until_departure = prediction_helper.translate_time(prediction_data[0]['attributes']['departure_time'])
        second_time_until_departure = prediction_helper.translate_time(prediction_data[1]['attributes']['departure_time'])

        first_mins_or_sec = prediction_helper.get_mins_or_sec(first_time_until_departure)
        second_mins_or_sec = prediction_helper.get_mins_or_sec(second_time_until_departure)

        first_train = "The next train predicted to head %s from %s is leaving in %s from now." % (direction, station_name, first_mins_or_sec)
        second_train = " The train after that leaves in %s" % second_mins_or_sec
        speech_output = first_train + second_train
        return helper.get_speech_text(speech_output)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    return question(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.session_ended
def session_ended():
    return "{}", 200








