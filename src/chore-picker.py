import configparser
from twilio.rest import Client
from jsonrpcclient import request as jsonrpcrequest
from jsonrpcclient import parse, Error, Ok 

import logging
import os
import requests

FILE_PATH            = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH          = f'{FILE_PATH}/config/config.ini'
RANDOMORG_ENDPOINT   = 'https://api.random.org/json-rpc/4/invoke'


TWILIO_SID: str           = ''
TWILIO_TOKEN: str         = ''
MESSAGING_SERVICE_ID: str = ''
RANDOMORG_KEY: str        = ''
RANDOM_INT_CONFIG: dict   = {}
PHONE_NUMBERS: list       = []
CHORE_LIST: list          = []
PARTICIPANT_NUMBER: int   = 0

cfg = configparser.ConfigParser()

def config_to_list(config):
    return [str(field).strip() for field in config.split(",")]

def init_keys() -> None:
    global TWILIO_SID
    global TWILIO_TOKEN
    global MESSAGING_SERVICE_ID
    global RANDOMORG_KEY

    TWILIO_SID           = cfg['TWILIO']['account_sid']
    TWILIO_TOKEN         = cfg['TWILIO']['auth_token']
    MESSAGING_SERVICE_ID = cfg['TWILIO']['messaging_service_id']
    RANDOMORG_KEY        = cfg['RANDOM.ORG']['randomorg_api_key']

    return

def init_randomorg_params() -> None:
    global RANDOM_INT_CONFIG
    global RANDOMORG_KEY
    global PARTICIPANT_NUMBER

    # https://api.random.org/json-rpc/4/basic
    RANDOM_INT_CONFIG["apiKey"]      = RANDOMORG_KEY
    RANDOM_INT_CONFIG["length"]      = PARTICIPANT_NUMBER
    RANDOM_INT_CONFIG["n"]           = 1
    RANDOM_INT_CONFIG["replacement"] = False
    RANDOM_INT_CONFIG["base"]        = 10
    RANDOM_INT_CONFIG["min"]         = 1
    RANDOM_INT_CONFIG["max"]         = PARTICIPANT_NUMBER
    
    return


def init_participant_details() -> None:
    global PHONE_NUMBERS
    global CHORE_LIST
    global PARTICIPANT_NUMBER

    PHONE_NUMBERS        = config_to_list(cfg['PARTICIPANTS']['phone_numbers'])
    CHORE_LIST           = config_to_list(cfg['PARTICIPANTS']['chore_list'])
    PARTICIPANT_NUMBER   = len(PHONE_NUMBERS)

    if(PARTICIPANT_NUMBER < 2):
        raise Exception(
            'There is currently only one phone number in the config.   Please use more than one phone number.'
        )

    return


def fetch_random_sequence() -> any:
    rpc_request = jsonrpcrequest("generateIntegerSequences", params=RANDOM_INT_CONFIG)
    return parse(requests.post(RANDOMORG_ENDPOINT, json=rpc_request).json())


##### MAIN #####
cfg.read(CONFIG_PATH)

init_keys()
init_participant_details()
init_randomorg_params()


twilio_client: Client = Client(TWILIO_SID, TWILIO_TOKEN)
twilio_client.http_client.logger.setLevel(logging.INFO)

response = fetch_random_sequence()

if not isinstance(response, Ok):
    raise Exception("Random.org bad response", response)

body = response.result

# Result is nested in these field as an array of arrays
random_sequence: list[int] = [value - 1 for value in body['random']['data'][0]]


for i in range(PARTICIPANT_NUMBER):
    chore_index: int = random_sequence[i]
    twilio_client.messages.create(
        messaging_service_sid=MESSAGING_SERVICE_ID,
        body=f'Happy Friday!   Your task for the weekend is: {CHORE_LIST[chore_index]}',
        to=f'{PHONE_NUMBERS[i]}'
    )

