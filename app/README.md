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
pip install -r requirements.txt          # non-web dependencies
pip install -r requirements-service.txt  # web service dependencies
```

The module may afterwards be run, as follows:

```shell
python -m app.main
```

Go to  http://localhost/docs to see the service documentation and to use the simple UI to input TRAPI messages for validation.

## Running the Web Service within Docker

The SRI Testing web service may be run inside a docker container, using Docker Compose.

Assuming that you have installed both [Docker (or rather, Docker Desktop)](https://docs.docker.com/get-docker/) and [Docker-Compose](https://docs.docker.com/compose/install/) (Note: Docker Desktop now conveniently installs both...), then the following commands may be run from the root folder of the project:

### Database for the Test Results

You will generally want to have the backend persist its test results in a MongoDb database(*), so first start up a Mongo instance as so:

```shell
docker-compose -f run-mongodb.yaml up -d
```

Note that the application will default to use the filing system for its test run under a local **results** directory, if the MongoDb container is not running.  The application will start a bit more slowly in such a situation as it awaits the timeout of the attempted connection to a MongoDb database.

If the database is running, the Mongo-Express container may be run to look at it:

```shell
docker-compose -f run-mongodb-monitor.yaml up -d
```

Mongo-Express web page is available at http://localhost:8081.  It is generally not a good idea to run this on a production server.

# Testing Engine and Web Dashboard

Next, build then start up the services consisting of Docker containers for the testing dashboard and backend engine - defined in the default _Dockerfile_ - using **Docker Compose**, by the root directory of the project, build the local docker container

```shell
docker-compose build
docker-compose up -d
```

Once again, go to  http://localhost/docs to see the service documentation.  Docker logs may be viewed in a streaming fashion by:

```shell
docker-compose logs -f
```

To stop the Docker containers:

```shell
docker-compose down
docker-compose -f run-mongodb.yaml down
```

Of course, the above `docker-compose` commands may be overridden by the user to suit their needs. Note that the docker implementation assumes the use of uvicorn (installed as a dependency).
