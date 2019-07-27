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
from WebexTeams import sld_pullbot_function as sld
from WebexTeams import CSSMJSONParser as cssm_parser
import xlsxwriter

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

import unittest


class SLDPullBotHelpTest(unittest.TestCase):
    def test_hello_msg_contains_intro(self):
        expected = '**Howdy, this is the Cisco Smart Licensing Dashboard Bot.  What can I do for you?**\n\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_intro should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_account_help(self):
        expected = '    * \'give me a list of virtual accounts\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_account_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_virtual_account_help(self):
        expected = '    * \'give me a list of account names\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_virtual_account_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_export_licenses_help(self):
        expected = '    * \'give me an export of licenses\' or \'export licenses\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_export_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_expired_license_header_help(self):
        expected = '    * **Expired Licenses Info**\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_usage_help(self):
        expected = '    * \'show me license usage\' or \'license usage\' or \'usage\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_thirty_day_expired_licenses_help(self):
        expected = '        * \'show me licenses that expire in 30 days\' or \'expire 30 days\' or \'expire 30\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_thirty_day_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_sixty_day_expired_licenses_help(self):
        expected = '        * \'show me licenses that expire in 60 days\' or \'expire 60 days\' or \'expire 60\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_sixty_day_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_ninety_day_expired_licenses_help(self):
        expected = '        * \'show me licenses that expire in 90 days\' or \'expire 90 days\' or \'expire 90\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_ninety_day_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))



    def test_hello_msg_contains_expired_licenses_help(self):
        expected = '        * \'give me a list of expired licenses\' or \'expired licenses\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_license_shortage_help(self):
        expected = '    * \'show me licenses with shortages\' or \'license shortage list\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_license_shortage_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_status_help(self):
        expected = '* \'show me the latest status\' or \'status\' or \'give me a status update\'\n'

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_status_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

    def test_hello_msg_contains_technology_help(self):
        expected = '    * \'show me the architecture mix\' or \'architecture mix\''

        result = sld.prepare_hello_message()

        self.assertTrue(expected in result, 'test_hello_msg_contains_expired_licenses_help should be equal:\nExpected: '
                                            '{}\nResult:{}'.format(expected, result))

if __name__ == '__main__':
    unittest.main()
