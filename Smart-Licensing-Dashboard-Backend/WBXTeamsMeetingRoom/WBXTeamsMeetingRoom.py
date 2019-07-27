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

import json
import requests
import datetime as dt


__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = ["William Kurkian <wkurkian@cisco.com>"]
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


class WBXTeamsMeetingRoom(object):
    def __init__(self, bot_token, teams_email_address):
        self.teams_email_address = teams_email_address
        self.bot_token = bot_token
        self.__message_json = None

    def message_json(self):
        if self.__message_json is None:
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
            the_dict = {'toPersonEmail': self.teams_email_address,
                        'markdown': msg}
            self.__message_json = json.dumps(the_dict)
 
        return self.__message_json

    def roomId_from_response_json(self, input_json):
        room_Id = ''
        if type(input_json) is dict:
            room_Id = input_json['roomId']
        elif type(input_json) is str:
            the_dict = json.loads(input_json)
            room_Id = the_dict['roomId']
        return room_Id

    def personId_from_response_json(self, input_json):

        person_Id = ''
        items = []
        if type(input_json) is dict:
            items = input_json['items']
        elif type(input_json) is str:
            the_dict = json.loads(input_json)
            items = the_dict['items']

        for item in items:
            if item['personEmail'] == self.teams_email_address:
                person_Id = item['personId']
                break

        return person_Id

    def create_team_room(self):
        post_url = "https://api.ciscospark.com/v1/messages"

        post_data = self.message_json()

        request_response_results = self.post_request(post_url,
                                                     post_headers={"Accept": "application/json",
                                                                   "Content-Type": "application/json;charset=UTF-8",
                                                                   "Authorization": "Bearer {}".format(self.bot_token)},
                                                     post_data=post_data)

        return request_response_results

    def get_room_membership_list(self, roomId):
        get_url = "https://api.ciscospark.com/v1/memberships?roomId={}".format(roomId)

        request_response_results = self.get_request(get_url,
                                                     get_headers={"Accept": "application/json",
                                                                   "Content-Type": "application/json;charset=UTF-8",
                                                                   "Authorization": "Bearer {}".format(self.bot_token)})
        return request_response_results

    def create_teams_room_get_room_people_ids(self):


        request_response_results = self.create_team_room()
        request_response_is_successful = request_response_results[0]

        date_time = dt.datetime.now()

        if request_response_is_successful:
            print("{}: creating team room was successful".format(date_time))
            room_Id = self.roomId_from_response_json(request_response_results[1].json())

            request_response_results = self.get_room_membership_list(room_Id)
            request_response_is_successful = request_response_results[0]

            if request_response_is_successful:
                print('persondId:  {}'.format(json.dumps(json.loads(request_response_results[1].text), indent=4)))
                person_Id = self.personId_from_response_json(request_response_results[1].json())


        return {'roomId': room_Id, 'personId': person_Id}

    def post_request(self, url, post_headers, post_data=None, post_json=None):

        spark_request = None
        if post_data:
            spark_request = requests.post(url,
                                          data=post_data,
                                          headers=post_headers)
        elif post_json:
            spark_request = requests.post(url, json=post_json, headers=post_headers)
        else:
            return [False, {"error_key": "No json or data payload"}]

        if spark_request.status_code == 200:
            return [True, spark_request]
        else:
            return [False, {"error_key": spark_request.status_code,
                            "response_json_key": json.loads(spark_request.text)}]

    def get_request(self, url, get_headers, post_data=None, post_json=None):

        spark_request = None
        spark_request = requests.get(url, headers=get_headers)

        if spark_request.status_code == 200:
            return [True, spark_request]
        else:
            return [False, {"error_key": spark_request.status_code,
                            "response_json_key": json.loads(spark_request.text)}]

