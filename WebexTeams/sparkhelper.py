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
from __future__ import absolute_import, division, print_function

import datetime as dt
import requests
import json
import hashlib
import hmac

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

def get_membership_org_id_list(json_items):
    return [d['personOrgId'] for d in json_items['items']]

def orgs_are_in_allowed_org_list(allowed_person_Org_Id, message_json):

    if type(allowed_person_Org_Id) is str:
        the_allowed_person_Org_id_list = [allowed_person_Org_Id]
    else:
        the_allowed_person_Org_id_list=allowed_person_Org_Id

    org_id_list = get_membership_org_id_list(message_json)

    number_orgs_not_allowed = len(set(the_allowed_person_Org_id_list).symmetric_difference(org_id_list))

    orgs_are_allowed=False
    if number_orgs_not_allowed == 0:
        orgs_are_allowed=True
    return orgs_are_allowed


def membership_check(room_Id, bot_token, allowed_person_Org_Id):
    date_time = dt.datetime.now()
    print("{}, membership_check starting".format(date_time))
    the_url = 'https://api.ciscospark.com/v1/memberships?roomId={}'.format(room_Id)
    room_member_orgs_allowed = False

    get_request_headers = {"Authorization": "Bearer {}".format(bot_token)}

    message_response = requests.get(the_url, verify=True, headers=get_request_headers)
    if message_response.status_code == 200:

        message_json = json.loads(message_response.text)

        room_member_orgs_allowed = orgs_are_in_allowed_org_list(allowed_person_Org_Id, message_json)

    else:
        print("{},   membership check failed: {}".format(date_time, message_response))

    print("{}, membership_check ending".format(date_time))
    return room_member_orgs_allowed

def check_and_delete_membership(bot_token, allowed_person_Org_Id):
    membership_url = "https://api.ciscospark.com/v1/memberships"
    membership_message_response = requests.get(membership_url, verify=True, headers={'Authorization': 'Bearer {}'.format(bot_token)})

    response_json = json.loads(membership_message_response.text)
    print(response_json, membership_message_response.status_code)
    if membership_message_response.status_code != 200:
        return
    memberships = response_json['items']
    # print(memberships)

    bad_memberships = []
    for membership_item in memberships:
        roomId = membership_item['roomId']
        membership_id = membership_item['id']

        allowed_membership = membership_check(roomId, bot_token, allowed_person_Org_Id)

        if allowed_membership == False:
            bad_memberships.append(membership_id)

            print("   Found Membership to delete:\n   ...roomId: {}\n   ...membershipId:  {}\n".format(roomId,
                                                                                                       membership_id))

    if len(bad_memberships) > 0:
        for bad_membership_id in bad_memberships:
            print("   ...deleting membership:  {}".format(bad_membership_id))
            delete_url = "https://api.ciscospark.com/v1/memberships/{}".format(bad_membership_id)
            delete_message_response = requests.delete(delete_url, verify=True,
                                               headers={'Authorization': 'Bearer {}'.format(bot_token)})
            if delete_message_response.status_code != 204:
                print("!!!***...unable to delete membership.  Rerun audit to delete")
            else:
                print("   ...delete membership status code: {}".format(delete_message_response.status_code))

    else:
        print("...no memberships to delete")


def verify_signature(key, raw_request_data, request_headers):
    date_time = dt.datetime.now()
    print("{}: verify_signature: start".format(date_time))
    signature_verified = False
    # Let's create the SHA1 signature
    # based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw_request_data, hashlib.sha1)
    validated_signature = hashed.hexdigest()

    if validated_signature == request_headers.get('X-Spark-Signature'):
        signature_verified = True
        print("{}:   verify_signature: webhook signature is valid".format(dt.datetime.now()))
    else:
        print("{}.   verify_signature: webhook signature is NOT valid".format(dt.datetime.now()))

    print("{}: verify_signature: end".format(date_time))
    return signature_verified
