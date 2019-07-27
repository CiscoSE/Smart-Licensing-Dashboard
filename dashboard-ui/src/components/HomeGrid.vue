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
  <div class="container">
    <br />
    <br />
    <div class="row"> 
    	<div class="col-md-8">
		<div class="row">
			<div class="col-md-6">
				<div class="article-preview"><h5>Top Customers by Usage (Top 5)</h5></div>  
    				<div id="customer">
      					<!--<v-client-table :data="customers" :columns="customer_columns" :options="options"></v-client-table>-->
					<pie-chart :data="customers_chart" width="250px" height="250px"></pie-chart>

    				</div>
			</div>
			<div class="col-md-6">
				<div class="article-preview"><h5>Top Technologies by Usage (Top 5)</h5></div>  
    				<div id="technology">
      					<!--<v-client-table :data="technologies" :columns="tech_columns" :options="options"></v-client-table>-->
					<pie-chart :data="technologies_chart" width="250px" height="250px""></pie-chart>
    				</div>
			</div>
 
		</div>
		<br />
		<br />
    		<div class="article-preview"><h5>Expiring Licenses (Top 5)</h5></div>  
    		<div id="licenses">
      			<v-client-table :data="licenses" :columns="columns" :options="options"></v-client-table>
    		</div> 
    	</div>
    	<div class="col-md-4">
    		<treeselect :multiple="true" :options="accounts" 
 			:always-open="true"
    			:append-to-body="true"
			v-model="filterValue" />
    	</div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { FETCH_EXPIRING, FETCH_TECHNOLOGY, FETCH_ACCOUNTS, FETCH_CUSTOMERS } from "../store/actions.type";
import Treeselect from '@riophae/vue-treeselect'
import '@riophae/vue-treeselect/dist/vue-treeselect.css'
  

export default {
  name: "HomeGrid",
  components: {
	Treeselect
  },
  props: {
  },
  data() {
   return {
      columns: ['Smart Account', 'Virtual Account', 'License Name', 'Quantity', 'End Date'],
      licenses: [],
      tech_columns: ['Technology', 'Usage'],
      technologies: [],
      technologies_chart: [],
      customer_columns: ['Customer', 'Usage'],
      customers: [],
      customers_chart: [],
      options: {
            // see the options API
      },
      myCustomOptions: {},
      myCustomStyles: {},
      value: null,
      accounts: [],
      filterValue: null,
      filter: []
    };
  },
  computed: {
    ...mapGetters(["isLoading","expiring_license","top_technology","list_accounts","top_customers"])
  },
  watch: {
    'filterValue': function(val, oldVal){
	 this.setFilter();
         this.fetchExpiring();
         this.fetchTechnology();
         this.fetchCustomers();
    }
  },
  mounted() {
    this.fetchExpiring();
    this.fetchTechnology();
    this.fetchAccounts();
    this.fetchCustomers();
  },
  methods: {
    setFilter() {
      this.filter = [];
      for (var i = 0; i < this.filterValue.length; i++) {
        var value = this.filterValue[i];
	var split_value = value.split("@");
        var parent = "";
	var name = split_value[1];
        if (split_value.length > 2) {
          parent = split_value[1];
          name = split_value[3];
        }
        var filter = {
          "value": name,
          "parent": parent
        }
        this.filter.push(filter);
      }
    },
    fetchExpiring() {
      this.$store.dispatch(FETCH_EXPIRING, {filter:this.filter}).then(response => {
            this.processLicenses()
        }, error => {
            console.error("Got nothing from server")
        })
    },
    fetchTechnology() {
      this.$store.dispatch(FETCH_TECHNOLOGY, {filter:this.filter}).then(response => {
            this.processTechnology()
        }, error => {
            console.error("Got nothing from server")
        })
    },
    fetchAccounts() {
      this.$store.dispatch(FETCH_ACCOUNTS, {}).then(response => {
            this.processAccounts()
        }, error => {
            console.error("Got nothing from server")
        })
    },
    fetchCustomers() {
      this.$store.dispatch(FETCH_CUSTOMERS, {filter:this.filter}).then(response => {
            this.processCustomers()
        }, error => {
            console.error("Got nothing from server")
        })
    },
    processLicenses() {
	var licenses = [];
    	var accounts = this.expiring_license.future_expired_licenses;
    	for (var i in accounts) {
        	var sa_account_name = i;
		for (var j in accounts[i]) {
	    		var va_account_name = j;
	    		for (var k in accounts[i][j]) {
				var license_name = k;
				var license_list = accounts[i][j][k];
				for (var index = 0; index < license_list.length; index++) {
					var license = {
						"Smart Account": sa_account_name,
						"Virtual Account": va_account_name,
						"License Name": license_name,
						"Quantity": license_list[index].quantity,
						"End Date": license_list[index].endDate
					}
					licenses.push(license);
				}
			}
    		}
	}
	this.licenses = licenses;

    },
    processTechnology() {
	// Pie chart example: [['Blueberry', 44], ['Strawberry', 23]]
	var technologies = [];
	var technologies_chart = [];
    	for (var i in this.top_technology) {
        	var tech_name = i;
		var usage = this.top_technology[i]["inUse"]
		var tech = {
			"Technology": tech_name,
			"Usage": parseFloat(usage).toFixed(2)+"%"
		}
		var tech_chart = [tech_name, parseFloat(usage).toFixed(2)]
		technologies.push(tech);
		technologies_chart.push(tech_chart);
	}
	this.technologies = technologies;
	this.technologies_chart = technologies_chart;
    },
    processAccounts() {
	var accounts = [];
	this.filterValue = [];
    	for (var i in this.list_accounts) {
        	var sa_name = i;
		var sa_item = {
			id: "sa@"+sa_name,
			label: sa_name,
			children: []
		};
		this.filterValue.push("sa@"+sa_name)
		for (var j = 0; j < this.list_accounts[i].length; j++) {
			var child = {
				id: "sa@"+sa_name+"@va@"+this.list_accounts[i][j],
				label: this.list_accounts[i][j]
			};
			sa_item.children.push(child);
		}
		accounts.push(sa_item);
	}
	this.accounts = accounts;
    },
    processCustomers() {
	var customers = [];
        var customers_chart = [];
    	for (var i in this.top_customers) {
        	var cust_name = i;
		var usage = this.top_customers[i]["inUse"]
		var customer = {
			"Customer": cust_name,
			"Usage": parseFloat(usage).toFixed(2)+"%"
		}
		var customer_chart = [cust_name, parseFloat(usage).toFixed(2)]
		customers.push(customer)
		customers_chart.push(customer_chart)
	}
	this.customers = customers;
	this.customers_chart = customers_chart;
    }

  }
};
</script>
