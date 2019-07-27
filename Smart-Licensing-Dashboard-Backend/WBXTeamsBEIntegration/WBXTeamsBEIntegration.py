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

import datetime as dt
import json
import hashlib
import hmac
import os
from requests import Request, Session
from dateutil import parser


__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


def get_hash(key, msg):
    print('WBXTeamsBEIntegration, get_hash start')

    the_hash = hmac.new(key, msg.encode('utf-8'), hashlib.sha512)
  # print('WBXTeamsBEIntegration, get_hash.  Hash hex digest:  {}'.format(the_hash.hexdigest()))
    print('WBXTeamsBEIntegration, get_hash end')
    return the_hash

def sign(key, msg):
    print('WBXTeamsBEIntegration, sign start')
    return_hash = get_hash(key, msg).digest()
    print('WBXTeamsBEIntegration, sign end')
    return return_hash

def stringToSign(rest_method, url, secret_key, json_body, headers):
    print('WBXTeamsBEIntegration, stringToSign start')
    body = json.dumps({})
    print('  starting string_to_return')
    string_to_return = rest_method + "\n" \
                       + url + "\n" \
                       + hmac.new(secret_key.encode('utf-8'), body.encode('utf-8'),
                                  hashlib.sha512).hexdigest() + "\n" \
                       + headers['X-SLD-Date'] + "\n" \
                       + 'Content-Type'.lower() + ":" + headers['Content-Type'] + "\n" \
                       + 'X-SLD-Date'.lower() + ":" + headers['X-SLD-Date']
    print('***!!!!**     string_to_sign:  \n{}\n'.format(string_to_return))
    print('  done with string_to_return')
    print('WBXTeamsBEIntegration, stringToSign end')
    return string_to_return

def signatureKey(key, dateStamp, serviceName):
    print('WBXTeamsBEIntegration, signatureKey start')
    print('  kDate signing')
    kDate = sign(('SLD' + key).encode('utf-8'), dateStamp)
    print('  kSigning signing')
    kSigning = sign(kDate, serviceName)
    print('WBXTeamsBEIntegration, signatureKey end')
    return kSigning

def signature(key, headers, method, url, body, service_name):
    print('WBXTeamsBEIntegration, signature start')
    print('  do datesamp')
    dateStamp = parser.parse(headers['X-SLD-Date']).strftime('%Y%m%d')
    print('  datestamp:  {}'.format(dateStamp))

    print('  do signing_key ')
    signing_key = signatureKey(key, dateStamp, service_name)

    the_body = json.dumps({})

    if method != "GET":
        the_body = body

    print('  do string_to_sign ')
    string_to_sign = stringToSign(method, url, key, body, headers)

    print('  do the_signature ')
    the_signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha512).hexdigest()

    return the_signature



class WBXTeamsBEIntegration(object):
    def __init__(self, bot_secret_key, access_token, request=Request(), serviceName=""):
        self.secret_key = bot_secret_key
        self.access_token = access_token
        self.request = request
        self.service_name = serviceName

    def getSignatureKey(self, dateStamp):

       return signatureKey(self.secret_key, dateStamp, self.service_name)

    def getStringToSign(self):

       body = json.dumps({})

       if self.request.method != "GET":
           body = self.request.json

       return stringToSign(self.request.method, self.request.url, self.secret_key, body, self.request.headers)

    def getSignature(self):

       body = json.dumps({})

       if self.request.method != "GET":
           body = self.request.json

       return signature(self.secret_key, self.request.headers, self.request.method, self.request.url, body, self.service_name)

    def signatureIsValid(self, signatureKey):

        signature_is_valid = False
        sent_signature = self.request.headers[signatureKey]
        calculatedSignature = self.getSignature()

        if sent_signature ==  calculatedSignature:
            signature_is_valid = True

        return signature_is_valid


def verify_signature(key, raw_request_data, signature, request = ""):
    date_time = dt.datetime.now()
    print("{}: verify_signature: start".format(date_time))
    signature_verified = False
    # Let's create the SHA1 signature
    # based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw_request_data, hashlib.sha1)
    validated_signature = hashed.hexdigest()

    if validated_signature == signature:
        signature_verified = True
        print("{}:   verify_signature: webhook signature is valid".format(dt.datetime.now()))
    else:
        print("{}.   verify_signature: webhook signature is NOT valid".format(dt.datetime.now()))

    print("{}: verify_signature: end".format(date_time))
    return signature_verified

def read(roomId, personId):
    # do something
    print('roomId:  {}\nperonsId:  {}'.format(roomId, personId))

    raw_data = {'accessToken': '2345'}
    message = json.dumps(raw_data).encode()
    hashed = hmac.new(key, message, hashlib.sha1)
    signature = hashed.hexdigest()
    print('validated signature:  {}'.format(signature))
    return raw_data, 200, {'X-SLD-BE-Signature': signature}
