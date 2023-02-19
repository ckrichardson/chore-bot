import configparser
from twilio.rest import Client
from jsonrpcclient import request as jsonrpcrequest
from jsonrpcclient import parse, Error, Ok 
import logging
import os
import json
import requests

FILE_PATH            = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH          = f'{FILE_PATH}/config/config.ini'
RANDOMORG_ENDPOINT   = 'https://api.random.org/json-rpc/4/invoke'


TWILIO_SID           = str()
TWILIO_TOKEN         = str()
MESSAGING_SERVICE_ID = str()
RANDOMORG_KEY        = str()
RANDOM_INT_CONFIG    = str()
PHONE_NUMBERS        = list()
CHORE_LIST           = list()
PARTICIPANT_NUMBER   = int()

def config_to_list(config):
    return [str(field).strip() for field in config.split(",")]

def init_keys():
    global TWILIO_SID
    global TWILIO_TOKEN
    global MESSAGING_SERVICE_ID
    global RANDOMORG_KEY
    global RANDOM_INT_CONFIG
    global PHONE_NUMBERS
    global CHORE_LIST
    global PARTICIPANT_NUMBER

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)

    print(cfg.sections())

    TWILIO_SID           = cfg['TWILIO']['account_sid']
    TWILIO_TOKEN         = cfg['TWILIO']['auth_token']
    MESSAGING_SERVICE_ID = cfg['TWILIO']['messaging_service_id']
    RANDOMORG_KEY        = cfg['RANDOM.ORG']['randomorg_api_key']
    RANDOM_INT_CONFIG    = json.loads(cfg['RANDOM.ORG']['random_int_config'])
    PHONE_NUMBERS        = config_to_list(cfg['PARTICIPANTS']['phone_numbers'])
    CHORE_LIST           = config_to_list(cfg['PARTICIPANTS']['chore_list'])
    PARTICIPANT_NUMBER   = len(PHONE_NUMBERS)

    if(RANDOM_INT_CONFIG['n'] > 1):
        raise Exception(
            'Application cannot support multiple random integer sequences from RANDOM.ORG (n > 1).'
        )

    if(PARTICIPANT_NUMBER < 2):
        raise Exception(
            'There is currently only one phone number in the config.   Please use more than one phone number.'
        )

    RANDOM_INT_CONFIG["apiKey"] = RANDOMORG_KEY
    RANDOM_INT_CONFIG["length"] = len(PHONE_NUMBERS)
    RANDOM_INT_CONFIG["min"]    = 1
    RANDOM_INT_CONFIG["max"]    = len(PHONE_NUMBERS)

    return


def fetch_random_sequence():
    rpc_request = jsonrpcrequest("generateIntegerSequences", params=RANDOM_INT_CONFIG)
    return parse(requests.post(RANDOMORG_ENDPOINT, json=rpc_request).json())


##### MAIN #####
init_keys()

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
twilio_client.http_client.logger.setLevel(logging.INFO)

result = fetch_random_sequence()

if not isinstance(result, Ok):
    raise Exception("Random.org bad response", result)

# Result is nested in these field as an array of arrays
random_sequence = [value - 1 for value in result.result['random']['data'][0]]

print(PHONE_NUMBERS)
print(random_sequence)
print(CHORE_LIST)

for i in range(PARTICIPANT_NUMBER):
    chore_index = random_sequence[i]
    print(PHONE_NUMBERS[i], CHORE_LIST[chore_index])
#     twilio_client.messages.create(
#         messaging_service_sid=MESSAGING_SERVICE_ID,
#         body='This is a test text for chore bot',
#         to=f'{number}'
# )

