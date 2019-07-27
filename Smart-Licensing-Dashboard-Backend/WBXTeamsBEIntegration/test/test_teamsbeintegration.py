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


import unittest
import json
import WBXTeamsBEIntegration as wbtm_beintegration
import hmac
import hashlib
import datetime as dt
from requests import Request, Session
from dateutil import parser

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


def get_hash(key, msg):
    the_hash = hmac.new(key, msg.encode('utf-8'), hashlib.sha512)
  #  print('1. WBXTeamsBEIntegrationTest, get_hash.  Hash hex digest:  {}'.format(the_hash.hexdigest()))
    return the_hash

def sign(key, msg):
    return_hash = get_hash(key, msg).digest()
  #  print('2. WBXTeamsBEIntegrationTest, sign.  hash digest:  {}'.format(return_hash))
    return return_hash

def signatureKey(key, dateStamp, serviceName):
    kDate = sign(('SLD' + key).encode('utf-8'), dateStamp)
    kSigning = sign(kDate, serviceName)

    return kSigning



class WBXTeamsBEIntegrationTest(unittest.TestCase):
    def test_WBXTeamsBEIntegrationExists(self):
        be_integration = wbtm_beintegration.WBXTeamsBEIntegration('sample_bot_secret_key', 'sample_bot_access_token')
        self.assertIsNotNone(be_integration, 'WBXTeamsBEIntegrationTest should return an object')

    def test_returnsCorrectSignatureKey(self):
        t = dt.datetime.utcnow()
        datestamp = t.strftime('%Y%m%d')

        the_key = "alksf5akf6ka6lkfa8kdjfadv9lakv10lkad11ka12kf13akdasdkjfho38rakdsjhoqw8eyrpoahladlakjflaehflqo8ero"

        expected = signatureKey(the_key, datestamp, "testService")

        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(the_key, 'sample_bot_access_token', serviceName="testService")
        result = be_integration.getSignatureKey(datestamp)


        self.assertEqual(result, expected, 'test_returnsCorrectSignatureKey should return correct key.  Expected: {}\n'
                                           'Result:  {}'.format(expected, result))

    # def test_stringToSignReturnsAString(self):
    #     be_integration = wbtm_beintegration.WBXTeamsBEIntegration('sample_bot_secret_key', 'sample_bot_access_token')
    #
    #
    #     result = be_integration.stringToSign()
    #
    #     self.assertIsInstance(result, str, 'test_stringToSignReturnsAString'
    #                                        ' should return a string.  Expected: {}\nResult:  {}'
    #                      .format(type(""), type(result)))


    def test_stringToSignReturnsCorrectString(self):
        key = 'sample_bot_secret_key'

        url = "https://127.0.0.1/api/userinfo/access-token?personId=123&roomId=456"
        rest_verb = 'GET'
        payload = ""
        headers = {'X-SLD-Date': '20190626T161021Z',
                   'Content-Type': 'application/json'}
        req = Request(rest_verb, url, json=json.dumps({}), headers=headers)


        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(key, 'sample_bot_access_token', req, serviceName="testService")

        expected = rest_verb + "\n" \
                   + url + "\n" \
                   + hmac.new(key.encode('utf-8'), req.json.encode('utf-8'), hashlib.sha512).hexdigest() + "\n"  \
                   + headers['X-SLD-Date'] + "\n" \
                   + 'Content-Type'.lower() + ":" + req.headers['Content-Type'] + "\n" \
                   + 'X-SLD-Date'.lower() + ":" + req.headers['X-SLD-Date']

     #   print(expected)
        #
        # yeah = hmac.new(key.encode('utf-8'), expected.encode('utf-8'), hashlib.sha512)
        #
        # print('yeah digest: {}'.format(yeah.digest()))
        # print('yeah hex digest: {}'.format(yeah.hexdigest()))
        # print('yeah base without strip: {}'.format(base64.encodebytes(yeah.digest())))
        # print('yeah base with strip: {}'.format(base64.encodebytes(yeah.digest()).strip()))

        result = be_integration.getStringToSign()


        self.assertEqual(result, expected, 'test_stringToSignReturnsCorrectString should should be equal.  Expected: {}\nResult:  {}'.format(expected, result))

    def test_requestSignatureIsCorrect(self):
        key = 'sample_bot_secret_key'
        service_name = 'SLD-WebexTeams-Bot-Service'

        url = "http://127.0.0.1:5050/api/userinfo/access-token?personId=123&roomId=456"
        rest_verb = 'GET'


        headers = {'X-SLD-Date': '20190626T161021Z',
                   'Content-Type': 'application/json',
                   'X-SLD-BOT-Signature': 'ae208b91ce38148db8cda0775f027d30ac0ea6434eff0a7c07e14f7a43c7a589743ea2ef' \
                                          'a984ae0da32318f83cf3bbc3f2add37dc543d528aea06a5cc2fb7326'}

        req = Request(rest_verb, url, json=json.dumps({}), headers=headers)

        signed_string = rest_verb + "\n" \
                   + url + "\n" \
                   + hmac.new(key.encode('utf-8'), json.dumps({}).encode('utf-8'), hashlib.sha512).hexdigest() + "\n" \
                   + headers['X-SLD-Date'] + "\n" \
                   + 'Content-Type'.lower() + ":" + req.headers['Content-Type'] + "\n" \
                   + 'X-SLD-Date'.lower() + ":" + req.headers['X-SLD-Date']

        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(key, 'sample_bot_access_token', req, serviceName=service_name)

        datestamp = parser.parse('20190626T161021Z')
        signing_key = be_integration.getSignatureKey(datestamp.strftime('%Y%m%d'))
        # print('test_requestSignatureIsCorrect, signing_key: {}'.format(signing_key))
        # print('test_requestSignatureIsCorrect, signing string: \n{}\n\n'.format(signed_string))
        expected = hmac.new(signing_key, signed_string.encode('utf-8'), hashlib.sha512).hexdigest()
        # print('Expected: {}'.format(expected))

        result = be_integration.getSignature()

        self.assertEqual(result, expected,'test_requestSignatureIsCorrect should should be equal.  Expected: {}\nResult:  {}'.format(expected, result))

    def test_signatureIsValidReturnsABool(self):
        key = 'sample_bot_secret_key'
        service_name = 'SLD-WebexTeams-Bot-Service'

        url = "http://127.0.0.1:5050/api/userinfo/access-token?personId=123&roomId=456"
        rest_verb = 'GET'

        headers = {'X-SLD-Date': '20190626T161021Z',
                   'Content-Type': 'application/json',
                   'X-SLD-BOT-Signature': "ae208b91ce38148db8cda0775f027d30ac0ea6434eff0a7c07e14f7a43c7a589743ea2ef" \
                                          "a984ae0da32318f83cf3bbc3f2add37dc543d528aea06a5cc2fb7326"}

        req = Request(rest_verb, url, json=json.dumps({}), headers=headers)

        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(key, 'sample_bot_access_token', req,
                                                                  serviceName=service_name)

        result = be_integration.signatureIsValid('X-SLD-BOT-Signature')
        self.assertIsInstance(result, bool, 'test_signatureIsValidatedReturnsABool '
                                                     'should return a bool.\nExpected: {}\nResult: {}'.
                format(type(True), type(result)))

    def test_signatureIsValidReturnsTrue(self):
        key = 'sample_bot_secret_key'
        service_name = 'SLD-WebexTeams-Bot-Service'

        url = "http://127.0.0.1:5050/api/userinfo/access-token?personId=123&roomId=456"
        rest_verb = 'GET'

        headers = {'X-SLD-Date': '20190626T161021Z',
                   'Content-Type': 'application/json',
                   'X-SLD-BOT-Signature': "ae208b91ce38148db8cda0775f027d30ac0ea6434eff0a7c07e14f7a43c7a589743ea2ef" \
                                          "a984ae0da32318f83cf3bbc3f2add37dc543d528aea06a5cc2fb7326"}

        req = Request(rest_verb, url, json=json.dumps({}), headers=headers)

        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(key, 'sample_bot_access_token', req,
                                                                  serviceName=service_name)

        result = be_integration.signatureIsValid('X-SLD-BOT-Signature')

        self.assertTrue(result,'test_signatureIsValidReturnsTrue should be true.  Expected: {}\nResult:  {}'.format(True, result))

    def test_signatureIsValidReturnsFalse(self):
        key = 'sample_bot_secret_key_2'
        service_name = 'SLD-WebexTeams-Bot-Service'

        url = "http://127.0.0.1:5050/api/userinfo/access-token?personId=123&roomId=456"
        rest_verb = 'GET'

        headers = {'X-SLD-Date': '20190626T161021Z',
                   'Content-Type': 'application/json',
                   'X-SLD-BOT-Signature': "ae208b91ce38148db8cda0775f027d30ac0ea6434eff0a7c07e14f7a43c7a589743ea2ef" \
                                          "a984ae0da32318f83cf3bbc3f2add37dc543d528aea06a5cc2fb7326"}

        req = Request(rest_verb, url, json=json.dumps({}), headers=headers)

        be_integration = wbtm_beintegration.WBXTeamsBEIntegration(key, 'sample_bot_access_token', req,
                                                                  serviceName=service_name)

        result =  be_integration.signatureIsValid('X-SLD-BOT-Signature')

        self.assertEqual(result, False,
                        'test_signatureIsValidReturnsFalse should be false.  Expected: {}\nResult:  {}'.format(
                            False, result))


if __name__ == '__main__':
    unittest.main()
