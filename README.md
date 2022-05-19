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

# SRI Testing Run as a Web Service

The Reasoner Validator is available wrapped as a simple web service.  The service may be run directly or as a Docker container.

## API

The web service has a single POST endpoint `/validate` taking a simple JSON request body, as follows:

```json
{
  "trapi_version": "1.0",
  "biolink_version": "2.2.16",
  "message": "<TRAPI JSON message blob...>"
}
```

The request body consists of JSON data structure with two top level tag:

- An **optional** `trapi_version` tag can be given a value of the TRAPI version against which the message will be validated, expressed as a SemVer string (defaults to 'latest' if omitted; partial SemVer strings are resolved to their 'latest' minor and patch releases). 
- An **optional** `biolink_version` tag can be given a value of the Biolink Model version against which the message knowledge graph semantic contents will be validated, expressed as a SemVer string (defaults to 'latest' Biolink Model Toolkit supported version, if omitted). 
- A **mandatory** `message` tag should have as its value the complete TRAPI **Message** JSON data structure to be validated.

## Running the Web Service Directly

The service may be run directly as a python module. It is suggested that a virtual environment first be created (using virtualenv, conda, within your IDE, or equivalent).  Then, certain Python dependencies need to be installed, as follows:

```shell
pip install -r requirements-service.txt
```

The module may afterwards be run, as follows:

```shell
python -m app.main
```

Go to  http://localhost/docs to see the service documentation and to use the simple UI to input TRAPI messages for validation.

## Running the Web Service within Docker

The Reasoner Validator web service may be run inside a docker container, using Docker Compose.

First, from the root project directory, build the local docker container

```shell
docker-compose build
```

Then, run the service:

```shell
docker-compose up -d
```

Once again, go to  http://localhost/docs to see the service documentation.

To stop the service:

```shell
docker-compose down
```

Of course, the above docker-compose commands may be customized by the user to suit their needs. Note that the docker implementation assumes the use of uvicorn
