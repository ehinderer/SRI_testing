// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'

// autoload plugins
import vuetify from './plugins/vuetify'
import pursue from './plugins/vue-pursue'

import App from './App'
import router from './router'

import { Laue } from 'laue'
import VueVega from 'vue-vega'
import VcPiechart from 'vc-piechart'
import 'vc-piechart/dist/lib/vc-piechart.min.css'

Vue.use(Laue)
Vue.use(VueVega)
Vue.use(VcPiechart)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  vuetify,
  components: { App },
  template: '<App/>'
})
