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

## Running the Web Service Directly

The service may be run directly as a python module. It is suggested that a virtual environment first be created (using virtualenv, conda, within your IDE, or equivalent).  Then, certain additional SRI Testing project Python dependencies need to be installed, as follows:

```shell
pip install -r requirements-service.txt
```

The module may afterwards be run, as follows:

```shell
python -m app.main
```

Go to  http://localhost/docs to see the service documentation and to use the simple UI to input TRAPI messages for validation.

## Running the Web Service within Docker

The SRI Testing web service may be run inside a docker container, using Docker Compose.

Assuming that you have installed both [Docker (or rather, Docker Desktop)](https://docs.docker.com/get-docker/) and [Docker-Compose](https://docs.docker.com/compose/install/) (Note: Docker Desktop now conveniently installs both...), then the following commands may be run:

First, from the root directory of the project, build the local docker container

```shell
docker-compose build
```

Then, run the service using **Docker Compose**:

```shell
docker-compose up -d
```

Once again, go to  http://localhost/docs to see the service documentation.  Docker logs may be viewed in a streaming fashion by:

```shell
docker-compose logs -f
```

To stop the docker container web service:

```shell
docker-compose down
```

Of course, the above `docker-compose` commands may be overridden by the user to suit their needs. Note that the docker implementation assumes the use of uvicorn (installed as a dependency).
