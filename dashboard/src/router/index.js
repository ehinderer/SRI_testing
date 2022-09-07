import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

// TODO: Eliminate
const Home = { template: '<div>Home {{ $route.params.id }} </div>' }
const About = { template: '<div>About {{ $route.params.id }} </div>' }

export default new Router({
  routes: [
    { path: '/', component: Home },
    { path: '/about/:id', component: About, name: 'about' },
    { path: '/about/:id/:test', name: 'about_test', component: About }
  ]
})
