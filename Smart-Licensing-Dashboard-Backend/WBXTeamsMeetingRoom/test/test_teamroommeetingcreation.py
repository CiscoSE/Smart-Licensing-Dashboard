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
import WBXTeamsMeetingRoom as wbxtm_meeting

__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


class WBXTeamsMeetingRoomTest(unittest.TestCase):

    def test_WBXTeamsMeetingRoomExists(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')
        self.assertIsNotNone(meeting_room_maker, 'test_WBXTeamsMeetingRoomExits should return an object')

    def test_creates_correct_object(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')
        self.assertIsInstance(meeting_room_maker, wbxtm_meeting.WBXTeamsMeetingRoom,
                              'test_creates_correct_object should return correct object.\nExpected: {}\n' \
                              'Result: {}'.format(type(wbxtm_meeting.WBXTeamsMeetingRoom), type(meeting_room_maker)))

    def test_message_json_creation_is_correct(self):
        meeting_room_maker= wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = {
            "toPersonEmail": "timtayl@cisco.com",
            "markdown": "This is the **Smart Dashboard Bot**.  Welcome to the Smart Licensing Dashboard!  Please stand by while we get things setup."
        }

        result = json.loads(meeting_room_maker.message_json())

        self.assertEqual(result, expected, 'test_message_json_creation_is_correct should return correct message json.\n'
                                           'Expected: {}\nResult: {}'.format(expected, result))

    def test_message_creation_response_returns_proper_personId_returns_string(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "somePersonIDalskd3"

        input_json = {
            "id": "someID",
            "roomId": "someMeetingRoomID1q3qerwerqew",
            "toPersonEmail": "timtayl@cisco.com",
            "roomType": "direct",
            "text": "This is the Smart Dashboard Bot. Welcome to the Smart Licensing Dashboard! Please stand by while we get things setup.",
            "personId": "somePersonID",
            "personEmail": "SLDBot@webex.bot",
            "markdown": "some Mark Down",
            "html": "<p>Some html</p>",
            "created": "2019-06-20T15:05:09.544Z"
        }

        result = meeting_room_maker.roomId_from_response_json(input_json)

        self.assertIsInstance(result, str, 'test_message_creation_response_returns_proper_personId_returns_string.\n'
                                           'Expected: {}\nResult: {}'.format(type(""), type(result)))

    def test_message_creation_response_parsing_returns_roomID_sending_dict(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "someMeetingRoomID1q3qerwerqew"

        input_json = {
            "id": "someID",
            "roomId": "someMeetingRoomID1q3qerwerqew",
            "toPersonEmail": "timtayl@cisco.com",
            "roomType": "direct",
            "text": "This is the Smart Dashboard Bot. Welcome to the Smart Licensing Dashboard! Please stand by while we get things setup.",
            "personId": "somePersonID",
            "personEmail": "SLDBot@webex.bot",
            "markdown": "some Mark Down",
            "html": "<p>Some html</p>",
            "created": "2019-06-20T15:05:09.544Z"
        }

        result = meeting_room_maker.roomId_from_response_json(input_json)

        print(expected)

        self.assertEqual(result, expected, 'test_message_creation_response_parsing_returns_roomID.\nExpected: {}\n'
                                           'Result: {}'.format(expected, result))

    def test_message_creation_response_parsing_returns_roomID_sending_string(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "someMeetingRoomID1q3qerwerqew"

        input_json = {
            "id": "someID",
            "roomId": "someMeetingRoomID1q3qerwerqew",
            "toPersonEmail": "timtayl@cisco.com",
            "roomType": "direct",
            "text": "This is the Smart Dashboard Bot. Welcome to the Smart Licensing Dashboard! Please stand by while we get things setup.",
            "personId": "somePersonID",
            "personEmail": "SLDBot@webex.bot",
            "markdown": "some Mark Down",
            "html": "<p>Some html</p>",
            "created": "2019-06-20T15:05:09.544Z"
        }

        result = meeting_room_maker.roomId_from_response_json(json.dumps(input_json))

        print(expected)

        self.assertEqual(result, expected, 'test_message_creation_response_parsing_returns_roomID.\nExpected: {}\n'
                                           'Result: {}'.format(expected, result))

    def test_membership_check_response_returns_proper_personId_returns_string(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "somePersonIDalskd3"

        input_json = {
              "items": [
                        {
                          "id": "someID1",
                          "roomId": "someMeetingRoomID1q3qerwerqew",
                          "personId": "somePersonIDalskd3",
                          "personEmail": "timtayl@cisco.com",
                          "personDisplayName": "Tim Taylor",
                          "personOrgId": "somePersonORgID1",
                          "created": "2019-06-07T17:14:33.919Z"
                        },
                        {
                          "id": "someID2",
                          "roomId": "someMeetingRoomID1q3qerwerqew",
                          "personId": "somePersonIDaladskfpkj4",
                          "personEmail": "SLDBot@webex.bot",
                          "personDisplayName": "SmartLicensingBot",
                          "personOrgId": "somePersonORgID2",
                          "created": "2019-06-07T17:14:33.919Z"
                        }
                      ]
        }

        result = meeting_room_maker.personId_from_response_json(input_json)

        self.assertIsInstance(result, str, 'test_membership_check_response_returns_proper_personId_returns_string.\n'
                                           'Expected: {}\nResult: {}'.format(type(""), type(result)))

    def test_membership_check_response_returns_proper_personId_sending_dict(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "somePersonIDalskd3"

        input_json = {
            "items": [
                {
                    "id": "someID1",
                    "roomId": "someMeetingRoomID1q3qerwerqew",
                    "personId": "somePersonIDalskd3",
                    "personEmail": "timtayl@cisco.com",
                    "personDisplayName": "Tim Taylor",
                    "personOrgId": "somePersonORgID1",
                    "created": "2019-06-07T17:14:33.919Z"
                },
                {
                    "id": "someID2",
                    "roomId": "someMeetingRoomID1q3qerwerqew",
                    "personId": "somePersonIDaladskfpkj4",
                    "personEmail": "SLDBot@webex.bot",
                    "personDisplayName": "SmartLicensingBot",
                    "personOrgId": "somePersonORgID2",
                    "created": "2019-06-07T17:14:33.919Z"
                }
            ]
        }

        result = meeting_room_maker.personId_from_response_json(input_json)

        self.assertEqual(result, expected,
                              'test_membership_check_response_returns_proper_personId_sending_dict returns '
                              'correct value.\nExpected: {}\nResult: {}'.format(expected, result))

    def test_membership_check_response_returns_proper_personId_sending_string(self):
        meeting_room_maker = wbxtm_meeting.WBXTeamsMeetingRoom('sample_bot_token', 'timtayl@cisco.com')

        expected = "somePersonIDalskd3"

        input_json = {
            "items": [
                {
                    "id": "someID1",
                    "roomId": "someMeetingRoomID1q3qerwerqew",
                    "personId": "somePersonIDalskd3",
                    "personEmail": "timtayl@cisco.com",
                    "personDisplayName": "Tim Taylor",
                    "personOrgId": "somePersonORgID1",
                    "created": "2019-06-07T17:14:33.919Z"
                },
                {
                    "id": "someID2",
                    "roomId": "someMeetingRoomID1q3qerwerqew",
                    "personId": "somePersonIDaladskfpkj4",
                    "personEmail": "SLDBot@webex.bot",
                    "personDisplayName": "SmartLicensingBot",
                    "personOrgId": "somePersonORgID2",
                    "created": "2019-06-07T17:14:33.919Z"
                }
            ]
        }

        result = meeting_room_maker.personId_from_response_json(json.dumps(input_json))

        self.assertEqual(result, expected,
                              'test_membership_check_response_returns_proper_personId_sending_string returns '
                              'correct value.\nExpected: {}\nResult: {}'.format(expected, result))

if __name__ == '__main__':
    unittest.main()
