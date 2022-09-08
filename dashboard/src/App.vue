<template>
<div>
  <v-app-bar class="app-bar" dense>
    <v-app-bar-title>
      TRAPI Resource Validator
    </v-app-bar-title>
 </v-app-bar>

<v-app>

  <v-container id="page-header">
    <v-row>
      <h1>Run Tests</h1>
    </v-row>
    <v-row no-gutter>
      <v-btn :class="['ml-36']"
             :disabled="loading === true"
             @click="triggerTestRun">Trigger new test run</v-btn>
      <span>&nbsp;&nbsp;</span>
      <span style="{ padding-top: 1px; }">OR</span>
      <span>&nbsp;&nbsp;</span>
      <v-select label="Test Run"
                :items="test_runs_selections"
                :hint="loading === null ? 'Choose a previous test run' : ''"
                v-model="id"
                :disabled="loading === true"
                dense>
      </v-select>


      <v-progress-circular
        v-if="loading"
        color="teal"
        :size="35"
        :width="5"
        :value="status"
        :indeterminate="status < 1">
        {{ status > 0 ? status : '' }}
      </v-progress-circular>

    </v-row>
    <v-row>
    </v-row>
  </v-container>
  <v-container>
    <h1>{{ id }}</h1>
    <h3 v-if="loading === true">This may take a few minutes.</h3>
    <v-tabs v-if="!(loading === null)" v-model="tab">
      <v-tab
        v-for="item in ['Overview', 'Details']"
        :key="item"
        >
        {{ item }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" >
      <v-tab-item
        v-for="item in ['Overview','Details']"
        :key="item"
        >
        <div v-if="tab === 0" >
          <v-container :key="`${id}_overview`" id="page-overview" v-if="loading !== null">
            <!-- <h1>Overview</h1> -->
            <!-- <h2>Summary statistics for different ARAs and KPs</h2> -->
            <v-skeleton-loader
              v-if="loading === true"
              v-bind="attrs"
              type="table"
              ></v-skeleton-loader>

            <div v-else-if="stats_summary !== null && loading === false">
              <h2>Test Results</h2>
              <h3>All providers</h3><br>

              <v-row no-gutter>
                <v-col>
                  <vc-piechart
                    :data="reduced_stats_summary"/>
                </v-col>
                <v-col>
                  <strong style="{ marginBottom: 5px }"># edges vs tests</strong>
                  <la-cartesian narrow stacked
                                :bound="[0]"
                                :data="reduce_provider_by_group(combine_provider_summaries(stats_summary))"
                                :colors="[status_color('passed'), status_color('failed'), status_color('skipped')]"
                                :width="820">
                    <la-bar label="passed" prop="passed" :color="status_color('passed')"></la-bar>
                    <la-bar label="failed" prop="failed" :color="status_color('failed')"></la-bar>
                    <la-bar label="skipped" prop="skipped" :color="status_color('skipped')"></la-bar>
                    <la-x-axis font-size="10" prop="name"></la-x-axis>
                    <la-y-axis></la-y-axis>
                    <la-tooltip></la-tooltip>
                  </la-cartesian>
                </v-col>
              </v-row>
              <div>
                <em>Subject categories</em><br>
                <v-chip-group>
                  <v-chip small outlined v-for="subject_category in Object.entries(countBy(subject_categories))" :key="`${kp}_${subject_category}`">
                    {{ formatCurie(subject_category[0]) }} ({{ subject_category[1] }})
                  </v-chip>
                </v-chip-group>
                <em>Object categories</em><br>
                <v-chip-group>
                  <v-chip small outlined v-for="object_category in Object.entries(countBy(object_categories))" :key="`${kp}_${subject_category}`">
                    {{ formatCurie(object_category[0]) }} ({{ object_category[1] }})
                  </v-chip>
                </v-chip-group>
                <em>Predicates</em><br>
                <v-chip-group>
                  <v-chip small outlined v-for="predicate in Object.entries(countBy(predicates))" :key="`${kp}_${predicate}`">
                    {{ formatCurie(predicate[0]) }} ({{ predicate[1] }})
                  </v-chip>
                </v-chip-group>
              </div>
              <br><h2>ARAs</h2>
              <div v-for="ara in Object.keys(stats_summary['ARA'])" :key="ara">
                <div v-for="kp in Object.keys(stats_summary['ARA'][ara].kps)" :key="kp">
                  <br><h3>{{ ara }}: {{ kp }}</h3><br>

                  <v-row no-gutter>
                    <v-col>
                      <vc-piechart
                        :data="reduce_provider_summary(denormalize_provider_summary(stats_summary['ARA'][ara].kps[kp]))"/>
                    </v-col>
                    <v-col>
                      <strong style="{ marginBottom: 5px }"># edges vs tests</strong>
                      <la-cartesian narrow stacked
                                    :bound="[0]"
                                    :data="Object.entries(stats_summary['ARA'][ara].kps[kp].results).map(el => ({ 'name': el[0], ...el[1]}))"
                                    :colors="[status_color('passed'), status_color('failed'), status_color('skipped')]"
                                    :width="820">
                        <la-bar label="passed" prop="passed" :color="status_color('passed')"></la-bar>
                        <la-bar label="failed" prop="failed" :color="status_color('failed')"></la-bar>
                        <la-bar label="skipped" prop="skipped" :color="status_color('skipped')"></la-bar>
                        <la-x-axis font-size="10" prop="name"></la-x-axis>
                        <la-y-axis></la-y-axis>
                        <la-tooltip></la-tooltip>
                      </la-cartesian>
                    </v-col>
                  </v-row>
                  <div>
                    <em>Subject categories</em><br>
                    <v-chip-group>
                      <v-chip small outlined v-for="subject_category in Object.entries(countBy(categories_index[`${ara}_${kp}`].subject_category))" :key="`${ara}_${kp}_${subject_category}`">
                        {{ formatCurie(subject_category[0]) }} ({{ subject_category[1] }})
                      </v-chip>
                    </v-chip-group>
                    <em>Object categories</em><br>
                    <v-chip-group>
                      <v-chip small outlined v-for="object_category in Object.entries(countBy(categories_index[`${ara}_${kp}`].object_category))" :key="`${ara}_${kp}_${object_category}`">
                        {{ formatCurie(object_category[0]) }} ({{ object_category[1] }})
                      </v-chip>
                    </v-chip-group>
                    <em>Predicates</em><br>
                    <v-chip-group>
                      <v-chip small outlined v-for="predicate in Object.entries(countBy(categories_index[`${ara}_${kp}`].predicate))" :key="`${ara}_${kp}_${predicate}`">
                        {{ formatCurie(predicate[0]) }} ({{ predicate[1] }})
                      </v-chip>
                    </v-chip-group>
                  </div>
                </div>
              </div>

              <br><h2>KPs</h2>
              <div v-for="kp in Object.keys(stats_summary['KP'])" :key="kp" v-if="categories_index !== null && categories_index !== {}" >
                <br><h3>{{ kp }}</h3><br>
                <v-row no-gutter>
                  <v-col>
                    <vc-piechart
                      :data="reduce_provider_summary(denormalize_provider_summary(stats_summary['KP'][kp]))"/>
                  </v-col>
                  <v-col>
                    <strong style="{ marginBottom: 5px }"># edges vs tests</strong>
                    <la-cartesian narrow stacked
                                  :bound="[0]"
                                  :data="Object.entries(stats_summary['KP'][kp].results).map(el => ({ 'name': el[0], ...el[1]}))"
                                  :width="820"
                                  :colors="[status_color('passed'), status_color('failed'), status_color('skipped')]">
                      <la-bar label="passed" prop="passed" :color="status_color('passed')"></la-bar>
                      <la-bar label="failed" prop="failed" :color="status_color('failed')"></la-bar>
                      <la-bar label="skipped" prop="skipped" :color="status_color('skipped')"></la-bar>
                      <la-x-axis font-size="10" prop="name"></la-x-axis>
                      <la-y-axis></la-y-axis>
                      <la-tooltip></la-tooltip>
                    </la-cartesian>
                  </v-col>
                </v-row>
                <div>
                  <em>Subject categories</em><br>
                  <v-chip-group>
                    <v-chip small outlined v-for="subject_category in Object.entries(countBy(categories_index[kp].subject_category))" :key="`${kp}_${subject_category}`">
                      {{ formatCurie(subject_category[0]) }} ({{ subject_category[1] }})
                    </v-chip>
                  </v-chip-group>
                  <em>Object categories</em><br>
                  <v-chip-group>
                    <v-chip small outlined v-for="object_category in Object.entries(countBy(categories_index[kp].object_category))" :key="`${kp}_${object_category}`">
                      {{ formatCurie(object_category[0]) }} ({{ object_category[1] }})
                    </v-chip>
                  </v-chip-group>
                  <em>Predicates</em><br>
                  <v-chip-group>
                    <v-chip small outlined v-for="predicate in Object.entries(countBy(categories_index[kp].predicate))" :key="`${kp}_${predicate}`">
                      {{ formatCurie(predicate[0]) }} ({{ predicate[1] }})
                    </v-chip>
                  </v-chip-group>
                </div>
              </div>
            </div>
          </v-container>
        </div>

        <div v-if="tab === 1">
          <v-container :key="`${id}_details` "id="page-details" v-if="loading !== null">
            <!-- <h1>Details</h1> -->
            <!-- <h2>Individual test results by Provider and Biolink Category</h2> -->
            <v-row v-if="loading !== null" no-gutter>
              <v-col v-if="loading === true">
                <v-skeleton-loader
                  v-bind="attrs"
                  type="table"
                  ></v-skeleton-loader>
              </v-col>
              <v-col v-else-if="loading === false">
                <!-- <v-text-field -->
                <!--   v-model="search" -->
                <!--   append-icon="mdi-magnify" -->
                <!--   label="Search" -->
                <!--   single-line -->
                <!--   hide-details -->
                <!--   ></v-text-field> -->
                <v-row no-gutter>
                  <v-col sl>
                    <v-select label="Filter for subject categories"
                              multiple
                              :items="subject_categories"
                              v-model="subject_category_filter"/>
                  </v-col>
                  <v-col sl>
                    <v-select label="Filter for predicates"
                              multiple
                              :items="predicates"
                              v-model="predicate_filter"/>
                  </v-col>
                  <v-col sl>
                    <v-select label="Filter for object categories"
                              multiple
                              :items="object_categories"
                              v-model="object_category_filter"/>
                  </v-col>
                  <v-col lg>
                    <v-radio-group
                      v-model="outcome_filter"
                      row>
                      <v-radio
                        label="All"
                        value="all"
                        ></v-radio>
                      <v-radio
                        label="Pass"
                        value="passed"
                        ></v-radio>
                      <v-radio
                        label="Fail"
                        value="failed"
                        ></v-radio>
                      <v-radio
                        label="Skip"
                        value="skipped"
                        ></v-radio>
                    </v-radio-group>
                  </v-col>
                </v-row>

                <v-data-table
                  :headers="_headers"
                  :items="kp_selections.length > 0 || ara_selections.length > 0 ?
                          denormalized_cells
                          .filter(cell => kp_selections.some(el =>
                          (el.includes(cell._id)
                          || kps_only ? el.includes(cell._id.split('|')[0]) || el.includes(cell._id.split('|')[1]) : false)
                          || ara_selections.some(el => el.includes(cell._id.split('|')[0]) || el.includes(cell._id.split('|')[1]))))
                          : denormalized_cells"
                  :items-per-page="-1"
                  group-by="_id"
                  class="elevation-1"
                  :search="search"
                  :custom-filter="searchMatches"
                  dense>
                  <template v-slot:item="{ item }">
                    <tr>
                      <td v-for="[test, result] in Object.entries(omit('_id')(item))"
                          v-bind:key="`${hash([test, result])}`"
                          :style="cellStyle(result.status)">

                        <v-tooltip
                          v-if="!!result.status"
                          :max-width="480"
                          bottom>
                          <template v-slot:activator="{ on, attrs }">
                            <div v-bind="attrs" v-on="on">
                              <router-link :to="{ name: 'about_test', params: { id: item['_id'],  idx: item['idx'], test: test } }">
                                {{ stateIcon(result.status) }} ({{ result.messages.length }})
                              </router-link>
                            </div>
                          </template>
                          <span>
                            {{test}}
                            <ul>
                              <li v-for="message in result.messages" :key="message">
                                {{ message }}
                              </li>
                            </ul>
                          </span>
                        </v-tooltip>

                        <span v-else-if="test === 'spec'">
                          <v-tooltip
                            bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <div v-bind="attrs" v-on="on">
                                <v-chip small outlined>{{formatCurie(result.subject_category)}}</v-chip>--<v-chip small outlined>{{formatCurie(result.predicate)}}</v-chip>-><v-chip small outlined>{{formatCurie(result.object_category)}}</v-chip>
                              </div>
                            </template>
                            <b>Test Edge:</b>
                            <span>
                              ({{result.subject}})--[{{result.predicate}}]->({{result.object}})<br>
                            </span>
                          </v-tooltip>
                        </span>

                        <span v-else>
                {{ stateIcon(result.status) }}
              </span>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-col>
    </v-row>
   </v-container>
    </div>

    </v-tab-item>
  </v-tabs-items>
  </v-container>
<div id="app">
</div>
</v-app>
</div>
</template>

<script>
/* eslint-disable */

import jp from 'jsonpath';
import jsonQuery from 'json-query';
import hash from "object-hash";

import omit from "lodash.omit";
import pick from "lodash.pick";
import matches from "lodash.matches";
import { isObject, isArray, isString, sortBy } from "lodash";
import * as _ from "lodash";

// Visualization
import VcPiechart from "vc-piechart";
import 'vc-piechart/dist/lib/vc-piechart.min.css';
import { Cartesian, Line, Bar } from 'laue'

// API code in separate file so we can switch between live and mock instance,
// also configure location for API in environment variables and build variables
import axios, { MOCK_TEST_RUN_ID } from "./api.js";
import { PYTEST_REPORT, MOLEPRO_REPORT } from "./__mocks__/test_data.js";

const API_HOST = "http://localhost";
// const MOCK = process.env.isAxiosMock;
const MOCK = false;

export default {
  name: 'App',
  components: {
    VcPiechart,
    LaCartesian: Cartesian,
    LaBar: Bar,
  },
  data() {
    return {
      API_HOST: API_HOST,
      MOCK: MOCK,
      hover: false,
      id: null,
      loading: null,
      headers: [],
      cells: [],
      edges: [],
      tests: [],
      token: null,
      search: '',
      tab: '',
      registryResults: [],
      kp_selections: [],
      ara_selections: [],
      test_runs_selections: [],
      kps_only: true,
      status_interval: -1,
      status: -1,
      outcome_filter: "all",
      predicate_filter: [],
      subject_category_filter: [],
      object_category_filter: [],
      index: null,
      stats_summary: null,
      subject_categories: [],
      object_categories: [],
      predicates: [],
      categories_index: null,
    }
  },
  async created () {
    // initialize application
    await axios.get(`${API_HOST}/test_runs`).then(response => {
      this.test_runs_selections = response.data.test_runs;
    })
    // Mock initialization
    if (MOCK) {
      await axios.post(`${API_HOST}/run_tests`, {}).then(response => {
        this.id = response.data.test_run_id;
        axios.get(`${API_HOST}/test_runs`).then(response => {
          this.test_runs_selections = response.data.test_runs;
        })
      })
    }

  },
  watch: {
    id(id, oldId) {
      this.loading = true;
      this.status_interval = setInterval(() => axios.get(`${API_HOST}/status?test_run_id=${id}`).then(response => {
        this.status = response.data.percent_complete;
        if (this.status >= 100) {
          window.clearInterval(this.status_interval)
        }
      }), 3000);
    },
    status(newStatus, oldStatus) {
      if (newStatus >= 100 && (this.headers.length === 0 && this.cells.length === 0)) {
        axios.get(`${API_HOST}/index?test_run_id=${this.id}`).then(response => {
          this.index = response.data.summary;
        })
        axios.get(`${API_HOST}/summary?test_run_id=${this.id}`).then(response => {
          this.stats_summary = response.data.summary;
        })
        this.loading = false;
        this.status = -1;
      }
    },
    index(newIndex, oldIndex) {
      if (!!newIndex) {
        this.makeTableData(this.id)
        this.getAllCategories(this.id, newIndex);
      };
    }
  },
  computed: {
    all_categories() {
      if (!!this.id) {
        return this.getAllCategories(this.id, this.index)
      } else {
        return {
          subject_categories: [],
          object_categories: [],
          predicates: [],
        }
      }
    },
    denormalized_stats_summary() {
      if (this.stats_summary !== null) {
        console.info("updating normalized_stat_summary", this.stats_summary)
        const combined_results = {
          ...this.stats_summary.KP,
          // TODO reduce across keys in 'kp'; split the denormalization below between KP and ARA then concat
          //...this.stats_summary.ARA,
        };
        return Object.keys(combined_results)
                     .flatMap(provider_key => this.denormalize_provider_summary(combined_results[provider_key], provider_key));
      } else {
        return [];
      }
    },
    reduced_stats_summary() {
      return this.reduce_provider_summary(this.denormalized_stats_summary)
    },
    registryItems() {
      return this.registryResults.map(el => {
        return {
          text: el.info.title,
          value: el.info["x-translator"].infores,
          component: el.info["x-translator"].component
        }
      })
    },
    _headers() {
      return this.headers.map(el => ({
        text: el,
        value: el,
        filterable: true,
        sortable: true,
        sort: (a, b) => {
          if (!!a.status && !!b.status)
            return a.status.localeCompare(b.status)
          if (!!a.spec && !!b.spec)
            return `${a.spec.subject}--${a.spec.predicate}->${a.spec.object}`.localeCompare(`${b.spec.subject}--${b.spec.predicate}->${b.spec.object}`)
          else
            return a - b;
        }
      }))
    },
    denormalized_cells() {
      // TODO: eliminate
      const denormalize_result = (result) => {
        const denormalized_result = ["outcome"]
              .some(status => Object.keys(result).includes(status)) ?
              {
                status: result.outcome,
                messages: result.errors
              }
              : result;
        return denormalized_result;
      }
      const _cells = this.cells.map(el => {
        const cell = Object.entries(JSON.parse(JSON.stringify(el)))
        const _el = Object.fromEntries(
          cell.map(
            entry => [
              entry[0],
              denormalize_result(entry[1])
            ]
          )
        )
        return _el;
      })
      const __cells = _cells.map(el => ({
        ...Object.fromEntries(this.headers.map(header => [header, {
          status: null,
          messages: []
        }])),
        ...el,
      }))
      return __cells
        .filter(el => !isString(el))
      // TODO: combine into one loop
        .filter(cell => Object.entries(cell).some(entry => this.outcome_filter !== "all" ? entry[1].status === this.outcome_filter : true))
        .filter(el => {
          return this.subject_category_filter.length > 0 ? this.subject_category_filter.includes(el.spec.subject_category) : true
            && this.predicate_filter.length > 0 ? this.predicate_filter.includes(el.spec.predicate) : true
            && this.object_category_filter > 0 ? this.object_category_filter.includes(el.spec.object_category) : true
        });
    }
  },
  methods: {
    async triggerTestRun() {
      axios.post(`${API_HOST}/run_tests`, {}).then(response => {
        this.id = response.data.test_run_id;
      }).then(() => {
        // refresh the test runs list
        axios.get(`${API_HOST}/test_runs`).then(response => {
          this.test_runs_selections = response.data.test_runs;
        })
      })
    },
    status_color: (status) => status === "passed" ? "#00ff00"
      : status === "skipped" ? "#f0e68c"
      : status === "failed" ? "#f08080"
      : "#000000",
    denormalize_provider_summary(provider_summary, provider_key) {
      return Object.entries(provider_summary.results)
                   .flatMap((([field, value]) => Object.keys(value)
                                                       .map(i => [provider_key, field, i, value[i]])))
                   .map(item => ({
                     'provider': item[0],
                     'test': item[1],
                     'label': item[2],
                     'value': item[3]
                   }))
    },
    combine_provider_summaries(provider_summary) {
      const denormalized_kps = Object.keys(provider_summary.KP).flatMap(kp => Object.entries(provider_summary.KP[kp].results).map(el => ({ 'name': el[0], ...el[1]})))
      const denormalized_aras = Object.keys(provider_summary.ARA).flatMap(ara => {
        return Object.keys(provider_summary.ARA[ara].kps).flatMap(kp => Object.entries(provider_summary.KP[kp].results).map(el => ({ 'name': el[0], ...el[1]})))
      })
      return [...denormalized_kps, ...denormalized_aras];
    },
    reduce_provider_summary(denormalized_provider_summary) {
      const tally = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
      };
      denormalized_provider_summary.forEach(({ label, value }) => {
        tally[label] += value;
      });
      return Object.entries(tally).map(([label, value]) => ({
        label,
        value,
        color: this.status_color(label)
      }))
    },
    reduce_provider_by_group(data) {
      const ans = _(data)
            .groupBy('name')
            .map((obj, id) => ({
              name: id,
              passed: _.sumBy(obj, 'passed'),
              failed: _.sumBy(obj, 'failed'),
              skipped: _.sumBy(obj, 'skipped'),
            }))
            .value()
      return ans
    },
    async getAllCategories(id, index) {
      const categories = {
        subject_category: [],
        predicate: [],
        object_category: [],
      };
      const addFromKPs = (id, kpSummary) => {
        Object.values(kpSummary).forEach(el => {

          if (isObject(el)) {

            let pre_categories_index = _.clone(this.categories_index);

            if (pre_categories_index === null) {
              pre_categories_index = {};
            }
            if (!!!pre_categories_index[id]) {
              pre_categories_index[id] = {};
              pre_categories_index[id].subject_category = [];
              pre_categories_index[id].object_category = [];
              pre_categories_index[id].predicate = [];
            }

            pre_categories_index[id].subject_category.push(el.test_data.subject_category);
            pre_categories_index[id].predicate.push(el.test_data.predicate);
            pre_categories_index[id].object_category.push(el.test_data.object_category);
            this.categories_index = pre_categories_index;

            categories.subject_category.push(el.test_data.subject_category)
            categories.predicate.push(el.test_data.predicate)
            categories.object_category.push(el.test_data.object_category)
          }
        });

      }
      index.KP.forEach(async kp_id => {
        await axios.get(`${API_HOST}/resource?test_run_id=${id}&kp_id=${kp_id}`)
                   .then(this.tap)
                   .then(response => addFromKPs(kp_id, response.data.summary))
      });
      Object.keys(index.ARA)
            .forEach(ara_id => {
              index.ARA[ara_id].forEach(async kp_id => {
                await axios.get(`${API_HOST}/resource?test_run_id=${id}&kp_id=${kp_id}&ara_id=${ara_id}`)
                           .then(response => addFromKPs(`${ara_id}_${kp_id}`, response.data.summary))
              })
           });
      // set the state directly for async updates
      // TODO: turn into incremental?
      this.subject_categories = categories.subject_category;
      this.object_categories = categories.object_category;
      this.predicates = categories.predicate;
      return categories;
    },
    async makeTableData(id) {
      // TODO: refactor to use index
      const report = axios.get(`${API_HOST}/summary?test_run_id=${id}`)
                          .then(response => {
                            const kp_details = Object.entries(response.data.summary.KP).map(([resource_id, value]) => {
                              return axios.get(`${API_HOST}/resource?test_run_id=${this.id}&kp_id=${resource_id}`).then(el => {
                                return {
                                  resource_id,  // inject the resource_id into the response
                                  ...el,
                              }
                          })
                      });
                      const ara_details = Object.entries(response.data.summary.ARA).map(([resource_id, value]) => {
                          return Object.keys(value.kps)
                              .map(key => axios.get(`${API_HOST}/resource?test_run_id=${this.id}&ara_id=${resource_id}&kp_id=${key}`)
                                   .then(el => {
                                       return {
                                           resource_id: `${resource_id}>${key}`,
                                           ...el,
                                       }
                                   }))
                      });
                      return Promise.all(
                          [...kp_details, ...ara_details.flatMap(i=>i)]
                              .map(p => p
                                   .then(value => ({
                                       status: "fulfilled",
                                       value
                                   }))
                                   .then(response => {
                                       if (response.status === "fulfilled") {
                                           const { headers, cells, edges, tests } = makeTableData(response.value.resource_id, response.value.data.summary);
                                           this.headers = Array.from(new Set(this.headers.concat(headers)));
                                           this.cells = this.cells.concat(cells);
                                       }
                                   })
                                   .catch(reason => ({
                                       status: "rejected",
                                       reason
                                   })))
                      )

                  })
                  .then(responses => {
                    this.loading = false;
                    this.status = -1;
                  });
        },

    // import methods from packages
        hash,
        isObject,
        countBy: _.countBy,

        // custom methods for application
        tap: a => { console.log("hello", a); return a },

        // test: get a new test token and subscribe to the results
        // must also change the "loading" state for the table
        test: () => {},
        omit: (...keys) => object => omit(object, keys),
        pick: (...keys) => object => pick(object, keys),
        notEmpty: (list) => list.filter(el => el !== ""),

        // `custom-filter` in v-data-table props: https://vuetifyjs.com/en/api/v-data-table/#props
        searchMatches: _searchMatches,

        // adjust cell style:
        // TODO - move on to use style classes instead
        cellStyle (state) {
            // getComputedStyle(document.querySelector("td")).backgroundColor

            let color = "black";
            let backgroundColor = "none";
            if (state === "passed" || state=== "failed") {
              color = "white";
              backgroundColor = this.status_color(state);
            } else if (state === "skipped") {
              backgroundColor = this.status_color(state);
            }
            return {
                color,
                backgroundColor,
                borderLeft: 'solid 1px white',
                borderRight: 'solid 1px white'
            }
        },
        stateIcon (state) {
            if (state === "passed") {
                return `✅ Pass`
            } else if (state === "skipped") {
                return `⚠️ Skip`
            } else if (state === "failed") {
                return `🚫 Fail`
            } else if (state === null) {
                return "NONE";
            }
            return state
        },
        formatEdge (result) {
            return `(${this.formatCurie(result.subject_category)})--[${this.formatCurie(result.predicate)}]->(${this.formatCurie(result.object_category)})`
        },
        formatCurie (curie) {
            return curie.split(':')[1];
        }

    }
}

