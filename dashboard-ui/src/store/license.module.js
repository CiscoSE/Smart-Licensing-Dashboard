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
  FETCH_EXPIRING,
  FETCH_TECHNOLOGY,
  FETCH_ACCOUNTS,
  FETCH_CUSTOMERS
} from "./actions.type";
import {
  SET_LICENSE,
  SET_TECHNOLOGY,
  SET_ACCOUNT,
  SET_CUSTOMERS,
  SET_ERROR
} from "./mutations.type";

const initialState = {
  expiring_license: {},
  top_technology: {},
  accounts : {},
  customers : {}
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_EXPIRING](context, filter) {
      return new Promise((resolve, reject) => {
      	ApiService.setHeader();
      	ApiService.post("ssoapi/expired_license", filter)
        	.then(({ data }) => {
          	context.commit(SET_LICENSE, data);
		resolve(data);
        })
      	.catch(({ response }) => {
        	context.commit(SET_ERROR, response.data.errors);
		reject(response)
      	});
      });
  },
  async [FETCH_TECHNOLOGY](context, filter) {
      return new Promise((resolve, reject) => {
      	ApiService.setHeader();
      	ApiService.post("ssoapi/technology", filter)
        	.then(({ data }) => {
          	context.commit(SET_TECHNOLOGY, data);
		resolve(data);
        })
      	.catch(({ response }) => {
        	context.commit(SET_ERROR, response.data.errors);
		reject(response)
      	});
      });
  },
  async [FETCH_ACCOUNTS](context) {
      return new Promise((resolve, reject) => {
      	ApiService.setHeader();
      	ApiService.get("ssoapi/accounts")
        	.then(({ data }) => {
          	context.commit(SET_ACCOUNT, data);
		resolve(data);
        })
      	.catch(({ response }) => {
        	context.commit(SET_ERROR, response.data.errors);
		reject(response)
      	});
      });
  },
  async [FETCH_CUSTOMERS](context, filter) {
      return new Promise((resolve, reject) => {
      	ApiService.setHeader();
      	ApiService.post("ssoapi/customer", filter)
        	.then(({ data }) => {
          	context.commit(SET_CUSTOMERS, data);
		resolve(data);
        })
      	.catch(({ response }) => {
        	context.commit(SET_ERROR, response.data.errors);
		reject(response)
      	});
      });
  } 


};

/* eslint no-param-reassign: ["error", { "props": false }] */
export const mutations = {
  [SET_LICENSE](state, license) {
    state.expiring_license = license;
  },
  [SET_TECHNOLOGY](state, technology) {
    state.top_technology = technology;
  },
  [SET_ACCOUNT](state, accounts) {
    state.accounts = accounts
  },
  [SET_CUSTOMERS](state, customers) {
    state.customers = customers
  }


};

const getters = {
  expiring_license(state) {
    return state.expiring_license;
  },
  top_technology(state) {
    return state.top_technology;
  },
  list_accounts(state) {
    return state.accounts;
  },
  top_customers(state) {
    return state.customers;
  }
};

export default {
  state,
  actions,
  mutations,
  getters
};
