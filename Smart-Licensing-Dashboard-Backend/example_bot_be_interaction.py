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

import requests
import datetime as dt
import WBXTeamsBEIntegration
import json


__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = ["William Kurkian <wkurkian@cisco.com>"]
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

sld_bot_key = 'bot_key'
service_name = 'SLD-WebexTeams-Bot-Service'
url = "https://www.easysmartaccounts.com:10000/api/userinfo/access-token?" \
      "personId=Y2lzY29zcGFyazovL3VzL1BFT1BMRS9jZmEzOGY5Zi01MzRmLTRmMWQtYTYwMy1jYzdjNDMxYTc3NDU&" \
      "roomId=Y2lzY29zcGFyazovL3VzL1JPT00vZmYyYWUwZWQtYzcyNC0zYWJkLWJjMTgtNmNhNDhhZDljMDli"
rest_verb = 'GET'

t = dt.datetime.utcnow()
the_time = t.strftime('%Y%m%dT%H%M%SZ')
headers = {'X-SLD-Date': the_time,
           'Content-Type': 'application/json'}

# Test that the signature functionality works
the_signature = WBXTeamsBEIntegration.signature(sld_bot_key, headers, rest_verb, url, json.dumps({}), service_name)

headers['X-SLD-BOT-Signature'] = the_signature

response = requests.get(url, json=json.dumps({}), headers=headers)

print(response.headers)
print('status code:  \n{}\nresult: {}'.format(response.status_code, json.dumps(json.loads(response.text),indent=4)))

response_signature = response.headers['X-SLD-BE-Signature']

calc_signature = WBXTeamsBEIntegration.signature(sld_bot_key, response.headers, 'Response', "", response.json(), 'X-SLD-BE-Service')
print('response body: {}'.format(json.dumps(response.json(),indent=4)))
print('response_signature: {}'.format(response_signature))
print('calc_signature: {}'.format(calc_signature))

if response_signature == calc_signature:
    print('Response Signature is valid!\n\n')
else:
    print('Response Signature is not valid\n\n')


# Test that the signature functionality works.  This time, send an improperly signed request
the_signature = WBXTeamsBEIntegration.signature(sld_bot_key, headers, rest_verb, url, json.dumps({}), service_name)

headers['X-SLD-BOT-Signature'] = the_signature+"99"

incorrect_response = requests.get(url, json=json.dumps({}), headers=headers)

print(incorrect_response.headers)
print('status code:  \n{}\nresult: {}'.format(incorrect_response.status_code, json.dumps(json.loads(incorrect_response.text),indent=4)))

incorrect_response_signature = incorrect_response.headers['X-SLD-BE-Signature']

incorrect_calc_signature = WBXTeamsBEIntegration.signature(sld_bot_key, incorrect_response.headers, 'Response', "", incorrect_response.json(), 'X-SLD-BE-Service')
print('response body: {}'.format(json.dumps(incorrect_response.json(),indent=4)))
print('response_signature: {}'.format(incorrect_response_signature))
print('calc_signature: {}'.format(incorrect_calc_signature))

if incorrect_response == incorrect_calc_signature:
    print('Response Signature is valid!\n\n')
else:
    print('Response Signature is not valid\n\n')

