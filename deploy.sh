###
#
#Copyright (c) 2019 Cisco and/or its affiliates.
#
#This software is licensed to you under the terms of the Cisco Sample
#Code License, Version 1.0 (the "License"). You may obtain a copy of the
#License at
#
#               https://developer.cisco.com/docs/licenses
#
#All use of the material herein must be in accordance with the terms of
#the License. All rights not expressly granted by the License are
#reserved. Unless required by applicable law or agreed to separately in
#writing, software distributed under the License is distributed on an "AS
#IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#or implied.
#
###

set -e

rm -rf ~/cisco-cssm/Smart-Licensing-Dashboard/dist
cp -r ~/cisco-cssm/Smart-Licensing-Dashboard/dashboard-ui/dist ~/cisco-cssm/Smart-Licensing-Dashboard/
cp -r ~/cisco-cssm/Smart-Licensing-Dashboard/Smart-Licensing-Dashboard-Backend/* ~/cisco-cssm/Smart-Licensing-Dashboard/dist/
cp ~/cisco-cssm/Smart-Licensing-Dashboard/cssm.ini ~/cisco-cssm/Smart-Licensing-Dashboard/dist/
cp ~/cisco-cssm/Smart-Licensing-Dashboard/keys ~/cisco-cssm/Smart-Licensing-Dashboard/dist/
rm -rf /var/dashboard
mkdir /var/dashboard
cp -r ~/cisco-cssm/Smart-Licensing-Dashboard/dist/* /var/dashboard/
find /var/dashboard -type f -exec chmod 0660 {} \;
sudo find /var/dashboard -type d -exec chmod 2770 {} \;
sudo chown -R "$USER":www-data /var/dashboard
sudo systemctl restart cssm.service
