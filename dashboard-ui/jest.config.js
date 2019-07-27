/**
* Copyright (c) 2019 Cisco and/or its affiliates.
*
* This software is licensed to you under the terms of the Cisco Sample
* Code License, Version 1.0 (the "License"). You may obtain a copy of the
* License at
*
*               https://developer.cisco.com/docs/licenses
*
* All use of the material herein must be in accordance with the terms of
* the License. All rights not expressly granted by the License are
* reserved. Unless required by applicable law or agreed to separately in
* writing, software distributed under the License is distributed on an "AS
* IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
* or implied.
*
**/



module.exports = {
  moduleFileExtensions: ["js", "jsx", "json", "vue"],
  transform: {
    "^.+\\.vue$": "vue-jest",
    ".+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$":
      "jest-transform-stub",
    "^.+\\.jsx?$": "babel-jest"
  },
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1"
  },
  snapshotSerializers: ["jest-serializer-vue"],
  testMatch: [
    "**/tests/unit/**/*.spec.(js|jsx|ts|tsx)|**/__tests__/*.(js|jsx|ts|tsx)"
  ],
  testURL: "http://localhost/"
};
