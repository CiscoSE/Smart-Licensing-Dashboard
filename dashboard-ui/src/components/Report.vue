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
  <div class="">
	<br />
	<br />
  	<div class="article-preview">Work In Progress - Historical Activations For Customer</div>  
    	<div id="activity">
		<column-chart :colors="['#b00', '#666', '#0b0', '#00b']" :stacked="true" height="400px" :data="[['Jan', 32], ['Feb', 46], ['March', 20], ['April', 60], ['May', 22], ['June', 43], ['July', 33], ['Aug', 10], ['Sept', 80], ['Oct', 19], ['Nov', 20], ['Dec', 15]]"></column-chart>	
    	</div>	
  </div>
</template>

<script>

export default {
  name: "Report",
  components: {
  },
  props: {
    
  },
  data() {
   return {
   };
  },
  computed: {
  },
  watch: {
  },
  mounted() {
  },
  methods: { 
  }
};
</script>
