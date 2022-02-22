# SRI Testing

This repository contains a compendium of semantics-driven tests for assessing Knowledge Providers (KPs) and Autonomous Relay Agents (ARAs) within the [Biomedical Data Translator](https://ncats.nih.gov/translator).
# Translator Status Dashboard Scripts
Generates data for the Status Dashboard by

# Dependencies

The tests are run using Python 3.6 or better. Creation of a virtual environment is recommended.

## Python Dependencies

From within your virtual environment, install the indicated Python dependencies in the `requirements.txt` file:

```shell
(venv) $ pip install -r requirements.txt  # or equivalent command
```

# Tests

Test suites currently implemented:

- [One Hop Tests for KPs and ARAs](./onehop/README.md)
