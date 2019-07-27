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

import pandas as pd
import CSSMLicense
from loguru import logger
import functools


__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


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

"""
The main mission in life for this object is to take an array of json from the SmartAccountSDK and parse it into a Pandas
dataframe.  Putting the info into a dataframe allows us to slice and dice potentially large data sets with high
and relatively little effort.  

Most of the instance variable are loaded lazily.

Functions that use this object will initialize it with the json array from SmartAccountSDK and then get the CSSMLicense
object
"""

class CSSMJSONParser(object):
    @logger_wraps()
    def __init__(self, json_to_parse=""):
        logger.info('CSSMJSONParser, init start')
        self.json_to_parse = json_to_parse
        # logger.debug('   json to parse type: {}'.format(type(json_to_parse)))
        # logger.debug('   json to parse: {}'.format(json_to_parse))
        self.__cssm_license = None
        self.__cssm_dataframe = None
        logger.info('CSSMJSONParser, init end')

    @logger_wraps()
    def cssm_dataframe(self):
        logger.info('CSSMJSONParser, cssm_dataframe start')
        if self.__cssm_dataframe is None:
            logger.info('   self.__cssm_dataframe doesnt exist, creating')
            self.__cssm_dataframe = self.convert_json_to_dataframe()
        logger.info('CSSMJSONParser, cssm_dataframe end')
        return self.__cssm_dataframe

    @logger_wraps()
    def cssm_license(self):
        if self.__cssm_license is None:
            self.__cssm_license = CSSMLicense.CSSMLicense(self.cssm_dataframe())
        return self.__cssm_license

    # where the real magic happens
    @logger_wraps()
    def convert_json_to_dataframe(self):

        license_list = []
        # Iterate through the accounts
        for account in self.json_to_parse:
            accountName = account['accountName']
            accountDomain = account['accountDomain']
            accountStatus = account['accountStatus']
            accountType = account['accountType']

            account_dict = {'accountName': account['accountName'],
                            'accountDomain': account['accountDomain'],
                            'accountStatus': account['accountStatus'],
                            'accountType': account['accountType']}

            #Iterate through the "roles"
            for role_dict in account['roles']:
                # logger.info('     working on role_dict: {}'.format(role_dict))
                role = role_dict['role']
                account_dict['role'] = role

                # we are only interested, at least at this time, in the following roles.
                # "Appended VA USER" is a faux user created by the SmartAccountSDK due to some wonkiness in how
                # the BU Production Test domain is acting.
                if role in ['Virtual Account Administrator', 'Virtual Account User', 'APPENDED VA USER']:
                    account_dict['virtualAccount'] = role_dict['virtualAccount']
                    account_dict['virtualAccount_status'] = ""
                    account_dict['statusMessage'] = ""
                    licenses_array = []

                    # There will be "assigned licenses" or licenses.  Choose which one we have run into.
                    if 'assignedLicenses' not in role_dict.keys():
                        # Check to see if there are issues.
                        if 'licenses' not in role_dict.keys():
                            logger.error('No licenses or assignedLicenses found!!')
                            continue
                        licenses_array = role_dict['licenses']
                        logger.success('Licenses found!!')
                    else:
                        logger.success('assignedLicenses found!!')
                        licenses_array = role_dict['assignedLicenses']['licenses']
                        account_dict['virtualAccount_status'] = role_dict['assignedLicenses']['status']
                        account_dict['statusMessage'] = role_dict['assignedLicenses']['statusMessage']

                    license_info_dict = {}
                    account_dict_copy = {}

                    # work through the array of licenses
                    for license_dict in licenses_array:
                        # logger.info('         working on license_dict: {}'.format(license_dict))
                        license_info_dict['license'] = license_dict['license']
                        license_info_dict['assignedLicenses_quantity'] = license_dict['quantity']
                        license_info_dict['inUse'] = license_dict['inUse']
                        license_info_dict['available'] = license_dict['available']
                        license_info_dict['ahaApps'] = license_dict['ahaApps']
                        license_info_dict['billingType'] = license_dict['billingType']
                        license_info_dict['pendingQuantity'] = license_dict['pendingQuantity']
                        license_info_dict['reserved'] = license_dict['reserved']
                        license_info_dict['isPortable'] = license_dict['isPortable']
                        license_info_dict['assignedLicenses_status'] = license_dict['status']

                        license_info_dict_copy = license_info_dict.copy()
                        license_detail_dict = {}

                        # Each license could have multiple instances.  i.e. quantities purchase at different times
                        # iterate through them
                        for license_detail in license_dict['licenseDetails']:
                            # logger.info('             working on license_detail: {}'.format(license_detail))
                            if type(license_detail['startDate']) is not type(None):
                                if 'Z' in license_detail['startDate']:
                                    license_detail['startDate'] = \
                                        pd.to_datetime(license_detail['startDate'], format='%m/%d/%y %H:%M',
                                                       infer_datetime_format=True,
                                                       utc=True).to_pydatetime()
                                else:
                                    license_detail['startDate'] = \
                                        pd.to_datetime(license_detail['startDate'],
                                                       infer_datetime_format=True, utc=True).to_pydatetime()
                            if type(license_detail['endDate']) is not type(None):
                                if 'Z' in license_detail['endDate']:
                                    license_detail['endDate'] = \
                                        pd.to_datetime(license_detail['endDate'], format='%m/%d/%y %H:%M',
                                                       infer_datetime_format=True,
                                                       utc=True).to_pydatetime()
                                else:
                                    license_detail['endDate'] = \
                                        pd.to_datetime(license_detail['endDate'],
                                                       infer_datetime_format=True, utc=True).to_pydatetime()

                            # Once we have everything, put into the list of licenses.
                            # We create a copy of the account dict, because we want rows of data in the dataframe.
                            # the information gathered earlier in the account_dict is common for all rows associated
                            # with the account.  i.e. accountName, virtualAccount, etc.
                            account_dict_copy = account_dict.copy()
                            account_dict_copy.update(license_info_dict_copy)
                            account_dict_copy.update(license_detail)
                            license_list.append(account_dict_copy)

        # Last but not least, create the Pandas Dataframe.
        df = pd.DataFrame(license_list)
        logger.info('CSSMJSONParser, convert_json_to_dataframe end')

        return df
