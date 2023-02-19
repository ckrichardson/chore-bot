import configparser
from twilio.rest import Client
import logging

CONFIG_PATH =   './config/config.ini'
TWILIO_SID =    str()
TWILIO_TOKEN =  str()
RANDOMORG_KEY = str()
PHONE_NUMBERS = any

def init_keys():
    global TWILIO_SID
    global TWILIO_TOKEN
    global RANDOMORG_KEY
    global PHONE_NUMBERS

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)

    TWILIO_SID =    cfg['TWILIO']['account_sid']
    TWILIO_TOKEN =  cfg['TWILIO']['auth_token']
    RANDOMORG_KEY = cfg['RANDOM.ORG']['randomorg_api_key']
    PHONE_NUMBERS = \
        [str(number) for number in cfg['PARTICIPANTS']['phone_numbers'].split(",")]

def fetch_random_sequence():
    return


##### MAIN #####
init_keys()

print(TWILIO_SID, TWILIO_TOKEN, RANDOMORG_KEY)

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
twilio_client.http_client.logger.setLevel(logging.INFO)

for number in PHONE_NUMBERS:
    twilio_client.messages.create(
        messaging_service_sid='MG31948ddea8e76f2dc3155430cef3d722',
        body='This is a test text for chore bot',
        to=f'{number}'
    )



