"""

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""
from __future__ import absolute_import, division, print_function
from flask import Flask , request
import requests
import json
import os
import datetime as dt
import sparkhelper
import sld_pullbot_function as sld
import threading
from loguru import logger
import functools

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

app = Flask(__name__)
key = str.encode(os.environ.get('SMART_LICENSING_WEBHOOK_SECRET'))
bot_token = os.environ.get('SMART_LICENSING_ACCESS_TOKEN')
be_secret_key = os.environ.get('SMART_LICENSING_BE_SECRET_KEY')

allowed_emails = ['timtayl@cisco.com', 'adaltrin@cisco.com', 'jdurkin@cisco.com', 'rosadams@cisco.com', 'wkurkian@cisco.com']


allowed_person_Org_Id = ['Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi8xZWI2NWZkZi05NjQzLTQxN2YtOTk3NC1hZDcyY2FlMGUxMGY']

logger.add("loguru_output", colorize=True, rotation="00:01")

# function that helps with decorator for logging in/out of functions/methods
def logger_wraps(*, entry=True, exit=True, level="DEBUG"):

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}'", name)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}'", name)
            return result

        return wrapped

    return wrapper

@logger_wraps()
def process_initial_request(message_id):
    logger.info('process_initial_request start')

    # First we need to get the actual message to see what the client is asking for.
    logger.info(' preparing request for the message')

    the_url = "https://api.ciscospark.com/v1/messages/{0}".format(message_id)
    date_time=dt.datetime.now()
    logger.info(' sending the request for the message')
    message_response = requests.get(the_url,verify=True,headers={'Authorization': 'Bearer {}'.format(bot_token)})
    logger.info(' received the response for the message request')
    raw = message_response.text

    # Check to see if the response was successful
    if message_response.status_code == 200:
        logger.info('   request was successful, status code=200')
        # Response was successful.  Figure out the context.
        message_json = json.loads(message_response.text)

        message_text = message_json["text"]

        #normalize the text
        message_text = message_text.translate({ord(c): None for c in '!"#$%&\()*+,-.:;<=>?@[\\]^_`{|}~'})

        logger.info('   retrieving the roomId and personId from the response')
        room_id = message_json["roomId"]
        person_id = message_json["personId"]

        # figure out what they want.
        if ("hello" in repr(message_text.lower())) or ("help" in repr(message_text.lower())):
            logger.info('entering send_hello_back')
            sld.send_hello_back(room_id, bot_token)
        else:

            # Retrieve the access token from the back end.
            logger.info('   retrieving the access token')
            retrieve_token_successful, status_code, cssm_token = sld.retrieve_be_token(be_secret_key, room_id, person_id)
            logger.info('   retrieved the token')

            # if there is a problem with retrieving the access token, notify the user.
            if retrieve_token_successful == False:
                logger.info('   token retrieval not successful')
                logger.info('     status code: {}'.format(status_code))
                sld.send_authentication_back(room_id, bot_token)
                if (status_code == 401) or (status_code == 404):
                    logger.info('   request was not authorized')

            else:
                # Figure out what the client wants and take action.
                logger.info('   token retrieval successful')
                if ("hello" in repr(message_text.lower())) or ("help" in repr(message_text.lower())):
                    logger.info('entering send_hello_back')
                    sld.send_hello_back(room_id, bot_token)
                if (("list of account names" in repr(message_text.lower()) or
                      ("list of accounts" in repr(message_text.lower()))) or
                    ("account names" in repr(message_text.lower()))):
                    logger.info('entering send_accout_names')
                    sld.send_account_names(room_id, bot_token, cssm_token)

                elif (("list of virtual account names" in repr(message_text.lower()) or
                       ("list of virtual accounts" in repr(message_text.lower()))) or
                      ("virtual accounts" in repr(message_text.lower()))):
                    logger.info('send_virtual_accounts')
                    sld.send_virtual_accounts(room_id, bot_token, cssm_token)

                elif ("export of licenses" in repr(message_text.lower())) or ("export license" in repr(message_text.lower())):
                    logger.info('send_license_export')
                    sld.send_license_export(room_id, bot_token, cssm_token)

                elif ("expired licenses" in repr(message_text.lower())):
                    logger.info('send_expired_licenses')
                    sld.send_expired_licenses(room_id, bot_token, cssm_token)

                elif ("show me licenses with shortages" in repr(message_text.lower())) or \
                        ("license shortage list" in repr(message_text.lower())) or \
                        ("shortages" in repr(message_text.lower())) or \
                        ("license shortage" in repr(message_text.lower())):
                    logger.info('send_license_shortage')
                    sld.send_license_shortage(room_id, bot_token, cssm_token)

                elif ("show me licenses that expire in 30 days" in repr(message_text.lower())) or \
                        ("expire 30" in repr(message_text.lower())) or \
                        ("expire 30 days" in repr(message_text.lower())):
                    logger.info('expire in 30 days')
                    sld.send_future_expired_licenses(room_id, bot_token, cssm_token, expiration_days=30)

                elif ("show me licenses that expire in 60 days" in repr(message_text.lower())) or \
                        ("expire 60" in repr(message_text.lower())) or \
                        ("expire 60 days" in repr(message_text.lower())):
                    logger.info('expire in 60 days')
                    sld.send_future_expired_licenses(room_id, bot_token, cssm_token, expiration_days=60)

                elif ("show me licenses that expire in 90 days" in repr(message_text.lower())) or \
                        ("expire 90" in repr(message_text.lower())) or \
                        ("expire 90 days" in repr(message_text.lower())):
                    logger.info('expire in 90 days')
                    sld.send_future_expired_licenses(room_id, bot_token, cssm_token, expiration_days=90)

                elif ("show me licenses that expire in 180 days" in repr(message_text.lower())) or \
                        ("expire 180" in repr(message_text.lower())) or \
                        ("expire 180 days" in repr(message_text.lower())):
                    logger.info('expire in 180 days')
                    sld.send_future_expired_licenses(room_id, bot_token, cssm_token, expiration_days=180)

                elif ("show me the latest status" in repr(message_text.lower())) or \
                        ("status" in repr(message_text.lower())) or \
                        ("give me a status update" in repr(message_text.lower())):
                    logger.info('status')
                    sld.send_license_status_update(room_id, bot_token, cssm_token)

                elif ('show me license usage'  in repr(message_text.lower())) or \
                        ("license usage" in repr(message_text.lower())) or \
                        ("usage" in repr(message_text.lower())):
                    logger.info('get usage status')
                    sld.send_license_usage(room_id, bot_token, cssm_token)

                elif ('show me the architecture mix'  in repr(message_text.lower())) or \
                        ("architecture mix" in repr(message_text.lower())) or \
                        ("architecture" in repr(message_text.lower())):
                    logger.info('architecture mix')
                    sld.send_license_architecture_mix(room_id, bot_token, cssm_token)

                else:
                    logger.info('entering send_problem abck')
                    sld.send_problem_back(room_id, bot_token)

    else:

        logger.info("message response was something other than 200")


@app.route('/smartdashpullbot',methods =['POST'])
@logger_wraps()
def smartdash_pullbot():
    request_json = request.json
    date_time = dt.datetime.now()

    # Don't respond to self.
    person_email = request_json['data']['personEmail']
    if person_email == "SLDBot@webex.bot":
        logger.info("{}: returning Message was from the SmartLicensingBot".format(date_time))
        return 'Ok'

    # make sure we don't respond to rooms that have users from unknown Teams organizations
    if not sparkhelper.membership_check(request_json['data']['roomId'], bot_token, allowed_person_Org_Id):
        return 'Ok'

    # for right now, to be safe, do not respond to folks from other companies.  Can be removed
    if "cisco.com" not in person_email:
        logger.info("{}: person email: {}, not responded to.".format(date_time,person_email))
        return 'Ok'

    # For right now, limit responses only to the ASIC Team. Can be removed
    if person_email not in allowed_emails:
        logger.info("{}: person email: {}, not responded to.".format(date_time, person_email))
        return 'Ok'

    # Verify the Request is from Webex Teams.
    raw = request.data
    signature_verified = sparkhelper.verify_signature(key, raw, request.headers)

    # If the signature is verified, start the process of responding.
    if signature_verified:
        message_id = request_json['data']['id']
        logger.info(' person email: {}'.format(person_email))

        # Pulling and processing the info can be time intensive.  Spawn the request off to a different thread so we can
        # respond back as quickly to the Webex Teams Service as quickly as possible.  Otherwise, if there are too many
        # requests without a response, they will disable the webhook
        x = threading.Thread(target=process_initial_request, args=(message_id,))
        x.start()

    return "Ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
