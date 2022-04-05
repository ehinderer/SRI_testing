# SRI Testing

This repository contains a compendium of semantics-driven tests for assessing Knowledge Providers (KPs) and Autonomous Relay Agents (ARAs) within the [Biomedical Data Translator](https://ncats.nih.gov/translator).

# Contents of the Repository

The project has two top level folders:

- Modules under [translator](translator) package, containing code shared between all categories of tests.
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

Simply run available [tests](tests) using Pytest within your favorite modality (i.e. CLI, IDE, etc.)
