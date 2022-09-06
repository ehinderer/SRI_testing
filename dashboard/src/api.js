/* eslint-disable */
import { PYTEST_REPORT, MOCK_REGISTRY, MOLEPRO_REPORT } from './__mocks__/test_data.js';
import axios, { AxiosRequestConfig } from 'axios';
import AxiosMockAdapter from 'axios-mock-adapter';

var API_HOST = "http://localhost";

const axiosMockInstance = axios.create();
const axiosLiveInstance = axios.create();

// This sets the mock adapter on the default instance
var mock = new AxiosMockAdapter(axiosMockInstance, { delayResponse: 1000 });

// Mock GET request to /users when param `searchText` is 'John'
// arguments for reply are (status, data, headers)
// TEST MOCK
mock.onGet("/users", { params: { searchText: "John" } }).reply(200, {
    users: [{ id: 1, name: "John Smith" }],
});

export const MOCK_TEST_RUN_ID = "2023-13-32_24-61-61"; // an impossible timestamp


// the regexes below are based off the fastapi docs types
// so values which likely ought to be typed as numbers are kept as string matches
// TODO: mention to the SRI_Testing API teams to clarify the intended types

mock
    .onPost(`${API_HOST}/run_tests`, {}).reply(200, {
        test_run_id: MOCK_TEST_RUN_ID,
        errors: null
    })
    .onGet(`${API_HOST}/status/${MOCK_TEST_RUN_ID}`)
    .replyOnce(200, {
        test_run_id: MOCK_TEST_RUN_ID,
        percent_complete: 0
    })
    .onGet(`${API_HOST}/status/${MOCK_TEST_RUN_ID}`)
    .replyOnce(200, {
        test_run_id: MOCK_TEST_RUN_ID,
        percent_complete: 50
    })
    .onGet(`${API_HOST}/status/${MOCK_TEST_RUN_ID}`)
    .reply(200, {
        test_run_id: MOCK_TEST_RUN_ID,
        percent_complete: 100
    })
    .onGet(new RegExp(`${API_HOST}\/status\/[\w_.-]+`)).reply(404, {
        test_run_id: "2022-08-15_18-47-55",
        percent_complete: -1
    })
    .onGet(`${API_HOST}/summary/${MOCK_TEST_RUN_ID}`).reply(200, {
        ...PYTEST_REPORT
    })
    .onGet(new RegExp(`${API_HOST}\/summary\/[\w_.-]+/`)).reply(404, {
        details: "Summary for test run '2022-08-15_18-47-55' is not (yet) available?"
    })
    .onGet(new RegExp(`\/details\/[\w_.-]+\/\[\w_.-]+\/[\w_.-]+\/[\w_.-]+`)).reply(200, function (config) {
        console.log(config)
        return [200, {}]
    });

mock.onGet("/list").reply(200, [MOCK_TEST_RUN_ID])

mock.onGet(`${API_HOST}/registry`).reply(200, MOCK_REGISTRY)

export const axiosMockAdapterInstance = new AxiosMockAdapter(axiosMockInstance, { delayResponse: 1000 }); // this is the wrapper used for developers to add mocking hooks to
// export default process.env.isAxioMock ? axiosMockInstance : axiosLiveInstance; // this is the actual axios instance
export default axiosLiveInstance
