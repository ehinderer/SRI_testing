from os import environ, makedirs, listdir
from os.path import sep, normpath
from typing import Dict, Optional, List, Generator

from urllib.parse import quote_plus

import orjson

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from tests.onehop import TEST_RESULTS_DIR, ONEHOP_TEST_DIRECTORY

import logging
logger = logging.getLogger()
logger.setLevel("DEBUG")

RUNNING_INSIDE_DOCKER = environ.get('RUNNING_INSIDE_DOCKER', False)


class TestReportDatabase:
    """
    Abstract Test Report Database superclass
    """
    def __init__(self, **kwargs):
        self.test_run_root_path: str = TEST_RESULTS_DIR  # not a great default value but better than nothing?

    def set_current_report(self, identifier: str):
        """
        Sets the current the report location.

        :return: None
        """
        assert identifier

        self.test_run_root_path = f"{TEST_RESULTS_DIR}{sep}{identifier}"

        # File system based reporting creates a 'test_run_id' named directory for test results
        # This folder may contain the full test results unless a test report database is used
        # in which case, only a Pytest log may be present?
        # TODO: maybe not needed in MongoDatabase version?
        makedirs(self.test_run_root_path, exist_ok=True)

    def get_test_run_root_path(self) -> str:
        return self.test_run_root_path

    def save_json_document(self, document: Dict, document_key: str, is_big: bool = False):
        """
        Saves an indexed document either to a test report database or the filing system.

        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        :return:
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def retrieve_document(self, report_type: str, document_key: str) -> Optional[Dict]:
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def stream_document(self, report_type: str, document_key: str) -> Generator:
        raise NotImplementedError("Abstract method - implement in child subclass!")


class FileReportDatabase(TestReportDatabase):
    """
    Wrapper class for an OS filing system-based repository for storing and retrieving SRI Testing test results.
    """
    def __init__(self, **kwargs):
        """
        :param **kwargs:
        """
        TestReportDatabase.__init__(self, **kwargs)

    def unit_test_report_filepath(self, edge_details_file_path: str) -> str:
        """
        Generate a report file path for a specific unit test result, compiled from descriptive components.

        :return: str, (posix) unit test file path to root name of report file path (*without* file extension)
        """
        path_parts = [TEST_RESULTS_DIR, self._test_run_id] + edge_details_file_path.split('/')

        unit_test_dir_path = sep.join(path_parts[:-1])
        try:
            makedirs(f"{unit_test_dir_path}", exist_ok=True)
        except OSError as ose:
            logger.warning(f"unit_test_report_filepath() makedirs exception: {str(ose)}")

        unit_test_file_path = sep.join(path_parts)

        return unit_test_file_path

    @classmethod
    def get_collections(cls) -> List[str]:
        """
        :return: list of test run identifiers of completed test runs
        """
        # TODO: maybe if a MongoDb is used at the back end, then this handler requires revision?
        test_results_directory = normpath(f"{ONEHOP_TEST_DIRECTORY}/test_results")
        test_run_list = listdir(test_results_directory)
        return test_run_list

    def save_json_document(self, document: Dict, document_key: str, is_big: bool = False):
        """
        Saves an indexed document to the test report filing system. The is_big flag is ignored

        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        :return:
        """
        # we add the file extension '.json' for file system based documents
        test_result_path = self.unit_test_report_filepath(document_key)
        with open(f"{test_result_path}.json", 'w') as document_file:
            orjson.dump(document, document_file, indent=4)

    def _absolute_report_file_path(self, report_file_path: str) -> str:
        assert self.test_run_root_path, "TestReportDatabase(): test_run_root_path not set?!"
        absolute_file_path = normpath(f"{self.test_run_root_path}{sep}{report_file_path}")
        return absolute_file_path

    def retrieve_document(self, report_type: str, document_key: str) -> Optional[Dict]:
        """
        Retrieves a document either from the TestReportDatabase or the local filing system.

        :param report_type: str, label of report type
        :param document_key: key ('path') to the document

        :return: Dict, JSON document as Python object
        """
        assert document_key
        document: Optional[Dict] = None
        document_path: str = self._absolute_report_file_path(document_key)
        try:
            with open(f"{document_path}.json", 'r') as report_file:
                contents = report_file.read()
            if contents:
                document = orjson.loads(contents)
        except OSError as ose:
            logger.warning(f"{report_type} file '{document_key}' not (yet) accessible: {str(ose)}?")

        return document

    def stream_document(self, report_type: str, document_key: str) -> Generator:
        """
        Returns the TRAPI Response file path for given resource component, edge and unit test identities.

        :param report_type: str, label of report type
        :param document_key: key ('path') to the document
        :param test_id: str, target unit test identifier, one of the values noted in the
                             edge leaf nodes of the JSON test run summary (e.g. 'by_subject', etc.).

        :return: str, TRAPI Response text data file path (generated, but not tested here for file existence)
        """
        response_file_path = self._absolute_report_file_path(f"{document_key}.json")
        try:
            with open(response_file_path, mode="rb") as datafile:
                yield from datafile
        except OSError as ose:
            logger.warning(f"{report_type} warning: {response_file_path}' not (yet) accessible: {str(ose)}?")


class MongoReportDatabase(TestReportDatabase):
    """
    Wrapper class for a MongoDb instance-based repository for storing and retrieving SRI Testing test results.
    """
    def __init__(
            self,
            user: str = environ.get('MONGO_INITDB_ROOT_USERNAME', "root"),
            password: str = environ.get('MONGO_INITDB_ROOT_PASSWORD', "example"),
            host: str = "mongo" if RUNNING_INSIDE_DOCKER else "localhost",
            **kwargs
    ):
        """
        TestReportDatabase constructor.

        :param user: str, MongoDb user (default: 'MONGO_INITDB_ROOT_USERNAME' or "root")
        :param password:  str, MongoDb password (default: 'MONGO_INITDB_ROOT_PASSWORD' or "example")
        :param host:  str, MongoDb host (default: "mongo" if inside the SRI Testing docker container else "localhost")
        :param kwargs:

        :raises pymongo.errors.ConnectionFailure
        """
        TestReportDatabase.__init__(self, **kwargs)

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
        self._current_collection: Optional[Collection] = self._sri_testing_db.test_results

    def get_client(self):
        return self._db_client

    def get_database(self):
        return self._sri_testing_db

    def set_current_collection(self, collection_name: str):
        """
        Each test run as its own MongoDb 'Collection', likely named after its 'test_run_id'.

        :param collection_name: str, the name of the Collection to be used as the current collection
        :return: None
        """
        assert collection_name  # should not be an empty string
        self._current_collection = self._sri_testing_db[collection_name]

    def get_current_collection(self) -> Collection:
        """
        :return: current pymongo.collection.Collection for report results
        """
        return self._current_collection

    @classmethod
    def get_collections(cls) -> List[str]:
        """
        :return: list of test run identifiers of completed test runs
        """
        raise NotImplementedError

    def set_current_report(self, identifier: str):
        """
        Sets up the test result location (either a database 'collection' or local test run root directory path)
        :return: None
        """
        TestReportDatabase.set_current_report(self, identifier=identifier)

        # (MongoDb) Database based 'OneHop' test run reporting
        # simply uses the test_run_id as the current Collection name
        self.set_current_collection(identifier)

    def save_json_document(self, document: Dict, document_key: str, is_big: bool = False):
        """
        Saves an indexed document to MongoDb. If the is_big flag is set, then save document as a GridFS file.

        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        """
        # Persist index test run result JSON document suitably indexed by
        # the document_key, into the (wrapped MongoDb) TestReportDatabase
        document["document_key"] = document_key

        if is_big:
            # Save using GridFS?
            raise NotImplementedError
        else:
            test_results: Collection = self.get_current_collection()
            assert test_results  # TODO: sanity check... maybe unnecessary?

            test_results.insert_one(document)

    def retrieve_document(self, report_type: str, document_key: str) -> Optional[Dict]:
        """
        Retrieves a document either from the TestReportDatabase or the local filing system.

        :param report_type: str, label of report type
        :param document_key: key ('path') to the document

        :return: Dict, JSON document as Python object
        """
        assert document_key

        test_results: Collection = self.get_current_collection()
        assert test_results  # TODO: sanity check... maybe unnecessary?

        document: Optional[Dict] = test_results.find_one({'document_key': document_key}, fields={'_id': False})

        return document

    def stream_document(self, report_type: str, document_key: str) -> Generator:
        """
        Returns the TRAPI Response file path for given resource component, edge and unit test identities.

        :param report_type: str, label of report type
        :param document_key: key ('path') to the document
        :param test_id: str, target unit test identifier, one of the values noted in the
                             edge leaf nodes of the JSON test run summary (e.g. 'by_subject', etc.).

        :return: str, TRAPI Response text data file path (generated, but not tested here for file existence)
        """
        # TODO: for reasons of file size scalability, we probably need to stream with MongoDb GridFS here
        raise NotImplementedError
