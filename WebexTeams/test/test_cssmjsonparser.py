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

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

file_name = "./license_by_sa-va_full.json"


def license_utilization(inUse, assignedLicenses_quantity):
    return inUse/assignedLicenses_quantity


class CSSMJsonParsingTests(unittest.TestCase):
    def test_CSSMJSONParser_Object_exists(self):
        parser = cssm_parser.CSSMJSONParser()
        self.assertIsNotNone(parser, 'test_CSSMJSONParser_Object_exists should return a value')

    def test_returns_cssm_dataframe(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)


        parser = cssm_parser.CSSMJSONParser(json_array)

        expected = pd.DataFrame()
        self.assertIsInstance(parser.cssm_dataframe(), pd.DataFrame)

    def test_json_from_list(self):
        the_list = [{'accountType': 'CUSTOMER', 'accountName': 'SA SME', 'roles': [{'licenses': [], 'role': 'Smart Account User'}, {'licenses': [{'license': 'CSR 1KV APPX 100M', 'reserved': 0, 'billingType': 'USAGE', 'isPortable': False, 'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': '2019-01-18T01:07:36Z', 'endDate': '2022-01-17T01:07:36Z', 'subscriptionId': 'Sub208966', 'status': 'ACTIVE', 'licenseType': 'STANDARD', 'quantity': 1}], 'licenseSubstitutions': [], 'available': 1, 'inUse': 0, 'quantity': 1, 'status': 'In Compliance'}, {'license': 'DNA Advantage For SDWAN', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': '2019-05-20', 'endDate': '2022-05-19', 'subscriptionId': 'Sub269233', 'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100}, {'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100}], 'licenseSubstitutions': [], 'available': 200, 'inUse': 0, 'quantity': 200, 'status': 'In Compliance'}, {'license': 'ISRV AX 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'AT&T', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': '2019-05-20', 'endDate': '2022-05-19', 'subscriptionId': 'Sub269233', 'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 100}, {'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 50}], 'licenseSubstitutions': [], 'available': 150, 'inUse': 0, 'quantity': 150, 'status': 'In Compliance'}], 'role': 'Virtual Account Administrator', 'virtualAccount': 'AT&T'}, {'licenses': [{'license': 'ISRV AX 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'ATT EE CUSTOMER C', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': '2019-05-30', 'endDate': '2020-05-29', 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'TERM', 'quantity': 50}], 'licenseSubstitutions': [], 'available': 50, 'inUse': 0, 'quantity': 50, 'status': 'In Compliance'}], 'role': 'Virtual Account Administrator', 'virtualAccount': 'ATT EE CUSTOMER C'}], 'accountDomain': 'sasme.cisco.com', 'accountStatus': 'Active'}, {'accountType': 'CUSTOMER', 'accountName': 'Cisco Sales Enablement', 'roles': [{'licenses': [{'license': 'ASAv10 Standard - 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10, 'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}, {'license': 'ISRV AX 250M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10, 'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}, {'license': 'ISRV AX 500M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10, 'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}, {'license': 'ISRV IPBase 1G', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10, 'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}, {'license': 'ISRV IPBase 500M', 'reserved': 0, 'billingType': 'PREPAID', 'isPortable': False, 'virtualAccount': 'Alex Daltrini (adaltrin)', 'ahaApps': False, 'pendingQuantity': 0, 'licenseDetails': [{'startDate': None, 'endDate': None, 'subscriptionId': None, 'status': 'ACTIVE', 'licenseType': 'PERPETUAL', 'quantity': 10}], 'licenseSubstitutions': [], 'available': 10, 'inUse': 0, 'quantity': 10, 'status': 'In Compliance'}], 'role': 'Virtual Account Administrator', 'virtualAccount': 'Alex Daltrini (adaltrin)'}], 'accountDomain': 'sales-enablement.cisco.com', 'accountStatus': 'Active'}]

   #     the_json = json.loads(the_list)
        print(json.dumps(the_list, indent=4))
        parser = cssm_parser.CSSMJSONParser(the_list)

        expected = pd.DataFrame()

        print('  dataframe:  {}'.format(parser.cssm_dataframe().info()))
        print('yeah:  {}'.format(parser.cssm_dataframe()['accountName']))
        self.assertIsInstance(parser.cssm_dataframe(), pd.DataFrame)

    def test_returns_cssm_license_for_williams_json(self):
        with open('./william_v1.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license().account_names()

        expected = ['BU Production Test', 'Cisco Sales Enablement']

        self.assertEqual(expected, result,
                         'test_returns_cssm_license_for_williams_json should return correct license info.  '
                         '\nExpected:\n{}\nResult:\n{}'.format(expected, result))

    def test_returns_cssm_license_for_williams_json2(self):
        with open('./william_json_v2.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license().account_names()

        expected = ['Cisco Sales Enablement']

        self.assertEqual(expected, result,
                         'test_returns_cssm_license_for_williams_json2 should return correct license info.  '
                         '\nExpected:\n{}\nResult:\n{}'.format(expected, result))

    def test_returns_cssm_license_for_alex_json(self):
        with open('./alex_json_v1.json') as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license().account_names()

        expected = ['PnP Test Account - KB', 'SA SME', 'Cisco Sales Enablement']

        self.assertEqual(expected, result,
                         'test_returns_cssm_license_for_alex_json should return correct license info.  '
                         '\nExpected:\n{}\nResult:\n{}'.format(expected, result))

        result = parser.cssm_license().cssm_virt_account_by_accountName()

        expected = {'PnP Test Account - KB': ['RCDN-lab', 'ENCS', 'Crossroad Select', 'lcartwri - SD-WAN BT-1', 'STARFLIGHT-1-VA', 'TDOELLMA', 'MnM-Project', 'IoT-IA-PTP', 'Kishan-test', 'STARFLIGHT-VA', 'PNP-LABFKF', 'hkardame_test_cedge_order', 'BASE2HQ', 'DubDemo Enterprise Networks', 'ENFV-LAB', 'wirelesspnp'], 'SA SME': ['IBM-SDWAN deployment', 'ATT EE CUSTOMER C', 'SASME-demo', 'DEFAULT', 'SDWAN', 'AT&T'], 'Cisco Sales Enablement': ['Alex Daltrini (adaltrin)', 'DEFAULT']}

        self.assertEqual(expected, result,
                         'test_returns_cssm_license_for_alex_json should return correct virtual accounts license info.  '
                         '\nExpected:\n{}\nResult:\n{}'.format(expected, result))



    def test_misc_test(self):
        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)

        result = parser.cssm_license().account_names()

        the_cssm_license = parser.cssm_license()

        license_df = the_cssm_license.cssm_dataframe

        # print(result)
        print(parser.cssm_license().cssm_virt_account_by_accountName())
        # print(parser.cssm_license().cssm_top_five_expired_licenses())
        # print(parser.cssm_license().cssm_top_five_future_expired_licenses())
        # print(parser.cssm_license().cssm_license_top_five_shortage())

        # grouped = license_df.groupby(['virtualAccount','license']).agg('assignedLicenses_quantity')
        # print(grouped.head())
        #
        # print(type(grouped))
        #
        # for key, group_df in grouped:
        #     print(key)
        #     print(group_df.head())

        print(license_df.info())

        filtered_df = license_df[(license_df['accountName']=='BU Production Test')]

        groupd_df = filtered_df.groupby(['accountName', 'virtualAccount', 'license'])['inUse', 'assignedLicenses_quantity'].sum()

        print(type(groupd_df))
        groupd_df['usage'] = license_utilization(groupd_df['inUse'], groupd_df['assignedLicenses_quantity'])

        print(groupd_df.sort_values(['usage'], ascending=False))


        self.assertTrue(False,)




if __name__ == '__main__':
    unittest.main()
