# Tests

The generic shared elements of the testing framework are unit test validated here:

- [test_trapi.py](./translator/trapi/test_trapi.py)
    - Validation of ARA and KP provenance (TRAPI attributes, infores id's, etc.)

The above generic elements are used within knowledge source specific, test-data-driven Translator KP and ARA knowledge source tests. The SRI Testing harness current implements the following broad categories of tests:

- ["One Hop" Tests for KPs and ARAs](./onehop/README.md)
