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
from datetime import datetime, timezone, timedelta
from loguru import logger
import functools
import json

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

"""
This function is meant to be used with Pandas Dataframes to quickly associated an architecture/technology with a 
particular license
"""
def license_technology_architecture(technology_dict, row):
    if row['license'] in technology_dict:
        architecture_dict = technology_dict[row['license']]
        return architecture_dict['architecture_1']
    else:
        logger.error('   missing architecture for license:  {}'.format(row['license']))
        return "Uncategorized"

"""
This function is meant to be used with Pandas Dataframes to calculate license utilization
"""
def license_utilization(inUse, assignedLicenses_quantity):
    return 100.0*(inUse/assignedLicenses_quantity)

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
This object is where all the magic happens.  It is initialized by a dataframe fed to it from the CSSMJSONParser.
This object will then use that dataframe to generate dataframes of information for specific requests.  i.e. for 
shortages, license usage, technology/architecture mix etc.  

All the instance variable are loaded lazily to be more efficient

Typically, each request from a user is supported by 2-3 functions.  While the one function could probably make it work, 
dividing into several allows for test driven development.

The three types of functions are (typically)
1. create the dataframe, 
2. massage the dataframe for a specific use case,
3. package up the info into a python dictionary for use by the sld_pushbot_function so that it can create a message 
"""
class CSSMLicense(object):
    @logger_wraps()
    def __init__(self, cssm_dataframe):
        self.cssm_dataframe = cssm_dataframe

        self.__cssm_virt_accounts_by_accountName = None
        self.__cssm_expired_licenses = None
        self.__account_names = None
        self.__cssm_license_shortage = None
        self.__cssm_license_top_five_shortage = None
        self.__cssm_top_license_usage_dict = None
        self.__cssm_license_usage_dict = None
        self.__cssm_top_license_technology_dict = None

    @logger_wraps()
    def account_names(self):
        if self.__account_names is None:
            self.__account_names = []
            if len(self.cssm_dataframe) > 0:
                self.__account_names = list(self.cssm_dataframe['accountName'].unique())

        return self.__account_names

    @logger_wraps()
    def cssm_future_expired_df(self, expiration_days=30):

        future_expired_df = self.cssm_dataframe[(self.cssm_dataframe['endDate'] < (datetime.now(timezone.utc)+timedelta(days=expiration_days))) &
                            ((datetime.now(timezone.utc) < self.cssm_dataframe['endDate'] ))]
        return future_expired_df.sort_values(by=['endDate','quantity'], ascending=[True, False])

    @logger_wraps()
    def cssm_prepare_future_expired_license_dict(self, expired_df):

        accountNames = expired_df['accountName'].unique()
        return_dict = {'quantity': len(expired_df)}
        account_dict = {}
        for accountName in accountNames:

           virtualAccount_dict = {}
           virtualAccounts = list(expired_df[expired_df['accountName'] == accountName]['virtualAccount'].unique())

           for virtualAccount in virtualAccounts:

                the_licenses = list(expired_df[expired_df['virtualAccount'] == virtualAccount]['license'].unique())

                virtual_account_df = expired_df[expired_df['virtualAccount'] == virtualAccount]
                license_dict = {}
                for license in the_licenses:

                    license_df = virtual_account_df[virtual_account_df['license']==license]

                    details_list = []
                    for index, row in license_df.iterrows():
                        details_dict = {'quantity': row['quantity'],
                                        'endDate': row['endDate'].strftime('%Y/%m/%d')}
                        details_list.append(details_dict)

                    license_dict[row['license']] = details_list

                virtualAccount_dict[virtualAccount] = license_dict


           account_dict[accountName] = virtualAccount_dict

        return_dict['future_expired_licenses'] = account_dict

        return return_dict

    @logger_wraps()
    def cssm_top_five_future_expired_licenses(self, expiration_days=180):
        logger.info('expiration days: {}'.format(expiration_days))

        df = self.cssm_dataframe

        expired_df = self.cssm_future_expired_df(expiration_days=expiration_days)

        return self.cssm_prepare_future_expired_license_dict(expired_df.head(5))

    @logger_wraps()
    def cssm_future_expired_licenses(self, expiration_days=30):
        logger.info('expiration days: {}'.format(expiration_days))

        df = self.cssm_dataframe

        expired_df = self.cssm_future_expired_df(expiration_days=expiration_days)

        return self.cssm_prepare_future_expired_license_dict(expired_df)

    @logger_wraps()
    def cssm_prepare_license_usage_dict(self, usage_df):
        accountNames = usage_df['accountName'].unique()
        the_dict = {}
        for accountName in accountNames:
            virtualAccount_dict = {}
            virtualAccounts = list(usage_df[usage_df['accountName'] == accountName]['virtualAccount'].unique())

            for virtualAccount in virtualAccounts:

                license_df = usage_df[usage_df['virtualAccount'] == virtualAccount]
                license_dict = {}
                for index, row in license_df.iterrows():
                    license_dict[row['license']] = {'usage': row['usage']}
                virtualAccount_dict[virtualAccount] = license_dict

            the_dict[accountName] = virtualAccount_dict

        return the_dict

    @logger_wraps()
    def cssm_license_usage_dict(self):
        if self.__cssm_license_usage_dict == None:
            usage_df = self.cssm_license_usage_df()

            self.__cssm_license_usage_dict = {}
            usage_df = usage_df[ (usage_df['usage'] > 0) & (usage_df['assignedLicenses_quantity'] > 0) ]
            usage_size = len(usage_df)
            if usage_size > 0:
                self.__cssm_license_usage_dict = {'dict_size': usage_size,
                                                  'usage_dict': self.cssm_prepare_license_usage_dict(usage_df)}

        return self.__cssm_license_usage_dict

    def cssm_top_license_usage_dict(self):
        if self.__cssm_top_license_usage_dict == None:
            usage_df = self.cssm_license_usage_df().sort_values('usage', ascending=False)

            self.__cssm_top_license_usage_dict = {}
            usage_df = usage_df[ (usage_df['usage'] > 0) & (usage_df['assignedLicenses_quantity'] > 0) ]
            if len(usage_df) > 0:
                self.__cssm_top_license_usage_dict = self.cssm_prepare_license_usage_dict(usage_df.head(5))

        return self.__cssm_top_license_usage_dict

    @logger_wraps()
    def cssm_license_usage_df(self):

        usage_df = self.cssm_dataframe

        groupd_df = usage_df.groupby(['accountName', 'virtualAccount', 'license'])[
            'inUse', 'assignedLicenses_quantity'].sum()

        groupd_df['usage'] = license_utilization(groupd_df['inUse'], groupd_df['assignedLicenses_quantity'])

        return groupd_df.reset_index()

    @logger_wraps()
    def cssm_prepare_license_technology_dict(self, usage_df):
        accountNames = usage_df['accountName'].unique()
        the_dict = {}
        for accountName in accountNames:
            architecture_dict = {}
            architecture_df = usage_df[usage_df['accountName'] == accountName]

            for index, row in architecture_df.iterrows():
                architecture_dict[row['architecture_1']] = {'inUse': row['inUse']}

            the_dict[accountName] = architecture_dict

        return the_dict

    logger_wraps()
    def cssm_top_license_technology_dict(self):
        if self.__cssm_top_license_technology_dict == None:

            technology_df = self.cssm_license_technology_df()

            if len(technology_df) > 0:
                technology_df.sort_values('inUse', ascending=False, inplace=True)
                print(technology_df)

                self.__cssm_top_license_technology_dict = {}
                if len(technology_df) > 0:
                    self.__cssm_top_license_technology_dict = self.cssm_prepare_license_technology_dict(technology_df)

            else:
                self.__cssm_top_license_technology_dict = {}

        return self.__cssm_top_license_technology_dict

    @logger_wraps()
    def cssm_license_technology_df(self):

        technology_df = self.cssm_dataframe[self.cssm_dataframe['inUse'] > 0]
       # technology_df = self.cssm_dataframe
        print(len(technology_df))
        grouped_pct = pd.DataFrame()
        if len(technology_df) > 0:
            with open('./technology_json_v2', 'r') as fp:
                technology_dict = json.load(fp)

            technology_df['architecture_1'] = technology_df.apply(
                lambda row: license_technology_architecture(technology_dict, row), axis=1)

            grouped_df = technology_df.groupby(['accountName', 'architecture_1']).agg(
                {'inUse': 'sum'})
            grouped_pct = grouped_df.groupby(level=0).apply(lambda x:
                                                            100 * x / float(x.sum()))

        return grouped_pct.reset_index()

    @logger_wraps()
    def cssm_prepare_expired_licenses_dict(self, expired_df):
        accountNames = expired_df['accountName'].unique()
        the_dict = {}
        for accountName in accountNames:
            virtualAccount_dict = {}
            virtualAccounts = list(expired_df[expired_df['accountName'] == accountName]['virtualAccount'].unique())

            for virtualAccount in virtualAccounts:

                license_df = expired_df[expired_df['virtualAccount'] == virtualAccount]
                license_dict = {}
                for index, row in license_df.iterrows():
                    license_dict[row['license']] = {'endDate': row['endDate'].strftime('%Y/%m/%d'),
                                                    'quantity': row['quantity']}
                virtualAccount_dict[virtualAccount] = license_dict

            the_dict[accountName] = virtualAccount_dict

        return the_dict

    @logger_wraps()
    def cssm_expired_licenses_df(self):

        df = self.cssm_dataframe

        expired_df = df[df['endDate'] < datetime.now(timezone.utc)]

        return expired_df.sort_values(by=['endDate'], ascending=True)

    @logger_wraps()
    def cssm_expired_licenses(self, va_filter_list=[]):

        expired_df = self.cssm_expired_licenses_df()

        if len(va_filter_list) > 0:
            expired_df = expired_df[expired_df['virtualAccount'].isin(va_filter_list)]

        return self.cssm_prepare_expired_licenses_dict(expired_df)


    @logger_wraps()
    def cssm_top_five_expired_licenses(self, va_filter_list=[]):

            expired_df = self.cssm_expired_licenses_df()

            if len(va_filter_list) > 0:
                expired_df = expired_df[expired_df['virtualAccount'].isin(va_filter_list)]

            return self.cssm_prepare_expired_licenses_dict(expired_df.head(5))

    @logger_wraps()
    def cssm_license_shortage_df(self):
        df = self.cssm_dataframe.drop_duplicates(subset=['virtualAccount', 'license', 'quantity', 'inUse'])
        df['shortage']=df['inUse']-df['assignedLicenses_quantity']
        return df[df['shortage']>0].sort_values('shortage',ascending=False)

    @logger_wraps()
    def cssm_prepare_license_shortage_dict(self, shortage_df):

        accountNames = shortage_df['accountName'].unique()
        the_dict = {}

        for accountName in accountNames:
            virtualAccount_dict = {}
            virtualAccounts = list(shortage_df[shortage_df['accountName'] == accountName]['virtualAccount'].unique())

            for virtualAccount in virtualAccounts:
                shortage_licenses = shortage_df[shortage_df['virtualAccount'] == virtualAccount]
                licenses = []
                for index, row in shortage_licenses.iterrows():
                    licenses.append({'license': row['license'],
                                     'quantity': row['assignedLicenses_quantity'],
                                     'inUse': row['inUse'],
                                     'shortage': row['shortage']
                                     })
                virtualAccount_dict[virtualAccount] = licenses

            the_dict[accountName] = virtualAccount_dict

        return the_dict

    @logger_wraps()
    def cssm_license_shortage(self):

       if self.__cssm_license_shortage is None:
           df = self.cssm_dataframe.drop_duplicates(subset=['virtualAccount', 'license', 'quantity', 'inUse'])

           shortage_df = self.cssm_license_shortage_df()

           self.__cssm_license_shortage = self.cssm_prepare_license_shortage_dict(shortage_df)

       return self.__cssm_license_shortage

    @logger_wraps()
    def cssm_license_top_five_shortage(self):

        if self.__cssm_license_top_five_shortage is None:
            df = self.cssm_dataframe.drop_duplicates(subset=['virtualAccount', 'license', 'quantity', 'inUse'])

            shortage_df = self.cssm_license_shortage_df()

            self.__cssm_license_top_five_shortage = self.cssm_prepare_license_shortage_dict(shortage_df.head(5))

    @logger_wraps()
    def cssm_virt_account_by_accountName(self):
        if self.__cssm_virt_accounts_by_accountName is None:
            df = self.cssm_dataframe

            accountNames = df['accountName'].unique()
            the_dict = {}
            for accountName in accountNames:
                the_dict[accountName] = list(df[df['accountName'] == accountName]['virtualAccount'].unique())

            self.__cssm_virt_accounts_by_accountName = the_dict

        return self.__cssm_virt_accounts_by_accountName
