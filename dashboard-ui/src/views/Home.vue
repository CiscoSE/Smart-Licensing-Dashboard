<!--
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
-->


<template>
  <div class="home-page">
   <div class = "container">
      <div class="col-md-3">
	  <sidebar-menu :menu="menu" width="150px" @item-click="onItemClick" />
      </div>
      <div class="col-md-9">
        <div class="row">
          <div class="row"> 
            <div class="col-md-3">
      	      <img src="img/logo.png" alt="Cisco" height="100" width="200">
            </div>
            <div class="col-md-9 align-self-end">
              <h1 class="header-text">Smart License Dashboard</h1>
            </div>
          </div>
        </div>
        <div class="container page">
          <div class="row">
            <div class="col-md-12">
              <router-view></router-view>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { FETCH_SSO_LINK } from "@/store/actions.type";
import { uuid } from "vue-uuid";

export default {
  name: "home",
  components: {
  },
  data() {
    return {
        menu: [
                //{
                //        header: true,
                //        title: '',
                //        // component: componentName
                //        // visibleOnCollapse: true
                //        class: 'logo'
                //        // attributes: {}
                //},
		//{
		//	header: true,
		//	title: 'Smart License Dashboard'
		//},
                {
                    href: '/',
                    title: 'Home',
                    icon: 'fa fa-user'
                },
                {
                    href: '#',
                    title: 'Login',
                    icon: 'fa fa-chart-area'
                },
		{
		    href: '/report',
		    title: 'Reports',
		    icon: 'fa fa-chart-area'
		}
            ]
     }
  },
  mounted() {
    this.$store.dispatch(FETCH_SSO_LINK);
  },
  computed: {
    ...mapGetters(["ssoLink"])
  },
  methods: {
    onItemClick(event, item) {
	if (item.title === "Login") {
		var sessionId = uuid.v4();
      		this.$cookies.set("session", sessionId); 

		window.location.href = this.ssoLink + sessionId
 
	}
    }
  }
};
</script>
