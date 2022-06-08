"""
Registry package
"""

# As of June 2022, the Translator SmartAPI Registry doesn't yet
# have significant compliant test_data_locations for KPs and ARAs,
# so we'll start by simulating this for now, with mock registry metadata
# (dereferencing test data in the SRI Testing project repository)
#
#
# Setting the followin flag triggers use of this local 'mock' data
MOCK_REGISTRY: bool = True
MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA = {
    "total": 3,
    "hits": [
        {
            "info": {
                "title": "Unit Test Knowledge Provider 1",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:panther",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Knowledge Provider 2",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:ontological-hierarchy",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_2.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Automatic Relay Agent",
                "version": "0.0.1",
                "x-translator": {
                    "infores": "infores:aragorn",
                    "component": "ARA",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
                }
            }
        }
    ]
}