// jsonpath
// queries based on schema circa Aug 5th 2022
const query_all_tests = "$.*..tests";
const query_all_results = "$.*.*.*";
const query_all_kp_results = "$.KP.*.*";
const query_all_ara_results = "$.ARA.*.*";

// recursive search function for matching string against *any* value within *any* object, array, or string within an object's hierarchy
// this behavior might require fine-tuning (should messages be searchable? should property matches be advertised?) but it's a first-pass
// for understanding what we want from our table search filtering
function _searchMatches(value, search, item) {
    return Object.entries(item).some(([key, entry]) => {
        if (isObject(entry)) {
            return _searchMatches(entry, search, entry)
        } else if (isArray(entry)) {
            return entry.some(el => _searchMatches(el, search, el))
        } else if (isString(entry)) {
            return key.toLowerCase().includes(search.toLowerCase()) || entry.toLowerCase().includes(search.toLowerCase());
        }
    })
}


function makeTableData(resource_id, report) {
    const test_results = jp.nodes(report, "$.*").filter(el => !el.path.includes("document_key"))
    const headers = Array.from(test_results.reduce((acc, item) => {
        const { test_data, results } = item.value;
        if (!!results) Object.keys(results).forEach(key => acc.add(key));    // fields
        // Object.keys(test_data).forEach(key => acc.add(key));  // edges
        return acc;
    }, new Set(["spec"])));
    const cells = test_results.reduce((acc, item) => {
        const { test_data, results } = item.value;
        acc.push({
            _id: resource_id,
            spec: test_data,
            ...results,
        })
        return acc;
    }, []);
    return {
        id: report.test_run_id,
        headers,
        cells,
    };
}

</script>

<style>
#app {
     font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    padding: 1%;
}
.app-bar {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
}

tr {
  margin-top: 5px;
}
th > span {
    text-align: center;
}
tr.v-row-group__header > td.text-start > button > span > i.mdi-close {
    display: none;
}
.v-tooltip__content {
    background: rgb(97,97,97);
    opacity: 1.0;
}

</style>
