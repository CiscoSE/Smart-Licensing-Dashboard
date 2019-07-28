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
import requests
import json
import datetime as dt
import CSSMJSONParser as cssm_parser
import pandas as pd
import io
from WBXTeamsBEIntegration import WBXTeamsBEIntegration
from requests_toolbelt import MultipartEncoder
from loguru import logger
import functools
import os
from cachetools import cached, \
    TTLCache  # 1 - let's import the "cached" decorator and the "TTLCache" object from cachetools
import threading

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"



be_service_name = 'SLD-WebexTeams-Bot-Service'

# Relevant URL's
url_base = "https://www.easysmartaccounts.com:10000/api/userinfo/access-token"
be_login_url = os.environ.get('SMART_LICENSING_LOGIN_URL')
cssm_url = os.environ.get('CSSM_DOMAIN')

# We cache our data for a few minutes so that subsequent requests from the client do not take too long.
license_cache = TTLCache(maxsize=100, ttl=300)

# for debugging purposes.
ARE_DEBUGGING=False
file_name = "./license_by_sa-va_full.json"

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


# This class is where the magic happens so far as being able to pull and parse the json from CSSM.
class SmartAccountSDK:
    @logger_wraps()
    def __init__(self, host, token):

        self.host = host
        self.token = token
        self.__all_licenses = None

    @logger_wraps()
    def list_accounts(self):
        """ returns all accounts associated with a user
        TODO: This could be a lot more defensive in terms of errors.
        """

        logger.info("preparing request")
        call = "/services/api/smart-accounts-and-licensing/v2/accounts/"
        uri = ("https://" + self.host + call)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.token}
        logger.info("done preparing request")
        response = requests.get(uri, headers=headers, verify=True)
        logger.info("received response")

        request_successful = False
        response_json = None
        if response.status_code == 200:
            logger.info("request was successful. status code 200")
            request_successful = True
            response_json = response.json()

        else:
            logger.info(" response not successful, response status code:  {}".format(response.status_code))
            try:
                logger.info(" response body:  \n{}".format(response.json()))
            except:
                logger.info(" no response body")
        #logger.info('list_accounts json: \n{}'.format(json.dumps(response_json, indent=4)))
        return request_successful, response.status_code, response_json

    @logger_wraps()
    def list_licenses(self, sa_domain, virtual_accounts):
        call = "/services/api/smart-accounts-and-licensing/v1/accounts/" + sa_domain + "/licenses"
        uri = ("https://" + self.host + call)

        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.token}
        body = {"limit": 100, "offset": 0, 'virtualAccounts': virtual_accounts}

        #logger.info('list_licenses json body: \n{}'.format(body))

        response = requests.post(uri, headers=headers, data=json.dumps(body), verify=True)

        status_code = response.status_code
        request_successful = False
        response_json = None
        if status_code == 200:
            logger.info("request was successful. status code 200")
            response_json = response.json()
            request_successful = True
        else:
            logger.info(" response not successful, response status code:  {}".format(response.status_code))
            try:
                logger.info(" response body:  \n{}".format(response.json()))
            except:
                logger.info(" no response body")

        #logger.info('list_licenses json: \n{}'.format(json.dumps(response_json, indent=4)))
        return request_successful, status_code, response_json

    @logger_wraps()
    def retrieve_and_process_licenses(self, sa, virtual_account_list):
        account_domain = sa.get("accountDomain")
        # logger.info('account domain:  {}'.format(account_domain))
        # logger.info('virtual_account_list: \n{}'.format(virtual_account_list))

        request_successful, status_code, json_array = self.list_licenses(account_domain, [])

        if request_successful == False:
            logger.info('Failure with list_licenses. status code: {}'.format(status_code))

        else:
            logger.info('Success with list_licenses. status code: {}'.format(status_code))

            domain_licenses = json_array.get("licenses")
            logger.info('list_licenses request_successful: {}\n'.format(request_successful))

            va_dict = {}
            # Sort licenses into lists and  put them into dictionary with key = virtualAccount

            for lic in domain_licenses:
                #      logger.info('license:  {}'.format(lic))
                if lic["virtualAccount"] not in va_dict.keys():
                    #         logger.info('license not in va_dict keys: {}'.format({lic["virtualAccount"]: [lic]}))
                    va_dict.update({lic["virtualAccount"]: [lic]})
                else:
                    va_dict[lic["virtualAccount"]].append(lic)

            for the_virtual_account_key, licenses in va_dict.items():
                logger.info('the_virtual_account_key: {}\n'.format(the_virtual_account_key))
                the_roles = sa.get("roles")
                isFound = False
                for the_role in the_roles:
                    if "virtualAccount" in the_role:
                        if the_virtual_account_key == the_role['virtualAccount']:
                            isFound = True
                            the_role.update({"licenses": licenses})

                if isFound == False:
                    # need to do this because of some of the wonkiness associated with the BU Production Test Domain.
                    the_roles.append({'role': "APPENDED VA USER", \
                                      "virtualAccount": the_virtual_account_key,
                                      "licenses": licenses})

        return request_successful, status_code

    @logger_wraps()
    def list_all_licenses(self):

        empty_virt_account_request_successful = False
        virt_account_request_successful = False
        status_code = -999

        # lazy loading of the licenses
        if self.__all_licenses == None:

            accounts = None

            # Get the list of accounts first
            request_successful, status_code, the_accounts = self.list_accounts()
            logger.info('list accounts request_successful: {}\n'.format(request_successful))

            if request_successful:
                # Getting the accounts was successful  Now loop through and get the virtual accounts

                accounts = the_accounts.get("accounts")
                for sa in accounts:
                    # create list of virtual accounts under Smart Account
                    # first the empty virtual accounts list to try and get everything because some licenses may not
                    # actually be in the virtual accounts.

                    logger.info('Starting getting licenses with virtual accounts set to []')

                    empty_virt_account_request_successful, status_code = self.retrieve_and_process_licenses(sa, [])
                    if empty_virt_account_request_successful:
                        logger.success('Empty virtual accounts\n     successful: {}\n' \
                                       '     status code: {}'.format(empty_virt_account_request_successful, status_code))
                    else:
                        logger.error('Empty virtual accounts\n     successful: {}\n' \
                                       '     status code: {}'.format(empty_virt_account_request_successful,
                                                                     status_code))

                    virtual_account_list = [va.get("virtualAccount") for va in sa.get("roles") if va.get("virtualAccount")]

                    logger.info('Starting getting licenses with virtual accounts set as a list of virtual accounts')

                    # next get the licenses for the virtual accounts
                    if len(virtual_account_list) > 0:
                        logger.info('Virtual Accounts length was greater than zero')
                        virt_account_request_successful, status_code = self.retrieve_and_process_licenses(sa, virtual_account_list)
                        if virt_account_request_successful:
                            logger.success('Full virtual accounts\n     successful: {}\n' \
                                           'status code: {}'.format(virt_account_request_successful, status_code))
                        else:
                            logger.error('Full virtual accounts\n     successful: {}\n' \
                                           'status code: {}'.format(virt_account_request_successful, status_code))


                    else:
                        logger.info('Virtual Accounts length was 0')

                    account_request_success = (empty_virt_account_request_successful or virt_account_request_successful)
                    logger.error('account_request_success: {}, for domain: {}'.format(account_request_success,
                                                                                      sa.get("accountDomain")))



                self.__all_licenses = accounts

        # send back the info including whether or not things were successful.  This way we can provide feedback to the user.
        # Typical reasons for problems have to do with the SSO having to be re-done.  i.e. the token from CSSM needs to be
        # refreshed.  TODO for CSSM to make their token system more like Webex Teams.

        overall_request_successful = (empty_virt_account_request_successful or virt_account_request_successful)
        logger.info("request_successful: {}, status code: {}".format(overall_request_successful, status_code))

        return overall_request_successful, self.__all_licenses


