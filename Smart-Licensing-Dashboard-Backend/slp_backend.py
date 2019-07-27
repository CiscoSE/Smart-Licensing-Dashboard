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

from sa_sdk import SmartAccountSDK, token_mgr
import CSSMJSONParser as cssm_parser
import connexion
import json
import hmac
import hashlib
import datetime as dt
from dateutil import parser
from WBXTeamsBEIntegration import WBXTeamsBEIntegration
import connexion
from flask import Flask, request, send_from_directory, redirect, url_for, jsonify
import os
from loguru import logger
import threading
import time
import redis

from WBXTeamsMeetingRoom import WBXTeamsMeetingRoom as wbx_meeting_room

# Program variables
token_rt = 3500  # How often the access token should be refreshed in seconds

# Instantiate Token Manager
client_id = os.environ.get("CSSM_CLIENT_ID")
client_secret = os.environ.get("CSSM_CLIENT_SECRET")
redirect_url = os.environ.get("CSSM_REDIRECT_URL")
token_mgr = token_mgr(client_id, client_secret, token_rt, redirect_url)
#csc = sa_sdk.SmartAccountSDK(sa_server, token)
#This is temporarily commented out. I think we still want to user a different oauth grant for local api testing, so we need to revisit this.

redis_db = redis.Redis()

tokens = {}
teams_ids = {}
session_ids = {}
license_cache = {}
license_cache_lock = {}

# For WebexTeams Bot integration, set the secret key in your environment.  Uncomment out the following once this is done.
sld_bot_key = os.environ.get('SLD_SMART_BOT_SECRET_KEY')
# Comment this out once the secret key is set in your environment
#sld_bot_key = ''

# Instantiate Token Manager
#token = sa_sdk.token_mgr(client_id, client_secret, token_rt)
#csc = sa_sdk.SmartAccountSDK(sa_server, token)

#license_info_all = csc.list_all_licenses()


def read():
    return csc.list_all_licenses()

def get_access_token(roomId, personId):

    # Function called by connexion when request with userinfo/access-token is received

    # Get the request
    request = connexion.request

    # Create a WBXTeamsBEIntegrtion object.  This will help you validate the request.
    be_integration = WBXTeamsBEIntegration.WBXTeamsBEIntegration(sld_bot_key,
                                                                 'a token',
                                                                 request,
                                                                 'SLD-WebexTeams-Bot-Service')

    return_json = {}
    return_status_code = -99
    return_headers = {}

    # Verify the signature
    signature_verified = be_integration.signatureIsValid('X-SLD-BOT-Signature')
    if signature_verified == False:
        # if the request signature is bad, respond with a 401
        return_json = {}
        return_status_code = 401
    else:
        # If the signature is valid, check for the token

        # Get the access token here.  Use the roomId and personId to look it up.  If the lookup is successful package
        # up the token in json and set the status_code to 200.
        #
        # if the lookup is unsuccessful, set the return_json to {} and status_code to 404.
        #
        # here is some sample code
        lookup_successful, the_access_token = getAccessTokenByIds(personId, roomId)
        print (lookup_successful)
        print (the_access_token)
        if lookup_successful:
            return_json = {'access_token': the_access_token}
            return_status_code = 200
        else:
            return_json = {}
            return_status_code = 404
    # Construct the response.  Start with the headers
    t = dt.datetime.utcnow()
    the_time = t.strftime('%Y%m%dT%H%M%SZ')

    headers = {'X-SLD-Date': the_time,
              'Content-Type': 'application/json'}

    # Generate the signature
    response_signature = WBXTeamsBEIntegration.signature(sld_bot_key, headers, 'Response', "", return_json, 'X-SLD-BE-Service')

    # Add the signature to the headers
    headers['X-SLD-BE-Signature'] = response_signature

    print(return_json)

    # return the json, status code, and headers
    return return_json, return_status_code, headers

def getAccessTokenByIds(personId, roomId):
    #print (teams_ids)
    #room_dict = teams_ids.get(personId, None)
    #print (room_dict)
    #if room_dict is None:
    #    return False, ''
    #email = room_dict.get(roomId, None)
    #print ("email")
    #print (email)
    email = redis_db.get("teams_"+personId+roomId)
    if email is None:
        return False, ''
    #return True, tokens[email].get("access_token")
    return True, redis_db.get("token_" + email.decode()).decode()

