import { axiosMockAdapterInstance as mock } from "../api.js"
mock.onGet("/users", { params: { searchText: "John" } }).reply(200, {
  users: [{ id: 1, name: "John Smith" }],
});
