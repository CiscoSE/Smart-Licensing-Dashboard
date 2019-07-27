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

import ApiService from "@/common/api.service";
import {
  FETCH_SSO_LINK
} from "./actions.type";
import { SET_ERROR, SET_SSO_LINK } from "./mutations.type";

const state = {
  ssoLink: ""
};

const getters = {
  ssoLink(state) {
    return state.ssoLink;
  }
};

const actions = {
  async [FETCH_SSO_LINK](context) {
      return new Promise((resolve, reject) => {
      	ApiService.get("ssoapi/sso-link")
        	.then(({ data }) => {
          	context.commit(SET_SSO_LINK, data);
		resolve(data);
        })
      	.catch(({ response }) => {
        	context.commit(SET_ERROR, response.data.errors);
		reject(response)
      	});
      });
  } 

};

const mutations = {
  [SET_ERROR](state, error) {
    state.errors = error;
  },
  [SET_SSO_LINK](state, link) {
    state.ssoLink = link;
  }
};

export default {
  state,
  actions,
  mutations,
  getters
};
