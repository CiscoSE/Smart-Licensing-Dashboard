import WBXTeamsMeetingRoom as wbx_meeting_room

meeting_room = wbx_meeting_room.WBXTeamsMeetingRoom("teams_token",
                                                    'email')

print(meeting_room.create_teams_room_get_room_people_ids())