# This function retrieve the CSSM token from the Smart Licensing System Backend.
@logger_wraps()
def retrieve_be_token(be_secret_key, roomId, personId):
    rest_verb = 'GET'

    t = dt.datetime.utcnow()

    the_time = t.strftime('%Y%m%dT%H%M%SZ')

    headers = {'X-SLD-Date': the_time,
               'Content-Type': 'application/json'}

    token_request_url = "{}?roomId={}&personId={}".format(url_base, roomId, personId)

    # Create the signature so that the BE can verify authenticity of our request
    logger.info('{},    generating signature\n'.format(dt.datetime.now()))

    the_signature = WBXTeamsBEIntegration.signature(be_secret_key, headers, rest_verb, token_request_url,
                                                    json.dumps({}), be_service_name)
    logger.info('    signature generated\n')

    headers['X-SLD-BOT-Signature'] = the_signature

    # Send the request
    logger.info('    sending request to BE server\n')
    response = requests.get(token_request_url, json=json.dumps({}), headers=headers)
    logger.info('    received response from BE server\n')

    the_token = ""
    request_successful = False
    response_dict = {}

    if response.status_code == 200:
        # Check the response signature to verify authenticity
        headers = {'X-SLD-Date': response.headers['X-SLD-Date'],
                   'Content-Type': 'application/json'}

        response_signature = response.headers['X-SLD-BE-Signature']
        response_json = None
        try:
            response_json = json.dumps(response.json())
        except:
            logger.info(" no response body")

        calculated_response_signature = WBXTeamsBEIntegration.signature(be_secret_key, headers,
                                                                 'Response',
                                                                 "",
                                                                 response_json,'X-SLD-BE-Service')

        if response_signature == calculated_response_signature:
            logger.success('Response signature authenticated')
            request_successful = True
            response_dict = json.loads(response.text)
            the_token = response_dict['access_token']
        else:
            logger.error('Response NOT signature authenticated')


    return request_successful, response.status_code, the_token


