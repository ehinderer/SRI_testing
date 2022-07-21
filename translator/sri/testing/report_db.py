import shutil
from os import environ, makedirs, listdir
from os.path import sep, normpath
from typing import Dict, Optional, List, Generator
from datetime import datetime
from urllib.parse import quote_plus

import json
import orjson

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

# for saving big MongoDb files
from gridfs import GridFS

from tests.onehop import TEST_RESULTS_DIR

import logging
logger = logging.getLogger()
logger.setLevel("DEBUG")

RUNNING_INSIDE_DOCKER = environ.get('RUNNING_INSIDE_DOCKER', False)


class TestReport:
    """
    Abstract superclass of a Test Report, which is a related
    collection of test run documents stored in a TestReportDatabase.
    """
    def __init__(self, identifier: str):
        assert identifier  # the test report 'identifier' should not be None or empty string
        self._report_identifier = identifier
        self._report_root_path = f"{TEST_RESULTS_DIR}{sep}{identifier}"

    def get_identifier(self) -> str:
        return self._report_identifier

    def get_root_path(self) -> str:
        return self._report_root_path

    def delete(self):
        """
        Delete internal representation of the report.
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def save_json_document(
            self,
            document_type: str,
            document: Dict,
            document_key: str,
            is_big: bool = False
    ):
        """
        Saves an indexed document either to a test report database or the filing system.

        :param document_type: Dict, Python object to persist as a JSON document.
        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def retrieve_document(self, document_type: str, document_key: str) -> Optional[Dict]:
        """
        Retrieves a single report type of document, corresponding to a specified document key.

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Dict, JSON document retrieved.
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def stream_document(self, document_type: str, document_key: str) -> Generator:
        """
        Retrieves a single report type of document, corresponding to a specified document key.

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Generator, generator of streamed JSON document text
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")


