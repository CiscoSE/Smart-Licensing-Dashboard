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
from WebexTeams import CSSMLicense
import xlsxwriter
from datetime import datetime, timezone
from datetime import timedelta
import copy

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

file_name = "./license_by_sa-va_full.json"

class SLDPullBotFunctionTest(unittest.TestCase):

    def test_create_account_names_message_returns_correct_message(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        expected_names = ['BU Production Test', 'Cisco Demo Customer Smart Account', 'Federal Team Testing Cisco Account',
         'Cisco Sales Enablement']
        expected = '**Here are the requested accounts:**\n\n'
        for name in expected_names:
            expected = expected + '* {}\n'.format(name)
        print('expected: {}'.format(expected))
        result = sld.create_account_names_message(cssm_license)

        self.assertEqual(expected, result, 'test_create_account_names_message_returns_correct_message:\nExpected: {}\n'
                                           'Result: {}'.format(expected, result))

    # def test_create_account_names_message_returns_correct_message_with_empty_json(self):
    #     result = sld.create_account_names_message(None)
    #
    #     expected = 'Sorry, there aren\'t any accounts for your credentials!'
    #
    #     self.assertEqual(expected, result, 'test_create_account_names_message_returns_correct_message_with_empty_json:\nExpected: {}\n'
    #                                        'Result: {}'.format(expected, result))


    def test_create_virtual_account_message_contains_string(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_virtual_accounts_message(cssm_license)
        self.assertIsInstance(result, str,
                              'test_create_virtual_account_message_contains_message.\nExpected: {}\nResult: {}\n'.
                              format(type(result),type("")))

    def test_create_virtual_account_message_contains_correct_message(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        expected = '**Here are the *virtual accounts*, grouped by Account**:\n' \
                   '* **BU Production Test**\n' \
                   '    * ATT CUSTOMER 2\n' \
                   '    * ATT ENCS\n' \
                   '    * ATT Account Team\n' \
                   '    * ATT CUSTOMER 1\n' \
                   '* **Cisco Demo Customer Smart Account**\n' \
                   '    * AF-Region\n' \
                   '* **Federal Team Testing Cisco Account**\n' \
                   '    * DoD-AF\n' \
                   '* **Cisco Sales Enablement**\n' \
                   '    * DEFAULT\n' \
                   '    * Alex Daltrini (adaltrin)\n'

        result = sld.create_virtual_accounts_message(cssm_license)
        self.assertEqual(result, expected,
                              'test_create_virtual_account_message_contains_correct_message.\nExpected: {}\nResult:{}'
                         .format(expected,result))

    def test_create_expired_licenses_message(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_expired_licenses_message(cssm_license)
        self.assertIsInstance(result, str,
                              'test_create_virtual_account_message_contains_message.\nExpected: {}\nResult: {}\n'.
                              format(type(result),type("")))

    def test_create_expired_licenses_message_correct(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_expired_licenses_message(cssm_license)

        expected = '**Here are the *expired licenses*, grouped by Account and Virtual Account**:\n' \
                   '* **BU Production Test**\n    * ATT ENCS\n        * CSR 1KV APPX 2500M\n'

        self.assertEqual(expected, result,
                         'test_create_expired_licenses_message_correct.\nExpected: {}\nResult:{}'
                         .format(expected, result))


    def test_create_license_status_message_creates_correct_expired_status(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)
        expected = '    * **Cisco Sales Enablement**\n' \
                   '        * DEFAULT\n' \
                   '            * ISRV AX 250M, Qty: 4990, Expired: 2018/11/19\n' \
                   '    * **BU Production Test**\n' \
                   '        * ATT CUSTOMER 1\n' \
                   '            * ISRV AX 2500M, Qty: 5, Expired: 2019/04/02\n' \
                   '            * ISRV IPB 2500M, Qty: 5, Expired: 2019/04/02\n' \
                   '        * ATT ENCS\n' \
                   '            * CSR 1KV AX 5G, Qty: 6, Expired: 2019/05/23\n' \
                   '        * ATT Account Team\n' \
                   '            * CSR 1KV AX 5G, Qty: 4, Expired: 2019/05/23\n'

        self.assertTrue(expected in result, 'test_create_license_status_message_creates_correct_expired_status.\nExpected: {}\nResult:{}'
                         .format(expected, result))

    def test_create_license_status_message_creates_correct_future_expired_status(self):
        with open('./multiple_future_expiration.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)
        # expected = "noway"
        expected = '* [Top 5 Licenses Expiring in the Next 180 Days](None "Future Expired License Link")\n' \
                   '    * **BU Production Test**\n' \
                   '        * ATT ENCS\n' \
                   '            * **CSR 1KV APPX 2500M**, Qty: 50 expire on: 2019/08/04\n' \
                   '        * Some Virtual Account 1\n' \
                   '            * **CSR 1KV APPX 10M**, Qty: 50 expire on: 2019/09/04\n' \
                   '            * **Some License**, Qty: 50 expire on: 2019/09/15\n' \
                   '    * **Some Goofy Production Test**\n' \
                   '        * Dowee Cheatum and Howe\n' \
                   '            * **Some License IV**, Qty: 50 expire on: 2019/11/04\n' \
                   '        * Fly By Night\n' \
                   '            * **Some License III**, Qty: 50 expire on: 2019/11/30'

        self.assertTrue(expected in result, 'test_create_license_status_message_creates_correct_expired_status.\nExpected: {}\nResult:{}'
                         .format(expected, result))

    def test_create_license_status_message_creates_correct_top_shortage(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)
        # expected = "noway"
        expected = '* [Top 5 License Shortages](None "License Shortage Link")\n' \
                   '    * **Cisco Sales Enablement**\n' \
                   '        * Alex Daltrini (adaltrin)\n' \
                   '            * ASAv10 Standard - 1G, has a shortage of 14 licenses\n' \
                   '        * DEFAULT\n' \
                   '            * CSR 1KV AX 250M, has a shortage of 13 licenses\n' \
                   '            * C3650_24_Ipserv, has a shortage of 12 licenses\n' \
                   '    * **Federal Team Testing Cisco Account**\n' \
                   '        * DoD-AF\n' \
                   '            * Prime Infrastructure 3.x, Lifecycle Lic., has a shortage of 11 licenses\n' \
                   '            * Prime Infrastructure 3.x, BASE Lic., has a shortage of 10 licenses'

        self.assertTrue(expected in result, 'test_create_license_status_message_creates_correct_top_shortage.\nExpected: {}\nResult:{}'
                         .format(expected, result))

    def test_create_license_status_message_creates_correct_top_usage(self):

        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)

        expected = '* [Top 5 Licenses By Consumption](None "License Consumption Link")\n' \
                   '    * **BU Production Test**\n' \
                   '        * Some Virtual Account 1\n' \
                   '            * Some License, has 64.0% utilization\n' \
                   '            * CSR 1KV APPX 10M, has 24.0% utilization\n' \
                   '    * **Some Goofy Production Test**\n' \
                   '        * Fly By Night\n' \
                   '            * Some License III, has 56.0% utilization\n' \
                   '            * Some License II, has 34.0% utilization\n' \
                   '        * Dowee Cheatum and Howe\n' \
                   '            * Some License IV, has 44.0% utilization\n'

        self.assertTrue(expected in result,
                       'test_create_license_status_message_creates_correct_top_usage.\nExpected: {}\nResult:{}'
                       .format(expected, result))

    def test_create_license_status_message_creates_correct_top_usage_when_no_usage(self):
        with open('./my_licensing_info.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)

        expected = '* [License Usage: There are no licenses in use right now](None "License Consumption Link")'

        self.assertTrue(expected in result,
                       'test_create_license_status_message_creates_correct_top_usage_when_no_usage.\nExpected: {}\nResult:{}'
                       .format(expected, result))

    def test_create_license_status_message_has_correct_initial_text(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        expected = "**Here is the high level status of your licensing**:\n"

        result = sld.create_license_status_message(cssm_license)

        self.assertTrue(expected in result, 'test_create_license_status_message_has_correct_initial_text.\nExpected:\n {}Result:\n{}'
                         .format(expected, result))


    def test_create_license_status_message_creates_correct_top_technology(self):

        with open('./alex_json_v1.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)

        expected = '* [Here is your architecture mix, by Account](None "License Architecture Mix Link")\n' \
                   '    * **PnP Test Account - KB**\n' \
                   '        * Security: 52.9%\n' \
                   '        * Enterprise Networking: 47.1%\n'

        self.assertTrue(expected in result,
                       'test_create_license_status_message_creates_correct_top_technology.\nExpected: {}\nResult:{}'
                       .format(expected, result))

    def test_create_license_status_message_creates_correct_top_technology_empty(self):

        with open('./my_licensing_info.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_status_message(cssm_license)

        expected = '[License Shortage: There are no license shortages](None "License Shortage Link")'

        self.assertTrue(expected in result,
                       'test_create_license_status_message_creates_correct_top_technology.\nExpected: {}\nResult:{}'
                       .format(expected, result))

    def test_create_expired_licenses_message_correct(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_expired_licenses_message(cssm_license)

        expected = '**Here are the *expired licenses*, grouped by Account and Virtual Account**:\n' \
                   '* **Cisco Sales Enablement**\n' \
                   '    * DEFAULT\n' \
                   '        * ISRV AX 250M, Qty: 4990, expires: 2018/11/19\n' \
                   '    * Alex Daltrini (adaltrin)\n' \
                   '        * ISRV AX 500M, Qty: 10, expires: 2019/05/31\n' \
                   '* **BU Production Test**\n' \
                   '    * ATT CUSTOMER 1\n' \
                   '        * ISRV AX 2500M, Qty: 5, expires: 2019/04/02\n' \
                   '        * ISRV IPB 2500M, Qty: 5, expires: 2019/04/02\n' \
                   '        * ISRV APPX 10M, Qty: 1, expires: 2019/05/31\n' \
                   '    * ATT ENCS\n' \
                   '        * CSR 1KV AX 5G, Qty: 6, expires: 2019/05/23\n' \
                   '    * ATT Account Team\n' \
                   '        * CSR 1KV AX 5G, Qty: 4, expires: 2019/05/23\n' \
                   '        * CSR 1KV IP BASE 10G, Qty: 4, expires: 2019/05/23\n' \
                   '        * CSR 1KV APPX 500M, Qty: 1, expires: 2019/05/31\n'

        self.assertEqual(result, expected,
                         'test_create_expired_licenses_message_correct.\nExpected: {}\nResult:{}'
                         .format(expected, result))


    def test_create_license_usage_message(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result, success = sld.create_license_usage_message(cssm_license)
        print(result)

        expected = '**Here is the license usage by account and virtual account**: \n' \
                   '* **BU Production Test**\n' \
                   '    * ATT ENCS\n' \
                   '        * CSR 1KV APPX 2500M, has 14.0% utilization\n' \
                   '    * Some Virtual Account 1\n' \
                   '        * CSR 1KV APPX 10M, has 24.0% utilization\n' \
                   '        * Some License, has 64.0% utilization\n' \
                   '* **Some Goofy Production Test**\n' \
                   '    * Dowee Cheatum and Howe\n' \
                   '        * Some License IV, has 44.0% utilization\n' \
                   '    * Fly By Night\n' \
                   '        * Some License II, has 34.0% utilization\n' \
                   '        * Some License III, has 56.0% utilization\n'

        self.assertEqual(expected, result,
                         'test_create_license_usage_message.\nExpected: {}\nResult:{}'
                         .format(expected, result))

    def test_create_license_technology_message(self):
        with open('./license_by_sa-va_full.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_architecture_mix_message(cssm_license)
        print(result)

        expected = '**Here is the architecture mix, by account**: \n' \
                   '* **Cisco Demo Customer Smart Account**\n' \
                   '    * Security: 100.0%\n' \
                   '* **Cisco Sales Enablement**\n' \
                   '    * Enterprise Networking: 99.5%\n' \
                   '    * Security: 0.5%\n' \
                   '* **BU Production Test**\n' \
                   '    * Enterprise Networking: 72.8%\n' \
                   '    * Security: 27.2%\n' \
                   '* **Federal Team Testing Cisco Account**\n' \
                   '    * Enterprise Networking: 65.6%\n' \
                   '    * Data Center: 28.1%\n' \
                   '    * Security: 6.2%\n'

        self.assertEqual(expected, result,
                         'test_create_license_technology_message.\nExpected: {}\nResult:{}'
                         .format(expected, result))

    def test_create_license_usage_message_large(self):
        with open('./usage_test_large.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result, success = sld.create_license_usage_message(cssm_license)

        expected = '**There are a large number of licenses.  Here is the license usage for the top 10 by account and virtual account**:\n' \
                   '* **BU Production Test**\n' \
                   '    * ATT ENCS\n' \
                   '        * CSR 1KV APPX 2500M, has 14.0% utilization\n' \
                   '    * Some Virtual Account 1\n' \
                   '        * CSR 1KV APPX 10M, has 24.0% utilization\n' \
                   '        * Some License, has 64.0% utilization\n' \
                   '* **Some Goofy Production Test**\n' \
                   '    * Dowee Cheatum and Howe\n' \
                   '        * Some License IV, has 44.0% utilization\n' \
                   '        * Some License V, has 10.0% utilization\n' \
                   '        * Some License VI, has 8.0% utilization\n' \
                   '        * Some License VII, has 6.0% utilization\n' \
                   '        * Some License VIII, has 4.0% utilization\n' \
                   '    * Fly By Night\n' \
                   '        * Some License II, has 34.0% utilization\n' \
                   '        * Some License III, has 56.0% utilization\n\n' \
                   'Will export all the licenses usage info to an excel file.\n'

        self.assertEqual(expected, result,
                         'test_create_license_usage_message_large.\nExpected: {}\nResult:{}'
                         .format(expected, result))



    def test_create_shortage_license_message(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()
        result = sld.create_license_shortages_message(cssm_license)
        self.assertIsInstance(result, str,
                              'test_create_shortage_license_message.\nExpected: {}\nResult: {}\n'.
                              format(type(result),type("")))

    def test_create_license_shortage_message_correct(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_license_shortages_message(cssm_license)

        expected = '    * ATT ENCS\n' \
                   '        * There is a shortage of **3** licenses for "**CSR 1KV AX 5G**"\n' \
                   '        * There is a shortage of **2** licenses for "**CSR 1KV APPX 2500M**"\n'

        self.assertTrue(expected in result,
                         'test_create_expired_licenses_message_correct.\nExpected: \n{}\nResult:\n{}'
                         .format(expected, result))

        expected = '* **Federal Team Testing Cisco Account**\n' \
                   '    * DoD-AF\n' \
                   '        * There is a shortage of **11** licenses for "**Prime Infrastructure 3.x, Lifecycle Lic.**"\n' \
                   '        * There is a shortage of **10** licenses for "**Prime Infrastructure 3.x, BASE Lic.**"\n' \
                   '        * There is a shortage of **9** licenses for "**Cisco Intersight SaaS - Essentials**"\n'

        self.assertTrue(expected in result,
                        'test_create_expired_licenses_message_correct.\nExpected: \n{}\nResult:\n{}'
                        .format(expected, result))

    def test_create_thirty_day_expired_licenses_message(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        result = sld.create_expired_licenses_message(cssm_license)
        self.assertIsInstance(result, str,
                              'test_create_virtual_account_message_contains_message.\nExpected: {}\nResult: {}\n'.
                              format(type(result),type("")))

    def test_create_correct_future_thirty_day_expired_licenses_message_single(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        cssm_license = parser.cssm_license()

        expected = '**Here are the licenses that will expire in 30 days:**:\n' \
                   '* **Cisco Sales Enablement**\n' \
                   '    * DEFAULT\n' \
                   '        * **ISR_4331_UnifiedCommunication**, Qty: 90 expire on: 2019/07/19\n'

        result = sld.create_future_expired_licenses_message(cssm_license)
        self.assertEqual(expected, result,
                              'test_create_correct_future_thirty_day_expired_licenses_message.\nExpected: {}\nResult: {}\n'.
                              format(expected,result))





if __name__ == '__main__':
    unittest.main()