# We are caching the license information for a few minutes so that response time to the user is faster.
@logger_wraps()
@cached(license_cache)
def get_cssm_license(room_id, bot_token, account_credentials=""):

    # Provide feedback to the user that fetching the info will take some time.
    please_wait_message = "Retrieving info from the Cisco Smart Software Manager.  This might take some time."
    x = threading.Thread(target=send_processing_status_message, args=(room_id, bot_token, please_wait_message))
    x.start()

    cssm_license = None
    request_successful = False

    # Retrieve the licenses
    smart_account = SmartAccountSDK(cssm_url, account_credentials)

    logger.info('entering smart_account.list_all_licenses()')
    request_successful, json_array = smart_account.list_all_licenses()

    logger.info('have exited smart_account.list_all_licenses()')
    logger.info('request_successful: {}\n'.format(request_successful))

    if request_successful:
        # Retrieving the licenses from CSSM was successful.  Update the user and parse the info into a CSSMLicense object
        retrieved_all_info_message = "Retrieved all the info from the CSSM Server, just a bit more time to get your request."
        send_processing_status_message(room_id, bot_token, retrieved_all_info_message)

        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()


    logger.info('request_successful: {}\n, cssm_license: {}\n'.format(request_successful, cssm_license))

    return request_successful, cssm_license

