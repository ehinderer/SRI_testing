# vc-piechart

> Pie and donut chart component for [VueJs](https://vuejs.org/) based on CSS3 conic gradients, created by [Martin Ivanov](https://wemakesites.net).

## Demo

https://vc-piechart.wemakesites.net

## Installation

``
$ npm i vc-piechart --save
``

## Usage

```
// in main.js, use globally
import VcPiechart from 'vc-piechart'
import 'vc-piechart/dist/lib/vc-piechart.min.css'
Vue.use(VcPiechart)

// as a component in another component
import VcPiechart from 'vc-piechart'
import 'vc-piechart/dist/lib/vc-piechart.min.css'

export default {
  name: 'app',
  components: {
    VcPiechart
  }
}
```

```
<vc-piechart :data="data1" />
```

```
<vc-piechart :data="data2" size="12em" :legend="true"  title="Chart 2" :donut="true" :flat="false" />
```

## Props

 - data (Array): chart data (default: []):
 ```javascript
[
  {
    "color": "#f44336",
    "value": 100,
    "label": "Red"
  },
  {
    "color": "#ff9800",
    "value": 123,
    "label": "Orange"
  },
  {
    "color": "#4caf50",
    "value": 456,
    "label": "Green"
  }
]
```
 - size (String): chart's height and width in px, em, etc. default: 256px
 - legend (Boolean): toggle chart's legend element (default: true)
 - title (String): optional chart title (default: null)
 - donut (Boolean): toggle the donut mode (default: false)
 - flat (Boolean): toggle chart's drop-shadow (default: false)

## Repo

https://bitbucket.org/acidmartin/vc-piechart/

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

# run unit tests
npm run unit

# run e2e tests
npm run e2e

# run all tests
npm test
```

For detailed explanation on how things work, checkout the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).

## Credits

Created by [Martin Ivanov](https://wemakesites.net).