# SRI Testing as a Web Service

The Reasoner Validator is available wrapped as a simple (FastAPI-coded) web service.  The service may be run directly or as a Docker container (see below).

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

## Running the Web Service API Directly

The web service application may be run directly as a Python module. It is suggested that a virtual environment first be created (using virtualenv, conda, within your IDE, or equivalent).  Then, certain additional SRI Testing project Python dependencies need to be installed, as follows:

```shell
pip install -r requirements.txt          # non-web dependencies
pip install -r requirements-service.txt  # web service dependencies
```

The module may afterwards be run, as follows:

```shell
python -m api.main
```

Go to  http://localhost/docs to see the service documentation and to use the simple web page to test TRAPI services.