# Generic function to provide status messages.
@logger_wraps()
def send_processing_status_message(room_id, bot_token, status_message):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': status_message}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting send_please_wait was successful")
    else:
        logger.info("posting send_please_wait not successful.  Status code: {}".format(
            request_response_results[1]["error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


# Creates the status message from a CSSMLicense object
# The status message provides a brief summary so we limit things to the top x items.  Whereas the normal commands
# will provide more verbose output.
#
# Since we are have all the info in the CSSMLicense Object, this goes pretty quickly
@logger_wraps()
def create_license_status_message(cssm_license):
    accounts_dict = cssm_license.cssm_expired_licenses()

    # logger.info(" accounts: dict = ")

    msg = "**Here is the high level status of your licensing**:\n"

    # Top five expired licenses first.
    expired_dict = cssm_license.cssm_top_five_expired_licenses()

    if expired_dict==None:
        expired_dict={}
    if len(expired_dict) > 0:
        msg = msg + '* [Top 5 Expired Licenses]({} "Expired License Link")\n'.format(be_login_url)

        for accountName, virtualAccounts in expired_dict.items():
            msg = msg + '    * **{}**\n'.format(accountName)

            for virtualAccount_name, licenses_dict in virtualAccounts.items():
                msg = msg + '        * {}\n'.format(virtualAccount_name)

                for license_name, license_dict in licenses_dict.items():
                    msg = msg + '            * {}, Qty: {}, Expired: {}\n'.format(license_name,
                                                                                  license_dict['quantity'],
                                                                                  license_dict['endDate'])

    else:
        msg = msg + '* [There were no expired licenses]({} "Expired License Link")!\n'.format(be_login_url)

    # Top Five Future Expiring licenses

    future_expired_licenses = cssm_license.cssm_top_five_future_expired_licenses(expiration_days=180)
    if future_expired_licenses==None:
        future_expired_licenses={}
    logger.info('keys future_expired_licenses: {}'.format(future_expired_licenses.keys()))
    expired_dict = future_expired_licenses['future_expired_licenses']
    if len(expired_dict) > 0:
        msg = msg + '* [Top 5 Licenses Expiring in the Next 180 Days]({} "Future Expired License Link")\n'.format(
            be_login_url)

        for accountName, virtualAccounts in expired_dict.items():
            msg = msg + '    * **{}**\n'.format(accountName)

            for virtualAccount_name, licenses_dict in virtualAccounts.items():
                msg = msg + '        * {}\n'.format(virtualAccount_name)

                for license_name, license_details_list in licenses_dict.items():
                    if len(license_details_list) == 1:
                        license_detail = license_details_list[0]
                        msg = msg + '            * **{}**, Qty: {} expire on: {}\n'.format(license_name,
                                                                                           license_detail['quantity'],
                                                                                           license_detail['endDate'])

                    else:

                        msg = msg + '            * **{}**\n'.format(license_name)

                        for license_detail in license_details_list:
                            msg = msg + '                * Qty: {}, Expiring: {}\n'.format(license_detail['quantity'],
                                                                                           license_detail['endDate'])

    else:
        msg = msg + '* [There are no licenses that expire in the next 180 days]({} "Future Expired License Link")!\n'.format(
            be_login_url)

    # Top five license shortages.
    shortage_dict = cssm_license.cssm_license_top_five_shortage()
    if shortage_dict == None:
        shortage_dict={}

    if len(shortage_dict) > 0:
        msg = msg + '* [Top 5 License Shortages]({} "License Shortage Link")\n'.format(be_login_url)

        for accountName, virtualAccounts_dict in shortage_dict.items():
            logger.info('accountName: {}'.format(accountName))
            logger.info('shortage_virtualAccounts_dict: {}'.format(virtualAccounts_dict))
            msg = msg + '    * **{}**\n'.format(accountName)

            for virtualAccount_name, licenses_list in virtualAccounts_dict.items():
                msg = msg + '        * {}\n'.format(virtualAccount_name)
                logger.info('licenses_list: {}'.format(licenses_list))
                for license_dict in licenses_list:
                    logger.info('license_dict: {}'.format(license_dict))
                    msg = msg + '            * {}, has a shortage of {} licenses\n'.format(license_dict['license'],
                                                                                           license_dict['shortage'])

    else:
        msg = msg + '* [License Shortage: There are no license shortages]({} "License Shortage Link")\n'.format(be_login_url)

    # Top five licenses by usage
    usage_dict = cssm_license.cssm_top_license_usage_dict()
    if usage_dict==None:
        usage_dict={}
    if len(usage_dict) > 0:
        msg = msg + '* [Top 5 Licenses By Consumption]({} "License Consumption Link")\n'.format(be_login_url)
        for accountName, virtualAccounts_dict in usage_dict.items():
            logger.info('accountName: {}'.format(accountName))
            logger.info('shortage_virtualAccounts_dict: {}'.format(virtualAccounts_dict))
            msg = msg + '    * **{}**\n'.format(accountName)

            for virtualAccount_name, licenses_dict in virtualAccounts_dict.items():
                msg = msg + '        * {}\n'.format(virtualAccount_name)
                logger.info('licenses_list: {}'.format(licenses_dict))
                for license_name, license_dict in licenses_dict.items():
                    logger.info('license_dict: {}'.format(license_dict))
                    msg = msg + '            * {}, has {:.1f}% utilization\n'.format(license_name,
                                                                                           license_dict['usage'])

    else:
        msg = msg + '* [License Usage: There are no licenses in use right now]({} "License Consumption Link")\n'.format(be_login_url)


    # Architecture mix summary.
    technology_dict = cssm_license.cssm_top_license_technology_dict()
    if technology_dict==None:
        technology_dict={}
    if len(technology_dict) > 0:
        logger.info('technology_dict: {}'.format(technology_dict))
        msg = msg + '* [Here is your architecture mix, by Account]({} "License Architecture Mix Link")\n'.format(be_login_url)
        for accountName, architecture_dict in technology_dict.items():
            logger.info('accountName: {}'.format(accountName))
            msg = msg + '    * **{}**\n'.format(accountName)

            for architecture_name, usage_info in architecture_dict.items():
                msg = msg + '        * {}: {:.1f}%\n'.format(architecture_name, usage_info['inUse'])

    else:
        msg = msg + '* [License Architecture Mix: There are no licenses in use right now]({} "License Architecture Mix Link")\n'.format(be_login_url)

    return msg


@logger_wraps()
def prepare_license_status_message(room_id, bot_token, account_credentials=""):
    request_successful = False
    cssm_license = None

    if ARE_DEBUGGING:
        #For testing only until we can pull data from another source

        with open(file_name) as json_data:
            json_array = json.load(json_data)

        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True

    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_license_status_message(cssm_license)

    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving the license shortage information.  Click [here]({}) to log back in.**".format(
            be_login_url)


# Function called by smartdashpullbot to send an overall status.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_license_status_update(room_id, bot_token, account_credentials):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_license_status_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('     got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting license_shortage was successful")
    else:
        logger.info("posting license_shortage not successful.  Status code: {}".format(request_response_results[1][
                                                                                           "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


@logger_wraps()
def create_license_shortages_message(cssm_license):
    accounts_dict = cssm_license.cssm_license_shortage()

    msg = "**There are no licenses shortages!!**"

    if len(accounts_dict) > 0:

        msg = "**Here is a list of licenses with shortages, grouped by Account and Virtual Account**:\n"
        for account_key in accounts_dict.keys():
            virtual_accounts = accounts_dict[account_key]
            msg = msg + "* **{}**\n".format(account_key)

            if len(virtual_accounts) > 0:
                for virtual_account_key in virtual_accounts.keys():
                    msg = msg + "    * {}\n".format(virtual_account_key)
                    licenses = virtual_accounts[virtual_account_key]

                    if len(licenses) > 0:
                        for license in licenses:
                            msg = msg + "        * There is a shortage of **{}** licenses for \"**{}**\"\n" \
                                .format(license['inUse'] - license['quantity'], license['license'])

    return msg


@logger_wraps()
def prepare_license_shortage_message(room_id, bot_token, account_credentials=""):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_license_shortages_message(cssm_license)
    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving the license shortage information.  Click [here]({}) to log back in.**".format(
            be_login_url)


# Function called by smartdashpullbot to send information on license shortages.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_license_shortage(room_id, bot_token, account_credentials):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_license_shortage_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('     got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting license_shortage was successful")
    else:
        logger.info("posting license_shortage not successful.  Status code: {}".format(request_response_results[1][
                                                                                           "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))

# This function creates the message for license usage.  It decides, based upon how many licenses, whether or not to
# truncate the message and notify the calling function about whether or not they need to send an excel file to that they
# get all the information.
@logger_wraps()
def create_license_usage_message(cssm_license):

    msg = "**There are no licenses being used!**"

    usage_info_dict = cssm_license.cssm_license_usage_dict()

    limit = 0

    should_export_as_excel = False

    if len(usage_info_dict) > 0:
        usage_size = usage_info_dict['dict_size']
        usage_dict = usage_info_dict['usage_dict']
        if usage_size > 9:
            should_export_as_excel = True
            msg = '**There are a large number of licenses.  Here is the license usage for the top 10 by account and virtual account**:\n'
        else:
            msg = '**Here is the license usage by account and virtual account**: \n'

        for accountName, virtualAccounts_dict in usage_dict.items():
            msg = msg + '* **{}**\n'.format(accountName)

            for virtualAccount_name, licenses_dict in virtualAccounts_dict.items():
                msg = msg + '    * {}\n'.format(virtualAccount_name)

                for license_name, license_dict in licenses_dict.items():

                    msg = msg + '        * {}, has {:.1f}% utilization\n'.format(license_name,
                                                                                     license_dict['usage'])
                    limit = limit +1
                    if limit==10:
                        msg = msg + '\nWill export all the licenses usage info to an excel file.\n'
                        break
                if limit==10:
                    break
            if limit == 10:
                break

    return msg, should_export_as_excel


@logger_wraps()
def prepare_license_usage_message(room_id, bot_token, account_credentials=""):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open('./usage_test_large.json') as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    should_export_as_excel = False

    if request_successful:
        logger.info('done getting list of licenses')
        msg, should_export_as_excel = create_license_usage_message(cssm_license)
        return msg, should_export_as_excel
    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving license usage information. Click [here]({}) to log back in.**".format(
            be_login_url), should_export_as_excel

# This function creates an in memory excel file that can be packaged up into a message to Webex Teams.
@logger_wraps()
def license_usage_excel_writer(cssm_df=None):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter', options={'remove_timezone': True})
    columns = ['accountName', 'virtualAccount', 'license', 'inUse', 'assignedLicenses_quantity','usage']

    cssm_df.to_excel(writer, sheet_name="Licenses", startcol=0, startrow=0, columns=columns)
    writer.save()

    return output.getvalue()

# Function called by smartdashpullbot to send license usage info.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_license_usage(room_id, bot_token, account_credentials):
    post_url = "https://api.ciscospark.com/v1/messages"

    msg, should_export_as_excel = prepare_license_usage_message(room_id, bot_token, account_credentials)

    post_data = {'roomId': room_id,
                 'markdown': msg}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    request_response_results = None

    # send an excel based report in case there were too many licenses to display on Teams.
    if should_export_as_excel:
        request_successful = False
        cssm_license = None
        if ARE_DEBUGGING:
            # For testing only until we can pull data from another source
            with open('./usage_test_large.json') as json_data:
                json_array = json.load(json_data)
            parser = cssm_parser.CSSMJSONParser(json_array)
            cssm_license = parser.cssm_license()
            request_successful = True
        else:
            request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)


        if request_successful:
            logger.info('getting the licenses was successful')
            excel_output = license_usage_excel_writer(cssm_license.cssm_license_usage_df())

            filetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            my_fields1 = {'roomId': room_id,
                          'files': ('license_usage_export.xlsx', excel_output, filetype)}


            message_data = MultipartEncoder(fields=my_fields1)

            logger.info('starting post')
            request_response_results = post_request(post_url,
                                                    post_headers={"Accept": "application/json",
                                                                  "Content-Type": message_data.content_type,
                                                                  "Authorization": "Bearer {}".format(bot_token)},
                                                    post_data=message_data)

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting license usage info was successful")
    else:
        logger.info("posting license usage not successful.  Status code: {}".format(request_response_results[1][
                                                                                             "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))

def create_license_architecture_mix_message(cssm_license):
    msg = "**There are no licenses being used.  No architecture mix available!**"

    tech_info_dict = cssm_license.cssm_top_license_technology_dict()


    if len(tech_info_dict) > 0:

        msg = '**Here is the architecture mix, by account**: \n'

        for accountName, architecture_dict in tech_info_dict.items():
            msg = msg + '* **{}**\n'.format(accountName)

            for architecture_name, usage_dict in architecture_dict.items():
                msg = msg + '    * {}: {:.1f}%\n'.format(architecture_name, usage_dict['inUse'])

    return msg


@logger_wraps()
def prepare_license_architecture_mix_message(room_id, bot_token, account_credentials="", expiration_days=30):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_license_architecture_mix_message(cssm_license)
    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving architecture mix information. Click [here]({}) to log back in.**".format(
            be_login_url)

# Function called by smartdashpullbot to send architecture mix info.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_license_architecture_mix(room_id, bot_token, account_credentials):

    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id,
                 'markdown': prepare_license_architecture_mix_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting send_license_architecture_mix info was successful")
    else:
        logger.info("posting send_license_architecture_mix not successful.  Status code: {}".format(request_response_results[1][
                                                                                             "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))



@logger_wraps()
def create_future_expired_licenses_message(cssm_license, expiration_days=30):
    expired_license_dict = cssm_license.cssm_future_expired_licenses(expiration_days=expiration_days)

    msg = "**There are no licenses that expire in {} days!!**"

    accounts_dict = expired_license_dict['future_expired_licenses']
    if len(accounts_dict) > 0:

        license_quantity = expired_license_dict['quantity']

        if license_quantity == 1:
            msg = "**There is _*{}*_ license".format(license_quantity)
        else:
            msg = "**There are _*{}*_ licenses".format(license_quantity)

        msg = msg + " that will expire in {} days:**:\n".format(expiration_days)

        for account_key, virtual_accounts in accounts_dict.items():

            msg = msg + "* **{}**\n".format(account_key)

            if len(virtual_accounts) > 0:
                for virtual_account_key, licenses in virtual_accounts.items():
                    msg = msg + "    * {}\n".format(virtual_account_key)

                    for license_key, license_details in licenses.items():
                        if len(license_details) == 1:
                            the_detail = license_details[0]
                            msg = msg + "        * **{}**, Qty: {} expire on: {}\n".format(license_key,
                                                                                           the_detail['quantity'],
                                                                                           the_detail['endDate'])
                        else:
                            msg = msg + "        * **{}**\n".format(license_key)
                            for license_detail in license_details:
                                msg = msg + "            * Qty: {} expire on: {}\n".format(license_detail['quantity'],
                                                                                           license_detail['endDate'])

    return msg.format(expiration_days)

@logger_wraps()
def prepare_future_expired_licenses_message(room_id, bot_token, account_credentials="", expiration_days=30):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_future_expired_licenses_message(cssm_license, expiration_days=expiration_days)
    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving expired licenses information. Click [here]({}) to log back in.**".format(
            be_login_url)

# Function called by smartdashpullbot to send information about licenses that will expire in X number of days info.
# This function calls on the prepare and create functions above to get the message to package up and send to webex
# teams in response to a request.
@logger_wraps()
def send_future_expired_licenses(room_id, bot_token, account_credentials, expiration_days=30):
    logger.info('send_thirty_expired_licenses start')

    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_future_expired_licenses_message(room_id, bot_token, account_credentials,
                                                                                        expiration_days=expiration_days)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting license expiration info was successful")
    else:
        logger.info("posting license expiration not successful.  Status code: {}".format(request_response_results[1][
                                                                                             "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


@logger_wraps()
def create_expired_licenses_message(cssm_license):
    accounts_dict = cssm_license.cssm_expired_licenses()
    logger.info(accounts_dict)
    msg = "**There are no expired licenses!!**"

    if len(accounts_dict) > 0:

        msg = "**Here are the *expired licenses*, grouped by Account and Virtual Account**:\n"
        for account_key in accounts_dict.keys():
            virtual_accounts = accounts_dict[account_key]
            msg = msg + "* **{}**\n".format(account_key)

            if len(virtual_accounts) > 0:
                for virtual_account_key in virtual_accounts.keys():
                    msg = msg + "    * {}\n".format(virtual_account_key)
                    licenses = virtual_accounts[virtual_account_key]

                    if len(licenses) > 0:
                        for license_name, license_info in licenses.items():
                            end_date = license_info['endDate']
                            msg = msg + "        * {}, Qty: {}, expires: {}\n".format(license_name,
                                                                                      license_info['quantity'],
                                                                                      end_date)

    return msg


@logger_wraps()
def prepare_expired_licenses_message(room_id, bot_token, account_credentials=""):
    # For testing only until we can pull data from another source
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_expired_licenses_message(cssm_license)
    else:
        logger.info('issue with generating the license')
        return "**There was a problem retrieving expired licenses information. Click [here]({}) to log back in.**".format(
            be_login_url)

# Function called by smartdashpullbot to send expired license info.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_expired_licenses(room_id, bot_token, account_credentials):
    logger.info('send_expired_licenses start')

    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_expired_licenses_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting account_names was successful")
    else:
        logger.info("posting account_names not successful.  Status code: {}".format(request_response_results[1][
                                                                                        "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))

# in memory excel writer.  This could be refactored with the other excel writer function above.
@logger_wraps()
def license_excel_writer(cssm_df=None):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter', options={'remove_timezone': True})
    columns = ['accountName', 'accountDomain', 'accountStatus', 'accountType', 'role', 'virtualAccount',
               'virtualAccount_status', 'statusMessage', 'license', 'assignedLicenses_quantity', 'inUse', 'available',
               'ahaApps', 'billingType', 'pendingQuantity', 'reserved', 'isPortable', 'assignedLicenses_status',
               'licenseType', 'quantity', 'startDate', 'endDate', 'subscriptionId', 'status']

    cssm_df.to_excel(writer, sheet_name="Licenses", startcol=0, startrow=0, columns=columns)
    writer.save()

    return output.getvalue()

# Function called by smartdashpullbot to send an export of all the license info.  This function calls on the prepare
# and create functions above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_license_export(room_id, bot_token, account_credentials):

    post_url = "https://api.ciscospark.com/v1/messages"

    my_fields1 = {'roomId': room_id}

    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)


    request_response_results = None
    if request_successful:
        logger.info('getting the licenses was successful')
        excel_output = license_excel_writer(cssm_license.cssm_dataframe)
        msg = '**Here is the license export that you requested!**'

        filetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        my_fields1['files'] = ('license_export.xlsx', excel_output, filetype)
        my_fields1['markdown'] = msg

        message_data = MultipartEncoder(fields=my_fields1)

        logger.info('starting post')
        request_response_results = post_request(post_url,
                                                post_headers={"Accept": "application/json",
                                                              "Content-Type": message_data.content_type,
                                                              "Authorization": "Bearer {}".format(bot_token)},
                                                post_data=message_data)
    else:
        my_fields1['markdown'] = "**There was a problem pulling the info for your license export request. " \
                                 "Click [here]({}) to log back in.**".format(be_login_url)
        request_response_results = post_request(post_url,
                                                post_headers={"Accept": "application/json",
                                                              "Content-Type": "application/json",
                                                              "Authorization": "Bearer {}".format(bot_token)},
                                                post_json=my_fields1)

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting account_names was successful")
    else:
        logger.info("posting account_names not successful.  Status code: {}".format(request_response_results[1][
                                                                                        "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


@logger_wraps()
def create_virtual_accounts_message(cssm_license):
    accounts_dict = cssm_license.cssm_virt_account_by_accountName()

    msg = "**Here are the *virtual accounts*, grouped by Account**:\n"
    for account in accounts_dict.keys():
        msg = msg + "* **{}**\n".format(account)
        for virtual_account in accounts_dict[account]:
            msg = msg + "    * {}\n".format(virtual_account)

    return msg


@logger_wraps()
def prepare_virtual_accounts_message(room_id, bot_token, account_credentials=""):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        return create_virtual_accounts_message(cssm_license)
    else:
        return "**There was a problem retrieving the virtual accounts information.  Click [here]({}) to log back in.**".format(
            be_login_url)

# Function called by smartdashpullbot to send virtual accounts info.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_virtual_accounts(room_id, bot_token, account_credentials):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_virtual_accounts_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting account_names was successful")
    else:
        logger.info("posting account_names not successful.  Status code: {}".format(request_response_results[1][
                                                                                        "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


@logger_wraps()
def create_account_names_message(cssm_license):
    logger.info('create_account_names_message start')

    account_names = cssm_license.account_names()
    logger.info('done retrieving account names')

    msg = "Sorry, there aren't any accounts for your credentials!"
    if len(account_names) > 0:
        msg = "**Here are the requested accounts:**\n\n"
        for name in account_names:
            msg = msg + '* {}\n'.format(name)
    logger.info('create_account_names_message end')
    return msg


@logger_wraps()
def prepare_account_names_message(room_id, bot_token, account_credentials=""):
    request_successful = False
    cssm_license = None
    if ARE_DEBUGGING:
        # For testing only until we can pull data from another source
        with open(file_name) as json_data:
            json_array = json.load(json_data)
        parser = cssm_parser.CSSMJSONParser(json_array)
        cssm_license = parser.cssm_license()
        request_successful = True
    else:
        request_successful, cssm_license = get_cssm_license(room_id, bot_token, account_credentials)

    if request_successful:
        logger.info('done getting list of licenses')
        #   print('{},    the json_array:  {}'.format(json_array))
        logger.info('{}, prepare_account_names_message end'.format(dt.datetime.now()))
        return create_account_names_message(cssm_license)
    else:
        logger.info('could not get list of licenses')
        return "**There was a problem retrieving the account names information. Click [here]({}) to log back in.**".format(
            be_login_url)

# Function called by smartdashpullbot to send smart account info.  This function calls on the prepare and create functions
# above to get the message to package up and send to webex teams in response to a request.
@logger_wraps()
def send_account_names(room_id, bot_token, account_credentials):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_account_names_message(room_id, bot_token, account_credentials)}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting account_names was successful")
    else:
        logger.info("posting account_names not successful.  Status code: {}".format(request_response_results[1][
                                                                                        "error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))

# Pretty self explanatory.  Put together the message for when a user types hello or help.
@logger_wraps()
def prepare_hello_message():
    msg = '**Howdy, this is the Cisco Smart Licensing Dashboard Bot.  What can I do for you?**\n\nThese are the things you can do:\n'
    msg = msg + '* \'show me the latest status\' or \'status\' or \'give me a status update\'\n' \
                '* **Account Related:**\n' \
                '    * \'give me a list of account names\'\n' \
                '    * \'give me a list of virtual accounts\'\n' \
                '* **Licensing:**\n' \
                '    * \'give me an export of licenses\' or \'export licenses\'\n' \
                '    * \'show me license usage\' or \'license usage\' or \'usage\'\n' \
                '    * \'show me the architecture mix\' or \'architecture mix\'\n' \
                '* **Licensing Issues:**\n' \
                '    * **Expired Licenses Info**\n' \
                '        * \'give me a list of expired licenses\' or \'expired licenses\'\n' \
                '        * \'show me licenses that expire in 30 days\' or \'expire 30 days\' or \'expire 30\'\n' \
                '        * \'show me licenses that expire in 60 days\' or \'expire 60 days\' or \'expire 60\'\n' \
                '        * \'show me licenses that expire in 90 days\' or \'expire 90 days\' or \'expire 90\'\n' \
                '        * \'show me licenses that expire in 180 days\' or \'expire 180 days\' or \'expire 180\'\n' \
                '    * \'show me licenses with shortages\' or \'license shortage list\'\n'
    return msg

# send a message to the user that authentication failed.
@logger_wraps()
def send_authentication_back(room_id, bot_token):
    post_url = "https://api.ciscospark.com/v1/messages"

    msg = "**There was a problem retrieving the account names information. Click [here]({}) to log back in.**".format(be_login_url)

    post_data = {'roomId': room_id, 'markdown': msg}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting problem back was successful")
    else:
        logger.info("posting problem back not successful.  Status code: {}".format(
            request_response_results[1]["error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


# Sent to the user when we don't understand what they were asking for.
@logger_wraps()
def send_problem_back(room_id, bot_token):
    post_url = "https://api.ciscospark.com/v1/messages"

    msg = 'Hi, sorry I did not understand your request.  Try typing \'help\' to get a list of commands.'

    post_data = {'roomId': room_id, 'markdown': msg}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting problem back was successful")
    else:
        logger.info("posting problem back not successful.  Status code: {}".format(
            request_response_results[1]["error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))


@logger_wraps()
def send_hello_back(room_id, bot_token):
    post_url = "https://api.ciscospark.com/v1/messages"

    post_data = {'roomId': room_id, 'markdown': prepare_hello_message()}

    logger.info('starting post')
    request_response_results = post_request(post_url,
                                            post_headers={"Accept": "application/json",
                                                          "Content-Type": "application/json",
                                                          "Authorization": "Bearer {}".format(bot_token)},
                                            post_json=post_data)
    logger.info('got response from post')

    request_response_is_successful = request_response_results[0]
    date_time = dt.datetime.now()
    if request_response_is_successful:
        logger.info("posting hello back was successful")
    else:
        logger.info("posting hello back not successful.  Status code: {}".format(
            request_response_results[1]["error_key"]))
        logger.info("response from server: {}".format(request_response_results[1]["response_json_key"]))

# Basic function that does the heavy lifting of sending messages and files to Webex Teams.
@logger_wraps()
def post_request(url, post_headers, post_data=None, post_json=None):
    spark_request = None
    if post_data:
        spark_request = requests.post(url,
                                      data=post_data,
                                      headers=post_headers)
    elif json:
        spark_request = requests.post(url, json=post_json, headers=post_headers)
    else:
        return [False, {"error_key": "No json or data payload"}]

    if spark_request.status_code == 200:
        return [True, {}]
    else:
        return [False, {"error_key": spark_request.status_code,
                        "response_json_key": json.loads(spark_request.text)}]
