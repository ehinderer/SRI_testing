# SRI Testing

This repository contains a compendium of semantics-driven tests for assessing Knowledge Providers (KPs) and Autonomous Relay Agents (ARAs) within the [Biomedical Data Translator](https://ncats.nih.gov/translator).

# Contents of the Repository

The project has two top level folders:

- Modules under [translator](translator) package, containing code shared between all categories of tests, including some generic TRAPI and Translator Status Dashboard scripts.
- Modules of the actual (Py)test harness under [tests](tests) 

# Getting Started

The tests are recommended to be run using Python 3.9 or better. 

If not running inside a Docker container, the creation of a virtual environment is recommended.

## Python Dependencies

From within your virtual environment, install the indicated Python dependencies in the `requirements.txt` file:

```shell
(venv) $ pip install -r requirements.txt  # or equivalent command
```

## Run the Tests

Simply run available [tests](tests) using Pytest, within your favorite modality (i.e. terminal, favorite IDE, etc.).

# SRI Testing as a Web Service

The SRI Testing Harness may be run as a Web Service. See [here](app/README.md) for more details. 

The SRI Testing web service may also be [run within a Docker Compose managed container](app/README.md#running-the-web-service-within-docker).
