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

import threading
import requests
import json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging
import functools
from loguru import logger

#The below code enables advanced http debugging, which is currently useful to debugging integration issues.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class token_mgr:
    def __init__(self, client_id, client_secret, token_rt, redirect_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_rt = token_rt
        self.redirect_url = redirect_url
        #self.__refresh_token()

    def get_token(self):
        return self.token

    def new_token(self, code):
        params = {"code": code,"client_id":self.client_id, "client_secret": self.client_secret, "redirect_uri": self.redirect_url, "grant_type": "authorization_code"}
        #uri = ("https://cloudsso.cisco.com/as/token.oauth2?grant_type=authorization_code&code="+code + "&client_id=" + self.client_id)
        uri = ("https://cloudsso.cisco.com/as/token.oauth2")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(uri, data=params, headers=headers, verify=True)
        print(params)
        print(response.text)
        print(json.dumps(response.json(), indent=4))
        return response.json()
   
   #curl -X POST -H "Authorization: Bearer LNNcQPS2Nl1vrNzSDkypEqMvTBlf" https://cloudsso.cisco.com/idp/userinfo.openid
    def fetch_email(self, access_token):
        uri = ("https://cloudsso.cisco.com/idp/userinfo.openid")
        headers = {"Authorization": "Bearer " + access_token}
        response = requests.post(uri, headers=headers, verify=True)
        print(response.text)
        print(json.dumps(response.json(), indent=4))
        return response.json()
    

    def new_token_client_grant(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        reply = oauth.fetch_token(token_url='https://cloudsso.cisco.com/as/token.oauth2', client_id=self.client_id,
                                  client_secret=self.client_secret)
        return reply.get("access_token")

    def __refresh_token(self):
        """ Recursive thread runs in background and refreshes the client token after token_rt (in seconds)
        """
        self.token = self.new_token()
        threading.Timer(self.token_rt, self.__refresh_token).start()

def logger_wraps(entry=True, exit=True, level="DEBUG"):
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



class SmartAccountSDK:
    @logger_wraps()
    def __init__(self, host, token):

        self.host = host
        self.token = token
        self.__all_licenses = None

    @logger_wraps()
    def list_accounts(self):
        """ returns all accounts assocaited with a user"""
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
            logger.info(" response not successful, response status code:  {}".format(response.status_code))
            try:
                logger.info(" response body:  \n{}".format(response.json()))
            except:
                logger.info(" no response body")
        logger.info('list_accounts json: \n{}'.format(json.dumps(response_json, indent=4)))
        return request_successful, response.status_code, response_json

    @logger_wraps()
    def list_licenses(self, sa_domain, virtual_accounts):
        call = "/services/api/smart-accounts-and-licensing/v1/accounts/" + sa_domain + "/licenses"
        uri = ("https://" + self.host + call)

        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.token}
        body = {"limit": 100, "offset": 0, 'virtualAccounts': virtual_accounts}
        # if len(virtual_accounts) > 0:
        #     body['virtualAccounts'] = (virtual_accounts)

        #logger.info('list_licenses json body: \n{}'.format(body))

        response = requests.post(uri, headers=headers, data=json.dumps(body), verify=True)

        logger.info(" response status code:  {}".format(response.status_code))

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
        logger.info('account domain:  {}'.format(account_domain))
        logger.info('virtual_account_list: \n{}'.format(virtual_account_list))

        request_successful, status_code, json_array = self.list_licenses(account_domain, [])

        if request_successful == False:
            logger.info('Failure with list_licenses. status code: {}'.format(status_code))
            logger.info('account domain: {}\nvirtual_account_list: {}'.format(account_domain, []))
        else:
            logger.info('Success with list_licenses. status code: {}'.format(status_code))

            domain_licenses = json_array.get("licenses")
            logger.info('list_licenses request_successful: {}\n'.format(request_successful))
            #   logger.info('size of domain_licenses: {}\n'.format(len(domain_licenses)))

            va_dict = {}
            # Sort licenses into lists and  put them into dictionary with key = virtualAccount
            for lic in domain_licenses:
                #      logger.info('license:  {}'.format(lic))
                if lic["virtualAccount"] not in va_dict.keys():
                    #         logger.info('license not in va_dict keys: {}'.format({lic["virtualAccount"]: [lic]}))
                    va_dict.update({lic["virtualAccount"]: [lic]})
                else:
                    va_dict[lic["virtualAccount"]].append(lic)

            # logger.info('va_dict:  {}'.format(va_dict))
            # append each list of accounts associated with virtual account under that sa/va in accounts
            # for va in sa.get("roles"):
            #     if va.get("virtualAccount") in va_dict.keys():
            #         va.update({"licenses": va_dict[va.get("virtualAccount")]})
            #     else:
            #         va.update({"licenses": []})

            logger.info('starting new part of parser')
            for the_virtual_account_key, licenses in va_dict.items():
                logger.info('the_virtual_account_key: {}\n'.format(the_virtual_account_key))
                the_roles = sa.get("roles")
                isFound = False
                for the_role in the_roles:
                    if "virtualAccount" in the_role:
                        if the_virtual_account_key == the_role['virtualAccount']:
                            logger.info('found: {}'.format(the_virtual_account_key))
                            isFound = True
                            the_role.update({"licenses": licenses})

                if isFound == False:
                    the_roles.append({'role': "APPENDED VA USER", \
                                      "virtualAccount": the_virtual_account_key,
                                      "licenses": licenses})

        return request_successful, status_code

    @logger_wraps()
    def list_all_licenses(self):

        empty_virt_account_request_successful = False
        virt_account_request_successful = False
        status_code = -999
        if self.__all_licenses == None:

            accounts = None
            request_successful, status_code, the_accounts = self.list_accounts()
            logger.info('list accounts request_successful: {}\n'.format(request_successful))

            if request_successful:
                accounts = the_accounts.get("accounts")
                for sa in accounts:
                    # create list of virtual accounts under Smart Account
                    is_empty_virt_account_pass = True

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

                    logger.info('Starting getting licenses with virtual accounts set actual virtual accounts')
                    logger.error('  virtual_account_list: {}'.format(virtual_account_list))
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

        overall_request_successful = (empty_virt_account_request_successful or virt_account_request_successful)
        logger.info("request_successful: {}, status code: {}".format(overall_request_successful, status_code))

        return overall_request_successful, self.__all_licenses



