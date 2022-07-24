import shutil
from os import environ, makedirs, listdir
from os.path import sep, normpath, exists
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

from tests.onehop import TEST_RESULTS_DB, get_test_results_dir, ONEHOP_TEST_DIRECTORY

import logging
logger = logging.getLogger()
logger.setLevel("DEBUG")

RUNNING_INSIDE_DOCKER = environ.get('RUNNING_INSIDE_DOCKER', False)


class TestReportDatabase:

    LOG_NAME = "logs"

    """
    Abstract superclass of a Test Report Database
    """
    def __init__(self, db_name: Optional[str] = TEST_RESULTS_DB, **kwargs):
        self._db_name: str = db_name if db_name else TEST_RESULTS_DB
        self._test_results_path: str = get_test_results_dir(self.get_db_name())

    def get_db_name(self) -> str:
        return self._db_name

    def get_test_results_path(self) -> str:
        return self._test_results_path

    def list_databases(self) -> List[str]:
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def drop_database(self):
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def get_available_reports(self) -> List[str]:
        """
        :return: list of identifiers of available ('completed') reports.
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def get_logs(self) -> List[Dict]:
        """
        :return: Dict, report database log (as a Python dictionary)
        """
        raise NotImplementedError("Abstract method - implement in child subclass!")

    def get_test_report(self, identifier):
        raise NotImplementedError("Abstract method - implement in child subclass!")


class TestReport:
    """
    Abstract superclass of a Test Report, which is a related
    collection of test run documents stored in a TestReportDatabase.
    """
    def __init__(self, identifier: str, database: TestReportDatabase):
        """
        TestReport constructor.

        :param identifier: report identifier (perhaps a timestamp?)
        :param database: TestReportDatabase to which the report belongs
        """
        assert identifier  # the test report 'identifier' should not be None or empty string
        self._report_identifier = identifier
        self._database = database
        self._report_root_path: Optional[str] = \
            f"{get_test_results_dir(self._database.get_db_name())}{sep}{identifier}"

    def get_identifier(self) -> str:
        return self._report_identifier

    def get_database(self) -> TestReportDatabase:
        return self._database

    def get_root_path(self) -> Optional[str]:
        return self._report_root_path

    def delete(self):
        """
        Delete internal representation of the report.
        """
        # Signal deletion with
        self._report_root_path = None

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


###############################################################
# Deferred TestReportDatabase method creation to work around  #
# TestReportDatabase and TestReport forward definitions issue #
###############################################################
def _get_test_report(obj, identifier: str) -> TestReport:
    """
    :return: TestReport of the appropriate kind for the given type of TestReportDatabase
    """
    raise NotImplementedError("Abstract method - implement in child subclass!")


TestReportDatabase.get_test_report = _get_test_report


def _delete_test_report(obj, report: TestReport):
    """
    :param report: TestReport, to be deleted
    """
    raise NotImplementedError("Abstract method - implement in child subclass!")


TestReportDatabase.delete_test_report = _delete_test_report


class FileTestReport(TestReport):

    def __init__(self, identifier: str, database: TestReportDatabase):
        TestReport.__init__(self, identifier=identifier, database=database)

        # File system based reporting needs to create a
        # 'identifier' tagged directory for test results
        makedirs(self.get_database().get_test_results_path(), exist_ok=True)

    def delete(self):
        try:
            shutil.rmtree(self.get_root_path())
            TestReport.delete(self)
        except OSError as ose:
            logger.warning(
                f"FileTestReport.delete():  could not delete '{str(self.get_root_path())}' report path: {str(ose)}"
            )

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
            # TODO: maybe I need to write 'is_big' files out as binary?
            with open(f"{document_path}.json", mode='w', encoding='utf8', buffering=1, newline='\n') as document_file:
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
            with open(f"{document_path}.json", mode='r', encoding='utf8', buffering=1, newline='\n') as report_file:
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
                data: bytes
                for data in datafile.readlines():
                    line: str = data.decode(encoding="utf8")
                    yield line.strip()
        except OSError as ose:
            logger.warning(f"{document_type} '{document_key}' is not (yet) accessible: {str(ose)}?")


class FileReportDatabase(TestReportDatabase):
    """
    Wrapper class for an OS filing system-based repository for storing and retrieving SRI Testing test results.
    """

    def __init__(self, db_name: Optional[str] = None, **kwargs):
        TestReportDatabase.__init__(self, db_name=db_name, **kwargs)

        # File system based reporting needs to create
        # a db_name'd root directory for test results
        makedirs(self.get_test_results_path(), exist_ok=True)

        self._logs: str = normpath(f"{self.get_test_results_path()}{sep}{self.LOG_NAME}")
        makedirs(self._logs, exist_ok=True)

        creation_log_file: str = f"{self._logs}{sep}creation.json"
        if not exists(creation_log_file):
            time_created: str = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
            document = {"time_created": time_created}
            try:
                with open(creation_log_file, mode='w', encoding='utf8', buffering=1, newline='\n') as log_file:
                    json.dump(document, log_file, indent=4)
            except OSError as ose:
                logger.warning(f"'{creation_log_file}' cannot be written out: {str(ose)}?")

    def list_databases(self) -> List[str]:
        # At present, the FileReportDatabase hosts all of its
        # 'databases' a.k.a. 'db_name' folders, under the ONEHOP_TEST_DIRECTORY
        return [identifier for identifier in listdir(ONEHOP_TEST_DIRECTORY)]

    def drop_database(self):
        shutil.rmtree(self.get_test_results_path())

    def get_test_report(self, identifier: str) -> TestReport:
        """
        :param identifier: str, test run identifier for the report
        :return: wrapped test report
        """
        report = FileTestReport(identifier=identifier, database=self)
        return report

    @staticmethod
    def delete_test_report(report: TestReport):
        """
        :param report: TestReport to be deleted
        """
        report.delete()

    def get_available_reports(self) -> List[str]:
        """
        :return: list of identifiers of available reports.
        """
        test_results_directory = self.get_test_results_path()
        test_run_list: List[str] = [
            identifier for identifier in listdir(test_results_directory)
            if identifier != TestReportDatabase.LOG_NAME
        ]
        return test_run_list

    def get_logs(self) -> List[Dict]:
        """
        :return: Dict, report database log (as a Python dictionary)
        """
        logs: List[Dict] = list()
        for identifier in listdir(self._logs):
            try:
                log_file_name = f"{self._logs}{sep}{identifier}"
                with open(log_file_name, mode='r', encoding='utf8', buffering=1, newline='\n') as log_file:
                    contents = log_file.read()
                if contents:
                    document: Dict = orjson.loads(contents)
                    logs.append(document)
            except OSError as ose:
                logger.warning(f"Log file '{identifier}' cannot be read in: {str(ose)}?")
        return logs


class MongoTestReport(TestReport):

    def __init__(self, identifier: str, database: TestReportDatabase, mongo_db: Database):

        TestReport.__init__(self, identifier=identifier, database=database)

        # remember the MongoDb database handle associated with this MongoTestReport
        self._db: Database = mongo_db

        # Also save large files into GridFS
        self._gridfs: GridFS = GridFS(self._db)

        # MongoDb based reporting needs to create a
        # 'identifier' tagged collection for test results
        self._collection: Optional[Collection] = self._db[identifier]

    def delete(self):
        self._collection = None
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
            gridfs_uid = self._gridfs.put(json.dumps(document), encoding="utf8")
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
        assert self._collection is not None
        document: Optional[Dict] = self._collection.find_one(
            filter={'document_key': document_key}, projection={'_id': False}
        )
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
                    yield datafile.readline().decode(encoding="utf8")
            except OSError as ose:
                logger.warning(f"{document_type} '{document_key}' is not (yet) accessible: {str(ose)}?")


class MongoReportDatabase(TestReportDatabase):

    """
    Wrapper class for a MongoDb instance-based repository for storing and retrieving SRI Testing test results.
    """
    def __init__(
            self,
            db_name: Optional[str] = None,
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
        :param db_name:  str, name of database (default: "sri_testing")
        :param kwargs:

        :raises pymongo.errors.ConnectionFailure
        """
        TestReportDatabase.__init__(self, db_name=db_name, **kwargs)

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

        # 'ping' will throw a pymongo.errors.ConnectionFailure if the connection fails
        self._db_client.admin.command('ping')

        self._mongo_db: Database = self._db_client[self._db_name]

        if self.LOG_NAME not in self._mongo_db.list_collection_names():
            time_created: str = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
            self._logs: Collection = self._mongo_db[self.LOG_NAME]
            # this should create the log once
            self._logs.insert_one({"time_created": time_created})
        else:
            self._logs: Collection = self._mongo_db[self.LOG_NAME]

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
        report = MongoTestReport(identifier=identifier, database=self, mongo_db=self._mongo_db)
        return report

    @staticmethod
    def delete_test_report(report: TestReport):
        """
        :param report: TestReport to be deleted (should be an instance of MongoTestReport)
        """
        assert isinstance(report, MongoTestReport)
        report.delete()

    def get_available_reports(self) -> List[str]:
        """
        :return: list of identifiers of available reports.
        """
        non_system_collection_filter: Dict = {"name": {"$regex": rf"^(?!system\.|{self.LOG_NAME}|fs\..*)"}}
        return self._mongo_db.list_collection_names(filter=non_system_collection_filter)

    def get_logs(self) -> List[Dict]:
        """
        :return: Dict, report database log (as a Python dictionary)
        """
        logs: List[Dict] = [doc for doc in self._logs.find()]
        return logs
