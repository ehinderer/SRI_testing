from os import environ

from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

import logging
logger = logging.getLogger()
logger.setLevel("DEBUG")

RUNNING_INSIDE_DOCKER = environ.get('RUNNING_INSIDE_DOCKER', False)


class TestReportDatabase:
    """
    Wrapper class for a MongoDb instance storing and retrieving SRI Testing test results.
    """

    def __init__(
            self,
            user: str = environ.get('MONGO_INITDB_ROOT_USERNAME', "root"),
            password: str = environ.get('MONGO_INITDB_ROOT_PASSWORD', "example"),
            host: str = "mongo" if RUNNING_INSIDE_DOCKER else "localhost"
    ):
        """
        TestReportDatabase constructor.

        :param user: str, MongoDb user (default: 'MONGO_INITDB_ROOT_USERNAME' or "root")
        :param password:  str, MongoDb password (default: 'MONGO_INITDB_ROOT_PASSWORD' or "example")
        :param host:  str, MongoDb host (default: "mongo" if inside the SRI Testing docker container else "localhost")

        :raises pymongo.errors.ConnectionFailure
        """
        self._db_uri = "mongodb://%s:%s@%s" % (quote_plus(user), quote_plus(password), host)
        self._db_client = MongoClient(
            host=self._db_uri,  # host: Optional[Union[str, Sequence[str]]] = None,
            port=27017,  # port: Optional[int] = None,
            # document_class: Optional[Type[_DocumentType]] = None,
            # tz_aware: Optional[bool] = None,
            # connect: Optional[bool] = None,
            # type_registry: Optional[TypeRegistry] = None,
            # **kwargs: Any,
        )
        self._db_client.admin.command('ping')  # will through pymongo.errors.ConnectionFailure if the connection fails

        self._sri_testing_db: Database = self._db_client.sri_testing
        self._current_collection: Collection = self._sri_testing_db.test_results

    def get_client(self):
        return self._db_client

    def get_database(self):
        return self._sri_testing_db

    def set_current_collection(self, name: str):
        """
        Each test run as its own MongoDb 'Collection' named after its test_run_id
        :param name: str, the name of the Collection to be used as the current collection
        :return: None
        """
        assert name  # should not be an empty string
        self._current_collection = self._sri_testing_db[name]

    def get_current_collection(self) -> Collection:
        """
        :return: current pymongo.collection.Collection for report results
        """
        return self._current_collection