class TestReportDatabase:
    """
    Abstract superclass of a Test Report Database
    """
    def __init__(self, **kwargs):
        pass

    def get_test_report(self, identifier: str) -> TestReport:
        """
        :return: TestReport of the appropriate kind for the given type of TestReportDatabase
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def delete_test_report(self, report: TestReport):
        """
        :param report: TestReport, to be deleted
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    @classmethod
    def get_available_reports(cls) -> List[str]:
        """
        :return: list of identifiers of available ('completed') reports.
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")


class FileTestReport(TestReport):

    def __init__(self, identifier: str):
        TestReport.__init__(self, identifier=identifier)

        # File system based reporting needs to create a
        # 'identifier' tagged directory for test results
        makedirs(self.get_root_path(), exist_ok=True)

    def delete(self):
        test_report_directory = normpath(self.get_root_path())
        shutil.rmtree(test_report_directory)

    def get_absolute_file_path(self, document_key: str, create_path: bool = False) -> str:
        """
        Gets the absolute path of a given relative file path, creating the path of directories if indicated.

        :param document_key: str, the relative (Posix?) directory path for a given file
        :param create_path: bool, if True, then ensure that the intermediate directories of the path are created
        :return: str, absolute path of a given relative file path
        """
        absolute_file_path = normpath(f"{self.get_root_path()}{sep}{document_key}")
        if create_path:
            dir_path: str = sep.join(absolute_file_path.split(sep=sep)[:-1])
            try:
                makedirs(f"{dir_path}", exist_ok=True)
            except OSError as ose:
                logger.warning(
                    f"get_absolute_file_path() directory path '{dir_path}' could not be created? Exception: {str(ose)}"
                )
        return absolute_file_path

    def save_json_document(
            self,
            document_type: str,
            document: Dict,
            document_key: str,
            is_big: bool = False
    ):
        """
        Saves an indexed document either to a test report database or the filing system.

        :param document_type: Dict, Python object to persist as a JSON document.
        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        """
        # for consistency relative to MongoTestReports, we add the document key to the document
        document["document_key"] = document_key

        document_path = self.get_absolute_file_path(document_key=document_key, create_path=True)
        try:
            with open(f"{document_path}.json", 'w') as document_file:
                json.dump(document, document_file, indent=4)
        except OSError as ose:
            logger.warning(f"{document_type} '{document_key}' cannot be written out: {str(ose)}?")

    def retrieve_document(self, document_type: str, document_key: str) -> Optional[Dict]:
        """
        Retrieves a single report type of document, corresponding to a specified document key.

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Dict, JSON document retrieved.
        """
        assert document_key
        document: Optional[Dict] = None
        document_path: str = self.get_absolute_file_path(document_key=document_key)
        try:
            with open(f"{document_path}.json", 'r') as report_file:
                contents = report_file.read()
            if contents:
                document = orjson.loads(contents)
        except OSError as ose:
            logger.warning(f"{document_type} '{document_key}' is not (yet) accessible: {str(ose)}?")

        return document

    def stream_document(self, document_type: str, document_key: str) -> Generator:
        """
        Retrieves a single report type of document, corresponding to a specified document key.

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Generator, generator of streamed JSON document text
        """
        document_path = self.get_absolute_file_path(document_key)
        try:
            with open(f"{document_path}.json", mode="rb") as datafile:
                yield from datafile
        except OSError as ose:
            logger.warning(f"{document_type} '{document_key}' is not (yet) accessible: {str(ose)}?")


class FileReportDatabase(TestReportDatabase):
    """
    Wrapper class for an OS filing system-based repository for storing and retrieving SRI Testing test results.
    """
    def __init__(self, **kwargs):
        TestReportDatabase.__init__(self, **kwargs)

    def get_test_report(self, identifier: str) -> TestReport:
        """
        :param identifier: str, test run identifier for the report
        :return: wrapped test report
        """
        report = FileTestReport(identifier=identifier)
        return report

    def delete_test_report(self, report: TestReport):
        """
        :param report: TestReport to be deleted
        """
        report.delete()

    @classmethod
    def get_available_reports(cls) -> List[str]:
        """
        :return: list of identifiers of available reports.
        """
        test_results_directory = normpath(TEST_RESULTS_DIR)
        test_run_list = listdir(test_results_directory)
        return test_run_list


class MongoTestReport(TestReport):

    def __init__(self, identifier: str, db: Database):
        TestReport.__init__(self, identifier=identifier)

        # MongoDb based reporting needs to create a
        # 'identifier' tagged collection for test results
        # Also save large files into GridFS
        self._db: Database = db
        self._gridfs: GridFS = GridFS(self._db)
        self._collection: Collection = self._db[identifier]

    def delete(self):
        self._db.drop_collection(self.get_identifier())

    def save_json_document(
            self,
            document_type: str,
            document: Dict,
            document_key: str,
            is_big: bool = False
    ):
        """
        Saves an indexed document either to a test report database or the filing system.

        :param document_type: Dict, Python object to persist as a JSON document.
        :param document: Dict, Python object to persist as a JSON document.
        :param document_key: str, indexing path for the document being saved.
        :param is_big: bool, if True, flags that the JSON file is expected to require special handling due to its size.
        """
        # Persist index test run result JSON document suitably indexed by
        # the document_key, into the (wrapped MongoDb) TestReportDatabase
        document['document_key'] = document_key
        if is_big:
            # Save this large document with GridFS
            gridfs_uid = self._gridfs.put(document)
            # we save large documents in GridFS dereferenced by a proxy document in the main database
            proxy_document = {
                'document_key': document_key,
                'gridfs_uid': gridfs_uid
            }
            self._collection.insert_one(proxy_document)
        else:
            self._collection.insert_one(document)

    def retrieve_document(self, document_type: str, document_key: str) -> Optional[Dict]:
        """
        Retrieves a single report type of document, corresponding to a specified document key.

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Dict, JSON document retrieved.
        """
        assert document_key
        assert self._collection
        document: Optional[Dict] = self._collection.find_one({'document_key': document_key}, fields={'_id': False})
        return document

    def stream_document(self, document_type: str, document_key: str) -> Generator:
        """
        Retrieves a single report type of document, corresponding to a specified document key

        :param document_type: str, name of report type simply used for informative error reporting.
        :param document_key: str, the key ('path') of the document being requested.
        :return: Generator, generator of streamed JSON document text
        """
        # For reasons of file size scalability, we assume that the document was large and stored in GridFS
        document_proxy: Optional[Dict] = self._collection.find_one({'document_key': document_key})
        if document_proxy:
            gridfs_uid = document_proxy["gridfs_uid"]
            try:
                with self._gridfs.get(gridfs_uid) as datafile:
                    yield from datafile
            except OSError as ose:
                logger.warning(f"{document_type} '{document_key}' is not (yet) accessible: {str(ose)}?")


class MongoReportDatabase(TestReportDatabase):
    """
    Wrapper class for a MongoDb instance-based repository for storing and retrieving SRI Testing test results.
    """
    def __init__(
            self,
            user: str = environ.get('MONGO_INITDB_ROOT_USERNAME', "root"),
            password: str = environ.get('MONGO_INITDB_ROOT_PASSWORD', "example"),
            host: str = "mongo" if RUNNING_INSIDE_DOCKER else "localhost",
            db_name: str = "sri_testing",
            **kwargs
    ):
        """
        TestReportDatabase constructor.

        :param user: str, MongoDb user (default: 'MONGO_INITDB_ROOT_USERNAME' or "root")
        :param password:  str, MongoDb password (default: 'MONGO_INITDB_ROOT_PASSWORD' or "example")
        :param host:  str, MongoDb host (default: "mongo" if inside the SRI Testing docker container else "localhost")
        :param db_name:  str, name of database (default: "sri_testing")
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
        self._db_name: Optional[str] = db_name
        self._sri_testing_db: Database = self._db_client[self._db_name]
        self._logs: Collection = self._sri_testing_db["test_logs"]
        time_created: str = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        self._logs.insert_one({"time_created": time_created})

    def list_databases(self) -> List[str]:
        return [name for name in self._db_client.list_database_names() if name not in ['admin', 'config', 'local']]

    def drop_database(self):
        if self._db_name:
            self._db_client.drop_database(self._db_name)
            self._db_name = None

    def get_test_report(self, identifier: str) -> TestReport:
        """
        :param identifier: str, test run identifier for the report
        :return: wrapped test report
        """
        report = MongoTestReport(identifier=identifier, db=self._sri_testing_db)
        return report

    def delete_test_report(self, report: TestReport):
        """
        :param report: TestReport to be deleted (should be an instance of MongoTestReport)
        """
        assert isinstance(report, MongoTestReport)
        report.delete()

    def get_available_reports(self) -> List[str]:
        """
        :return: list of identifiers of available reports.
        """
        non_system_collection_filter: Dict = {"name": {"$regex": r"^(?!system\.)"}}
        return self._sri_testing_db.list_collection_names(filter=non_system_collection_filter)
