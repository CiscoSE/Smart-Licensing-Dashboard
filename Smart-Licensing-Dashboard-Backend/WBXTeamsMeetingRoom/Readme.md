# WBXTeamsMeetingRoom Class
This class creates a Webex Team Room with the Smart Licensing Dashboard Bot and the user of the dashboard.

After creating the room, the class returns the non-Personably Identifiable Information (PII) 'personId' and 'roomId' 
that can be used to associate the user with the CSSM access token.  

## Usage

````python
import WBXTeamsMeetingRoom as wbx_meeting_room
import os

bot_token = os.environ.get('SMART_LICENSING_ACCESS_TOKEN')
webex_teams_email_address = "your_webex_teams@emailaddress.com"
meeting_room = wbx_meeting_room.WBXTeamsMeetingRoom(bot_token, webex_teams_email_address)

the_dict = meeting_room.create_teams_room_get_room_people_ids()

print(the_dict)

````
The result should be a dictionary with 'roomId' and 'personId' keys:
```python
{
    'roomId': 'aRoomID',
    'personId': 'aPersonId',
}

```
