from flask_ask import statement
def get_speech_text(speech_output):
    return statement('<speak>{}</speak>'.format(speech_output))


def isPlural(num):
    return num > 1