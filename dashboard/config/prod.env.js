'use strict'
const merge = require('webpack-merge')
const dotEnv = require('dotenv').config()

module.exports = merge(dotEnv.parsed, {
  NODE_ENV: '"production"',

})
