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

import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import ApiService from "./common/api.service";
import UUID from 'vue-uuid'; 
import VueCookies from 'vue-cookies'
import {ClientTable} from 'vue-tables-2';
import Chartkick from 'vue-chartkick'
import Chart from 'chart.js'
import VueSidebarMenu from 'vue-sidebar-menu'
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

//Chart.Legend.prototype.afterFit = function() {
//    this.height = this.height + 50;
//};

Vue.use(VueSidebarMenu)
Vue.use(Chartkick.use(Chart))
Vue.use(ClientTable);
Vue.use(VueCookies)
Vue.use(UUID);

Vue.config.productionTip = false;
ApiService.init();
;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