# Create the application instance
app = connexion.App(__name__, specification_dir='./')


# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yaml', validate_responses=True)


@app.route('/')
def home():
    return send_from_directory('./', 'index.html')

@app.route('/ssoapi/sso-link', strict_slashes=False) 
def sso_link():
    sso_link = "https://cloudsso.cisco.com/as/authorization.oauth2?response_type=code&client_id="+ client_id + "&redirect_uri=" + redirect_url + "&scope=openid%20profile%20email&state="
    return sso_link

@app.route('/login_status', strict_slashes=False)
def login_status():
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        #email = session_ids.get(session_id, None)
        success, token, email = getAccessTokenBySession(session_id)
        if email is None:
            return "", 404
        else:
            return '{\"email\":\"' + email + '\"}'

@app.route('/ssoapi/accounts', strict_slashes=False)
def account():
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        success, token, email = getAccessTokenBySession(session_id)
        if success:
            logger.info("Obtained token. Getting expired licenses")
            while email in license_cache_lock.keys():
                time.sleep(.1)
            json_array = redis_db.get("license_"+email)
            if not json_array is None:
                logger.info("Using cached data")
                #cssm_license = license_cache[email]
                parser = cssm_parser.CSSMJSONParser(json.loads(json_array.decode()))
                cssm_license = parser.cssm_license()
            else:
                success, cssm_license = get_cssm_license(token)
            return jsonify(cssm_license.cssm_virt_account_by_accountName()), 200
        else:
            return "", 404

    return None

@app.route('/ssoapi/customer', strict_slashes=False, methods=["GET", "POST"])
def customer():
    logger.info("Entering customer endpoint")
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        success, token, email = getAccessTokenBySession(session_id)
        filter_data = json.loads(request.data.decode())
        if success:
            logger.info("Obtained token. Getting expired licenses")
            while email in license_cache_lock.keys():
                time.sleep(.1)
            json_array = redis_db.get("license_"+email)
            if not json_array is None:
                logger.info("Using cached data")
                #cssm_license = license_cache[email]
                parser = cssm_parser.CSSMJSONParser(json.loads(json_array.decode()))
                cssm_license = parser.cssm_license()
            else:
                success, cssm_license = get_cssm_license(token)
            return jsonify(cssm_license.cssm_top_license_customer_dict(get_va_list(cssm_license,filter_data))), 200
        else:
            return "", 404

    return None

@app.route('/ssoapi/technology', strict_slashes=False, methods=["GET", "POST"])
def technology():
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        success, token, email = getAccessTokenBySession(session_id)
        filter_data = json.loads(request.data.decode())
        if success:
            logger.info("Obtained token. Getting expired licenses")
            while email in license_cache_lock.keys():
                time.sleep(.1)
            json_array = redis_db.get("license_"+email)
            if not json_array is None:
                logger.info("Using cached data")
                #cssm_license = license_cache[email]
                parser = cssm_parser.CSSMJSONParser(json.loads(json_array.decode()))
                cssm_license = parser.cssm_license()
            else:
                success, cssm_license = get_cssm_license(token)
            return jsonify(cssm_license.cssm_top_license_technology_dict(get_va_list(cssm_license,filter_data))), 200
        else:
            return "", 404

    return None

@app.route('/ssoapi/expired_license', strict_slashes=False, methods=["GET", "POST"])
def expired_license():
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        success, token, email = getAccessTokenBySession(session_id)
        filter_data = json.loads(request.data.decode())
        if success:
            logger.info("Obtained token. Getting expired licenses")
            while email in license_cache_lock.keys():
                time.sleep(.5)
            json_array = redis_db.get("license_"+email)
            if not json_array is None:
                logger.info("Using cached data")
                #cssm_license = license_cache[email]
                parser = cssm_parser.CSSMJSONParser(json.loads(json_array.decode()))
                cssm_license = parser.cssm_license()
            else:
                success, cssm_license = get_cssm_license(token)
            return jsonify(cssm_license.cssm_top_five_future_expired_licenses(get_va_list(cssm_license,filter_data))), 200
        else:
            return "", 404

    return None



