"""
Registry package
"""

# Setting the following flag to 'True' triggers use of the
# local 'mock' Registry data entries immediately below
MOCK_REGISTRY: bool = False


def mock_registry(status: bool):
    global MOCK_REGISTRY
    MOCK_REGISTRY = status


# This 'mock' registry entry relies a bit on ARAGORN (Ranking Agent)
# and the RENCI Automat KP's, which may sometimes be offline?
MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA = {
    "total": 3,
    "hits": [
        {
            "info": {
                "title": "Unit Test Knowledge Provider 1",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:test-kp-1",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.3.0",
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
                    "infores": "infores:test-kp-2",
                    "team": "Ranking Agent",
                    "biolink-version": "2.4.8"
                },
                "x-trapi": {
                    "version": "1.3.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_2.json"
                }
            }
        },
        #
        # ARA is endpoint broken for now but I need some tests here!
        #
        # {
        #     "info": {
        #         "title": "Unit Test Automatic Relay Agent",
        #         "version": "0.0.1",
        #         "x-translator": {
        #             "infores": "infores:aragorn",
        #             "component": "ARA",
        #             "team": "Ranking Agent",
        #             "biolink-version": "2.2.16"
        #         },
        #         "x-trapi": {
        #             "version": "1.2.0",
        #             "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
        #                                   "tests/onehop/test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
        #         }
        #     }
        # }
    ]
}
