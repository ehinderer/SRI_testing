// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import vuetify from "./plugins/vuetify"
import App from './App'
import router from './router'

import { Laue } from 'laue'
Vue.use(Laue)

import VcPiechart from 'vc-piechart'
import 'vc-piechart/dist/lib/vc-piechart.min.css'
Vue.use(VcPiechart)

// TODO: deprecate
import VueVega from 'vue-vega'
Vue.use(VueVega)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  vuetify,
  components: { App },
  template: '<App/>'
})