@app.route('/ssoapi/license')
def license():
    if 'Authorization' in request.headers:
        session_id = request.headers.get('Authorization')
        success, token = getAccessTokenBySession(session_id)
        if success:
            return get_cssm_license(token), 200
        else:
            return "", 404

    return None

@app.route('/login', methods=["GET", "POST"])
def login():
    print ("Login Arguments")
    print (request.args)
    if not request.args.get("code") is None:
        token = token_mgr.new_token(request.args.get("code"))
        session_id = request.args.get("state")
        email = token_mgr.fetch_email(token.get("access_token"))
        #tokens[email.get("email")] = token
        redis_db.set("token_" + email.get("email"), token.get("access_token"))
        teams_id = getTeamsIds(email.get("email"))
        
        person_id = teams_id.get("personId")
        room_id = teams_id.get("roomId")
        print ("email retrieved")
        print (email.get("email"))
        #if not person_id in teams_ids.keys():
            #print ('adding person key to teams_ids')
            #teams_ids[person_id] = {}
        #teams_ids[person_id][room_id] = email.get("email")
        redis_db.set("teams_" + person_id + room_id, email.get("email"))

        #if not session_id in session_ids.keys():
        #    session_ids[session_id] = {}
        #session_ids[session_id] = email.get("email")
        redis_db.set("session_"+session_id, email.get("email"))

        #start license load thread for caching data
        t = threading.Thread(target=license_cacher, args=(email.get("email"),token.get("access_token")))
        t.start()

        return redirect(url_for('home'))


def license_cacher(email, token):
    """thread worker function"""
    while email in license_cache_lock.keys():
        time.sleep(.5)
    license_cache_lock[email] = True
    success, json_array = get_cssm_license(token)
    if success:
        logger.info("license info cached")
        #license_cache[email] = cssm_license
        redis_db.set("license_"+email, json.dumps(json_array))
    else:
        logger.info("License cache request failed")
    del license_cache_lock[email]

def get_va_list(cssm_license, filter_data):
    va_list = []
    accounts = cssm_license.cssm_virt_account_by_accountName()
    for account in filter_data["filter"]:
        logger.info(account)
        if account["parent"] == '':
            for va_account in accounts[account["value"]]:
                va_list.append(account["value"] + "_" + va_account)
        else:
            va_list.append(account["parent"] + "_" + account["value"])
    logger.info(va_list)
    return va_list

def getTeamsIds(email):
    #code was written with token in this variable. It should be inserted with environment variable
    bot_token = os.environ.get("WEBEX_TEAMS_TOKEN")
    #logger.info(bot_token)
    webex_teams_email_address = email
    meeting_room = wbx_meeting_room.WBXTeamsMeetingRoom(bot_token, webex_teams_email_address)

    ids = meeting_room.create_teams_room_get_room_people_ids()
    print(ids)
    return ids

def getAccessTokenBySession(sessionId):
    #email = session_ids.get(sessionId, None)
    email = redis_db.get("session_"+ sessionId)
    print ("email")
    print (email)
    if email is None:
        return False, '', None
    #return True, tokens[email].get("access_token"), email
    return True, redis_db.get("token_" + email.decode()).decode(), email.decode() 

def get_cssm_license(account_credentials=""):

    cssm_license = None
    request_successful = False

    smart_account = SmartAccountSDK("apx.cisco.com", account_credentials)
    logger.info('entering smart_account.list_all_licenses()')
    request_successful, json_array = smart_account.list_all_licenses()
    logger.info('have exited smart_account.list_all_licenses()')
    logger.info('request_successful: {}\n'.format(request_successful))
    #if request_successful:
        #logger.info('json array: {}'.format(json.dumps(json_array, indent=4)))

        #parser = cssm_parser.CSSMJSONParser(json_array)
        #cssm_license = parser.cssm_license()


    logger.info('request_successful: {}\n, cssm_license: {}\n'.format(request_successful, cssm_license))

    return request_successful, json_array

if __name__ == "__main__":
    flask_port = 10000

    print('\n********   Starting up Flask Web...    ********\n\n')

    app.run(host='0.0.0.0', port=flask_port, debug=True)
