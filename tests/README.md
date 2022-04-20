# Tests

The generic shared elements of the testing framework are unit test validated here:

- [test_biolink_compliance_validation.py](translator/biolink/test_biolink_compliance_validation.py) Version-specific Biolink Model semantic compliance test harness unit tests:
    - **test_check_biolink_model_compliance_of_input_edge:** test of KP data template test input edges validation
    - **test_check_biolink_model_compliance_of_knowledge_graph:** test of TRAP output knowledge graphs validation
- [test_trapi.py](./translator/trapi/test_trapi.py)
    - Validation of ARA and KP provenance (TRAPI attributes, infores id's, etc.)

The above generic elements are used within knowledge source specific, test-data-driven Translator KP and ARA knowledge source tests. The SRI Testing harness current implements the following broad categories of tests:

- ["One Hop" Tests for KPs and ARAs](./onehop/README.md)
