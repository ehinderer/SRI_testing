# SRI Testing

This repository contains a compendium of semantics-driven tests for assessing Knowledge Providers (KPs) and Autonomous Relay Agents (ARAs) within the [Biomedical Data Translator](https://ncats.nih.gov/translator).

# Contents of the Repository

The project has two top level folders:

- Modules under [translator](translator) package, containing code shared between all categories of tests, including some generic TRAPI and Translator Status Dashboard scripts.
- Modules of the actual (Py)test harness under [tests](tests) 

# Getting Started

The tests are run using Python 3.7 or better. Creation of a virtual environment is recommended.

A portion of the test suite may be operating system aware. The tests are not guaranteed to work properly under Microsoft Windows.

## Python Dependencies

From within your virtual environment, install the indicated Python dependencies in the `requirements.txt` file:

```shell
(venv) $ pip install -r requirements.txt  # or equivalent command
```

## Run the Tests

Simply run available [tests](tests) using Pytest within your favorite modality (i.e. CLI, IDE, etc.). 

For specific tests like the 'onehops' test harness, available options may be seen by typing:

```shell
pytest tests/onehop/test_onehops.py --help
```

which include SRI Testing-specific custom options:

```
  --teststyle=TESTSTYLE
                        Which Test to Run?
  --one                 Only use first edge from each KP file
  --triple_source=TRIPLE_SOURCE
                        'REGISTRY', directory or file from which to retrieve triples.
                        (Default: 'REGISTRY', which triggers the use of metadata, in KP entries
                        from the Translator SmartAPI Registry, to configure the tests).
  --ARA_source=ARA_SOURCE
                        'REGISTRY', directory or file from which to retrieve ARA Config.
                        (Default: 'REGISTRY', which triggers the use of metadata, in ARA entries
                        from the Translator SmartAPI Registry, to configure the tests).
  --TRAPI_Version=TRAPI_VERSION
                        TRAPI API Version to use for the tests 
                        (Default: latest public release  or REGISTRY metadata value).
  --Biolink_Release=BIOLINK_RELEASE
                        Biolink Model Release to use for the tests
                        (Default: latest Biolink Model Toolkit default or REGISTRY metadata value).
```

Such options include one
