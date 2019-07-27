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
from WebexTeams import CSSMJSONParser as cssm_parser
from WebexTeams import CSSMLicense as cssm_license
import pandas as pd
import datetime as dt
from datetime import timezone
from datetime import timedelta

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

file_name = "./license_by_sa-va_full.json"

class CSSMLicensingTests(unittest.TestCase):


    def test_returns_an_array_for_account_names(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license()

        self.assertIsNotNone(result.account_names(), 'test_returns_an_object_for_account_names should return a value')

    def test_returns_an_array_with_correct_account_names(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)


        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license()

        #expected = ['BU Production Test', 'Cisco Demo Customer Smart Account', 'Federal Team Testing Cisco Account', 'Cisco Sales Enablement']
        expected_array = ['Cisco Demo Customer Smart Account', 'BU Production Test', 'Federal Team Testing Cisco Account',
                    'Cisco Sales Enablement']
        result_array = result.account_names()

        outer_compare_result = True

        for expected in expected_array:
            inner_compare_result = False
            for result in result_array:
                if result == expected:
                    inner_compare_result = True
                    break

            if inner_compare_result==False:
                outer_compare_result = False
                break


        self.assertTrue(outer_compare_result, "test_returns_an_array_with_correct_account_names should be equal.  "
                                           "\nExpected: {}\nResult: {}\n".format(expected_array, result_array))

    def test_cssm_dataframe_has_correct_accounts(self):

        with open(file_name) as json_data:
            json_array = json.load(json_data)

        expected_array = ['Cisco Demo Customer Smart Account', 'BU Production Test',
                          'Federal Team Testing Cisco Account',
                          'Cisco Sales Enablement']

        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license()

        df = parser.cssm_dataframe()

        result_array = df['accountName'].unique()

        expected_array = ['Cisco Demo Customer Smart Account', 'BU Production Test',
                          'Federal Team Testing Cisco Account',
                          'Cisco Sales Enablement']

        outer_compare_result = True

        for expected in expected_array:
            inner_compare_result = False
            for result in result_array:
                if result == expected:
                    inner_compare_result = True
                    break

            if inner_compare_result == False:
                outer_compare_result = False
                break

        self.assertTrue(outer_compare_result, "test_cssm_dataframe_has_correct_accounts should return expcted accounts"
                                              "\nExpected: {}\nResult: {}\n".format(expected_array, result_array))

    def test_cssm_virt_accounts_grouped_by_names_returns_dict(self):

        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_virt_account_by_accountName()

        self.assertIsInstance(result, dict,
                              'test_cssm_virt_accounts_grouped_by_names_returns_dict. Expected: {}\nResult: {}'
                              .format(type(dict), type(result)))


    def test_cssm_virt_accounts_grouped_by_names_returns_correct_virtual_accounts(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_virt_account_by_accountName()

        expected = {'BU Production Test': ['ATT CUSTOMER 2', 'ATT ENCS', 'ATT Account Team', 'ATT CUSTOMER 1'],
                    'Cisco Demo Customer Smart Account': ['AF-Region'],
                    'Cisco Sales Enablement': ['DEFAULT', 'Alex Daltrini (adaltrin)'],
                    'Federal Team Testing Cisco Account': ['DoD-AF']}

        self.assertEqual(expected, result, 'test_cssm_virt_accounts_grouped_by_names_returns_correct_virtual_accounts. '
                                           'Expected: {}\nResult: {}'.format(type(dict), type(result)))

    def test_multiple_assigned_license_parsed_correctly(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        df = parser.cssm_license().cssm_dataframe

        expected = [dt.date(2019, 10, 4), dt.date(2019, 11, 28)]
        result = list(df['endDate'])

        self.assertEqual(expected[0],result[0].date(), 'test_multiple_assigned_license_parsed_correctly. \n'
                                                                  'Expected: {}.\nResult: {}'.format(expected, result))

    def test_cssm_expired_license_returns_dict(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_expired_licenses()

        self.assertIsInstance(result, dict, '    def test_cssm_expired_license_returns_dict should return a dict')

    def test_cssm_expired_license_returns_correct_info(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_expired_licenses()

        expected = {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': {'endDate': '2019/05/31', 'quantity': 50}}}}

        self.assertEqual(expected, result,
                         'test_cssm_expired_license_returns_correct_info should return correct value\n'
                         'Expected: {}\n'
                         'Result: {}'.format(expected, result))

    def test_cssm_expired_license_returns_correct_info_full(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_expired_licenses()

        expected = {'BU Production Test': {'ATT Account Team': {'CSR 1KV APPX 500M': {'endDate': '2019/05/31',
                                                                   'quantity': 1},
                                             'CSR 1KV AX 5G': {'endDate': '2019/05/23',
                                                               'quantity': 4},
                                             'CSR 1KV IP BASE 10G': {'endDate': '2019/05/23',
                                                                     'quantity': 4}},
                        'ATT CUSTOMER 1': {'ISRV APPX 10M': {'endDate': '2019/05/31',
                                                             'quantity': 1},
                                           'ISRV AX 2500M': {'endDate': '2019/04/02',
                                                             'quantity': 5},
                                           'ISRV IPB 2500M': {'endDate': '2019/04/02',
                                                              'quantity': 5}},
                        'ATT ENCS': {'CSR 1KV AX 5G': {'endDate': '2019/05/23',
                                                       'quantity': 6}}},
 'Cisco Sales Enablement': {'Alex Daltrini (adaltrin)': {'ISRV AX 500M': {'endDate': '2019/05/31',
                                                                          'quantity': 10}},
                            'DEFAULT': {'ISRV AX 250M': {'endDate': '2018/11/19',
                                                         'quantity': 4990},
                                        'ISR_4331_UnifiedCommunication': {'endDate': '2019/07/19',
                                                                          'quantity': 90}}}}

        self.assertEqual(expected, result,
                         'test_cssm_expired_license_returns_correct_info should return correct value\n'
                         'Expected: {}\n'
                         'Result: {}'.format(expected, result))

    def test_cssm_top_five_expired_licenses_returns_correct_dict(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_top_five_expired_licenses()

        expected = \
        {'BU Production Test': {'ATT Account Team': {'CSR 1KV AX 5G': {'endDate': '2019/05/23',
                                                                       'quantity': 4}},
                                'ATT CUSTOMER 1': {'ISRV AX 2500M': {'endDate': '2019/04/02',
                                                                     'quantity': 5},
                                                   'ISRV IPB 2500M': {'endDate': '2019/04/02',
                                                                      'quantity': 5}},
                                'ATT ENCS': {'CSR 1KV AX 5G': {'endDate': '2019/05/23',
                                                               'quantity': 6}}},
         'Cisco Sales Enablement': {'DEFAULT': {'ISRV AX 250M': {'endDate': '2018/11/19',
                                                                 'quantity': 4990}}}}

        self.assertEqual(expected, result,
                         'test_cssm_top_five_expired_licenses_returns_correct_dict should return correct value\n'
                         'Expected: {}\n'
                         'Result: {}'.format(expected, result))


    def test_cssm_license_shortage_returns_dict(self):
        with open('./shortage_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_license_shortage()

        self.assertIsInstance(result, dict, 'test_cssm_license_shortage_returns_dict should return a dict')

    def test_cssm_license_shortage_returns_correct_dict(self):
        with open('./shortage_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_license_shortage()

        expected = {'BU Production Test': {'Customer III': [{'license': 'ISRV APPX 10M', 'quantity': 1, 'inUse': 60, 'shortage': 59}, {'license': 'ISRV APPX 100M', 'quantity': 1, 'inUse': 45, 'shortage': 44}, {'license': 'CSR 1KV APPX 2500M', 'quantity': 100, 'inUse': 125, 'shortage': 25}], 'ATT ENCS': [{'license': 'CSR 1KV APPX 2500M', 'quantity': 100, 'inUse': 113, 'shortage': 13}], 'Customer II': [{'license': 'ISRV APPX 10M', 'quantity': 1, 'inUse': 5, 'shortage': 4}], 'Customer I': [{'license': 'ISRV APPX 100M', 'quantity': 1, 'inUse': 3, 'shortage': 2}]}}
        self.assertEqual(expected, result,
                              'test_cssm_license_shortage_returns_correct_dict should return correct dict.\n \
                              Expected: {}\nResult:{}'.format(expected, result))

    def test_cssm_license_top_five_shortage_returns_correct_dict(self):
        with open('./shortage_license_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_license_top_five_shortage()

        expected = {'BU Production Test': {'Customer III': [{'license': 'ISRV APPX 10M', 'quantity': 1, 'inUse': 60, 'shortage': 59}, {'license': 'ISRV APPX 100M', 'quantity': 1, 'inUse': 45, 'shortage': 44}, {'license': 'CSR 1KV APPX 2500M', 'quantity': 100, 'inUse': 125, 'shortage': 25}], 'ATT ENCS': [{'license': 'CSR 1KV APPX 2500M', 'quantity': 100, 'inUse': 113, 'shortage': 13}], 'Customer II': [{'license': 'ISRV APPX 10M', 'quantity': 1, 'inUse': 5, 'shortage': 4}]}}
        self.assertEqual(expected, result,
                              'test_cssm_license_shortage_returns_correct_dict should return correct dict.\n \
                              Expected: {}\nResult:{}'.format(expected, result))

    def test_cssm_license_wo_assigned_licenses_returns_correct_accountNames(self):
        the_list = [{'accountType': 'CUSTOMER', 'accountName': 'SA SME',
                     'roles': [{'licenses': [], 'role': 'Smart Account User'}, {'licenses': [
                         {'license': 'CSR 1KV APPX 100M', 'reserved': 0, 'billingType': 'USAGE', 'isPortable': False,
                          'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [
                             {'startDate': '2019-01-18T01:07:36Z', 'endDate': '2022-01-17T01:07:36Z',
                              'subscriptionId': 'Sub208966', 'status': 'ACTIVE', 'licenseType': 'STANDARD',
                              'quantity': 1}], 'licenseSubstitutions': [], 'available': 1, 'inUse': 0, 'quantity': 1,
                          'status': 'In Compliance'},
                         {'license': 'DNA Advantage For SDWAN', 'reserved': 0, 'billingType': 'PREPAID',
                          'isPortable': False, 'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0,
                          'licenseDetails': [
                              {'startDate': '2019-05-20', 'endDate': '2022-05-19', 'subscriptionId': 'Sub269233',
                               'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100},
                              {'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None,
                               'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100}], 'licenseSubstitutions': [],
                          'available': 200, 'inUse': 0, 'quantity': 200, 'status': 'In Compliance'},
                         {'license': 'ISRV AX 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False,
                          'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [
                             {'startDate': '2019-05-20', 'endDate': '2022-05-19', 'subscriptionId': 'Sub269233',
                              'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100},
                             {'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None,
                              'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 50}], 'licenseSubstitutions': [],
                          'available': 150, 'inUse': 0, 'quantity': 150, 'status': 'In Compliance'}],
                                                                                'role': 'Virtual Account Administrator',
                                                                                'virtualAccount': 'AT&T'}, {
                                   'licenses': [{'license': 'ISRV AX 1G', 'reserved': 0, 'billingType': 'PREPAID',
                                                 'isPortable': False, 'virtualAccount': 'ATT EE CUSTOMER C',
                                                 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [
                                           {'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None,
                                            'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 50}],
                                                 'licenseSubstitutions': [], 'available': 50, 'inUse': 0,
                                                 'quantity': 50, 'status': 'In Compliance'}],
                                   'role': 'Virtual Account Administrator', 'virtualAccount': 'ATT EE CUSTOMER C'}],
                     'accountDomain': 'sasme.cisco.com', 'accountStatus': 'Active'},
                    {'accountType': 'CUSTOMER', 'accountName': 'Cisco Sales Enablement', 'roles': [{'licenses': [
                        {'license': 'ASAv10 Standard - 1G', 'reserved': 0, 'billingType': 'PREPAID',
                         'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False,
                         'pendingQuantity': 0, 'licenseDetails': [
                            {'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE',
                             'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10,
                         'inUse': 0, 'quantity': 10, 'status': 'In Compliance'},
                        {'license': 'ISRV AX 250M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False,
                         'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0,
                         'licenseDetails': [
                             {'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE',
                              'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10,
                         'inUse': 0, 'quantity': 10, 'status': 'In Compliance'},
                        {'license': 'ISRV AX 500M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False,
                         'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0,
                         'licenseDetails': [
                             {'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE',
                              'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10,
                         'inUse': 0, 'quantity': 10, 'status': 'In Compliance'},
                        {'license': 'ISRV IPBase 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False,
                         'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0,
                         'licenseDetails': [
                             {'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE',
                              'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10,
                         'inUse': 0, 'quantity': 10, 'status': 'In Compliance'},
                        {'license': 'ISRV IPBase 500M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False,
                         'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0,
                         'licenseDetails': [
                             {'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE',
                              'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10,
                         'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}],
                                                                                                    'role': 'Virtual Account Administrator',
                                                                                                    'virtualAccount': 'Alex Daltrini (adaltrin)'}],
                     'accountDomain': 'sales-enablement.cisco.com', 'accountStatus': 'Active'}]

        #     the_json = json.loads(the_list)
        print(json.dumps(the_list, indent=4))
        parser = cssm_parser.CSSMJSONParser(the_list)

        result = parser.cssm_license()

        # expected = ['BU Production Test', 'Cisco Demo Customer Smart Account', 'Federal Team Testing Cisco Account', 'Cisco Sales Enablement']
        expected_array = ['SA SME', 'Cisco Sales Enablement']
        result_array = result.account_names()

        outer_compare_result = True

        for expected in expected_array:
            inner_compare_result = False
            for result in result_array:
                if result == expected:
                    inner_compare_result = True
                    break

            if inner_compare_result == False:
                outer_compare_result = False
                break

        self.assertTrue(outer_compare_result, "test_returns_an_array_with_correct_account_names should be equal.  "
                                              "\nExpected: {}\nResult: {}\n".format(expected_array, result_array))


    def test_cssm_thirty_day_expired_license_returns_correct_info(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        expected = {
            'BU Production Test':
                {
                    'ATT ENCS':
                        {
                            'CSR 1KV APPX 2500M':
                                [
                                    {
                                        'quantity': 50,

                                    },
                                    {
                                        'quantity': 50,

                                    }
                                ]
                        }

                }
        }

        for the_dict in json_array:
        #   print('the_dict keys: {}'.format(the_dict.keys()))

            for roles_dict in the_dict['roles']:
                for licenses in roles_dict['assignedLicenses']['licenses']:
                    iCntr = 0
                    for license_detail in licenses['licenseDetails']:
                        the_date = (dt.datetime.now(timezone.utc) + timedelta(days=10 + iCntr))
                        license_detail['endDate'] = the_date.strftime('%Y-%m-%d')
                        expected['BU Production Test']['ATT ENCS']['CSR 1KV APPX 2500M'][iCntr]['endDate']=the_date.strftime('%Y/%m/%d')
                        iCntr = iCntr + 1

                        print(license_detail)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_future_expired_licenses(30)



        self.assertEqual(expected, result,
                         'test_cssm_thirty_day_expired_license_returns_correct_info should return correct value\n'
                         'Expected: \n{}\n'
                         'Result:\n {}'.format(expected, result))

    def test_cssm_ninety_day_expired_license_returns_correct_info(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        expected = {'future_expired_licenses': {
                'BU Production Test':
                    {
                        'ATT ENCS':
                            {
                                'CSR 1KV APPX 2500M':
                                    [
                                        {
                                            'quantity': 50,

                                        },
                                        {
                                            'quantity': 50,

                                        }
                                    ]
                            }

                    }
            },
            'quantity': 2}

        for the_dict in json_array:
        #   print('the_dict keys: {}'.format(the_dict.keys()))

            for roles_dict in the_dict['roles']:
                for licenses in roles_dict['assignedLicenses']['licenses']:
                    iCntr = 0
                    for license_detail in licenses['licenseDetails']:
                        the_date = (dt.datetime.now(timezone.utc) + timedelta(days=65 + iCntr))
                        license_detail['endDate'] = the_date.strftime('%Y-%m-%d')
                        expected['BU Production Test']['ATT ENCS']['CSR 1KV APPX 2500M'][iCntr]['endDate']=the_date.strftime('%Y/%m/%d')
                        iCntr = iCntr + 1

                        print(license_detail)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_future_expired_licenses(90)

        self.assertEqual(expected, result,
                         'test_cssm_ninety_day_expired_license_returns_correct_info should return correct value\n'
                         'Expected: \n{}\n'
                         'Result:\n {}'.format(expected, result))

    def test_cssm_sixty_day_expired_license_returns_correct_info(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        expected = {
            'BU Production Test':
                {
                    'ATT ENCS':
                        {
                            'CSR 1KV APPX 2500M':
                                [
                                    {
                                        'quantity': 50,

                                    },
                                    {
                                        'quantity': 50,

                                    }
                                ]
                        }

                }
        }

        for the_dict in json_array:
        #   print('the_dict keys: {}'.format(the_dict.keys()))

            for roles_dict in the_dict['roles']:
                for licenses in roles_dict['assignedLicenses']['licenses']:
                    iCntr = 0
                    for license_detail in licenses['licenseDetails']:
                        the_date = (dt.datetime.now(timezone.utc) + timedelta(days=45 + iCntr))
                        license_detail['endDate'] = the_date.strftime('%Y-%m-%d')
                        expected['BU Production Test']['ATT ENCS']['CSR 1KV APPX 2500M'][iCntr]['endDate']=the_date.strftime('%Y/%m/%d')
                        iCntr = iCntr + 1

                        print(license_detail)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_future_expired_licenses(expiration_days=60)

        self.assertEqual(expected, result,
                         'test_cssm_ninety_day_expired_license_returns_correct_info should return correct value\n'
                         'Expected: \n{}\n'
                         'Result:\n {}'.format(expected, result))

    def test_cssm_one_eight_day_expired_license_returns_correct_info(self):
        with open('./multiple_assigned_license_test.json') as json_data:
            json_array = json.load(json_data)

        expected = {
            'BU Production Test':
                {
                    'ATT ENCS':
                        {
                            'CSR 1KV APPX 2500M':
                                [
                                    {
                                        'quantity': 50,

                                    },
                                    {
                                        'quantity': 50,

                                    }
                                ]
                        }

                }
        }

        for the_dict in json_array:
        #   print('the_dict keys: {}'.format(the_dict.keys()))

            for roles_dict in the_dict['roles']:
                for licenses in roles_dict['assignedLicenses']['licenses']:
                    iCntr = 0
                    for license_detail in licenses['licenseDetails']:
                        the_date = (dt.datetime.now(timezone.utc) + timedelta(days=120 + iCntr))
                        license_detail['endDate'] = the_date.strftime('%Y-%m-%d')
                        expected['BU Production Test']['ATT ENCS']['CSR 1KV APPX 2500M'][iCntr]['endDate']=the_date.strftime('%Y/%m/%d')
                        iCntr = iCntr + 1

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_future_expired_licenses(180)

        self.assertEqual(expected, result,
                         'test_cssm_ninety_day_expired_license_returns_correct_info should return correct value\n'
                         'Expected: \n{}\n'
                         'Result:\n {}'.format(expected, result))

    def test_cssm_top_five_future_license_expired_correct_info(self):
        with open('./multiple_future_expiration.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        result = parser.cssm_license().cssm_top_five_future_expired_licenses(expiration_days=180)
        expected = {'future_expired_licenses': {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': [{'endDate': '2019/08/04',
                                                                                         'quantity': 50}]},
                                                    'Some Virtual Account 1': {'CSR 1KV APPX 10M': [{'endDate': '2019/09/04',
                                                                                                     'quantity': 50}],
                                                                               'Test License': [{'endDate': '2019/09/15',
                                                                                                 'quantity': 50}]}},
                             'Some Goofy Production Test': {'Awesome Cisco Customer': {'Test License IV': [{'endDate': '2019/11/04',
                                                                                                            'quantity': 50}]},
                                                            'Great Cisco Customer': {'Test License III': [{'endDate': '2019/11/30',
                                                                                                           'quantity': 50}]}}},
 'quantity': 5}

        self.assertEqual(expected, result,
                         'test_cssm_top_five_future_license_expired_correct_info should return correct value\n'
                         'Expected: \n{}\n'
                         'Result:\n {}'.format(expected, result))

    def test_cssm_usage_returns_correct_info(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        usage_df = the_cssm_license.cssm_license_usage_df().sort_values('usage', ascending=False)
        print(usage_df)

        result = usage_df.iloc[3,3]

        expected = 34.0

        self.assertEqual(expected, result, 'test_cssm_usage_returns_correct_info.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_prepare_cssm_usage_dict_returns_correct_info(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        usage_df = the_cssm_license.cssm_license_usage_df()

        print(type(usage_df))
        print(usage_df.index)

        result = the_cssm_license.cssm_prepare_license_usage_dict(usage_df)

        expected = {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': {'usage': 14.000000000000002}},
                        'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                    'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                    'Some License': {'usage': 64.0}}},
 'Other Production Test': {'Great Cisco Customer': {'ASAv10 Standard - 1G': {'usage': 56.00000000000001},
                                                    'C9400 Network Advantage': {'usage': 34.0}},
                           'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                       'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                       'Some License': {'usage': 64.0}}}}

        self.assertEqual(expected, result, 'test_prepare_cssm_usage_dict_returns_correct_info.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))

    def test_prepare_top_cssm_usage_dict_returns_correct_info(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        usage_df = the_cssm_license.cssm_license_usage_df()

        print(type(usage_df))
        print(usage_df.index)

        result = the_cssm_license.cssm_prepare_license_usage_dict(usage_df)

        expected = {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': {'usage': 14.000000000000002}},
                        'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                    'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                    'Some License': {'usage': 64.0}}},
 'Other Production Test': {'Great Cisco Customer': {'ASAv10 Standard - 1G': {'usage': 56.00000000000001},
                                                    'C9400 Network Advantage': {'usage': 34.0}},
                           'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                       'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                       'Some License': {'usage': 64.0}}}}

        self.assertEqual(expected, result, 'test_prepare_top_cssm_usage_dict_returns_correct_info.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_cssm_usage_dict_returns_correct_info(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()


        result = the_cssm_license.cssm_license_usage_dict()

        expected = {'dict_size': 6,
 'usage_dict': {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': {'usage': 14.000000000000002}},
                                       'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                                   'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                                   'Some License': {'usage': 64.0}}},
                'Other Production Test': {'Great Cisco Customer': {'ASAv10 Standard - 1G': {'usage': 56.00000000000001},
                                                                   'C9400 Network Advantage': {'usage': 34.0}},
                                          'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                                      'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                                      'Some License': {'usage': 64.0}}}}}
        self.assertEqual(expected, result, 'test_cssm_usage_dict_returns_correct_info.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))

    def test_cssm_top_usage_dict_returns_correct_info(self):
        with open('./usage_test.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()


        result = the_cssm_license.cssm_top_license_usage_dict()

        expected = {'BU Production Test': {'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                    'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                    'Some License': {'usage': 64.0}}},
 'Other Production Test': {'Great Cisco Customer': {'ASAv10 Standard - 1G': {'usage': 56.00000000000001},
                                                    'C9400 Network Advantage': {'usage': 34.0}},
                           'Terrific Cisco Customer': {'CSR 1KV APPX 10M': {'usage': 24.0},
                                                       'Prime Infrastructure 3.x, BASE Lic.': {'usage': 44.0},
                                                       'Some License': {'usage': 64.0}}}}

        self.assertEqual(expected, result, 'test_cssm_usage_dict_returns_correct_info.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_cssm_usage_dict_returns_correct_info_with_shortage(self):
        with open('./usage_test_large.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()


        result = the_cssm_license.cssm_license_usage_dict()

        expected = {'dict_size': 10,
 'usage_dict': {'BU Production Test': {'ATT ENCS': {'CSR 1KV APPX 2500M': {'usage': 14.000000000000002}},
                                       'Some Virtual Account 1': {'C9400 Network Advantage': {'usage': 64.0},
                                                                  'CSR 1KV APPX 10M': {'usage': 24.0}}},
                'Other Production Test': {'Great Cisco Customer': {'ACI Advantage License for 10+G Leaf': {'usage': 4.0},
                                                                   'Aironet DNA Advantage Term Licenses': {'usage': 6.0},
                                                                   'Cisco ASAv5': {'usage': 8.0},
                                                                   'UC Manager Basic License  (12.x)': {'usage': 10.0},
                                                                   'Virtual WLC Access Point License': {'usage': 44.0}},
                                          'Terrific Cisco Customer': {'CSR 1KV AX 250M': {'usage': 34.0},
                                                                      'Cisco Intersight SaaS - Essentials': {'usage': 56.00000000000001}}}}}

        self.assertEqual(expected, result, 'test_cssm_usage_dict_returns_correct_info_with_shortage.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_cssm_technology_works(self):
        with open('./my_licensing_info.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_dataframe

        expected = {}

        print(result)

        self.assertEqual(expected, result, 'test_cssm_technology_works.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_cssm_technology_df_is_correct(self):
        with open('./alex_json_v1.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_license_technology_df()

        expected = pd.DataFrame()

        print(result.iloc[0, :])
        print(result.iloc[1, :])
        print(result.iloc[2, :])
        print(result.iloc[3, :])

        self.assertEqual(expected, result, 'test_cssm_technology_df_is_correct.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))


    def test_cssm_license_top_technology_correct_alex(self):
        with open('./alex_json_v1.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_top_license_technology_dict()


        expected = {'PnP Test Account - KB': {'Security': {'inUse': 52.94117647058823},
                                              'Enterprise Networking': {'inUse': 47.05882352941177}}}


        self.assertEqual(expected, result, 'test_cssm_license_top_technology_correc_alext.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))

    def test_cssm_license_top_technology_correct_alex2(self):
        with open('./alex_json_v2.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_top_license_technology_dict()


        expected = {'PnP Test Account - KB': {'Data Center': {'inUse': 49.504950495049506},
                           'Enterprise Networking': {'inUse': 23.762376237623762},
                           'Security': {'inUse': 26.73267326732673}}}

        self.assertEqual(expected, result, 'test_cssm_license_top_technology_correc_alext.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))

    def test_cssm_license_top_technology_correct_empty(self):
        with open('./my_licensing_info.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_top_license_technology_dict()


        expected = {}



        self.assertEqual(expected, result, 'test_cssm_license_top_technology_correct_empty.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))

    def test_cssm_license_top_technology_correct_mainline(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        the_cssm_license = parser.cssm_license()

        result = the_cssm_license.cssm_top_license_technology_dict()


        expected = {'BU Production Test': {'Enterprise Networking': {'inUse': 72.83236994219654},
                        'Security': {'inUse': 27.167630057803468}},
 'Cisco Demo Customer Smart Account': {'Security': {'inUse': 100.0}},
 'Cisco Sales Enablement': {'Enterprise Networking': {'inUse': 99.53115842938074},
                            'Security': {'inUse': 0.46884157061926157}},
 'Federal Team Testing Cisco Account': {'Data Center': {'inUse': 28.125},
                                        'Enterprise Networking': {'inUse': 65.625},
                                        'Security': {'inUse': 6.25}}}

        self.assertEqual(expected, result, 'test_cssm_license_top_technology_correct_empty.\n'
                                           'Expected: {}\n Result: {}'.format(expected, result))







if __name__ == '__main__':
    unittest.main()
