import json

from os.path import sep
from datetime import datetime
from typing import Dict, Optional, List

from tests.onehop import get_test_results_dir
from translator.sri.testing.report_db import FileReportDatabase, TestReport

# For early testing of the Unit test, test data is not deleted when DEBUG is True;
# however, this interferes with idempotency of the tests (i.e. data must be manually deleted from the test database)
DEBUG: bool = True

TEST_DATABASE = "test-database"


def test_create_file_report_database():

    frd = FileReportDatabase(db_name=TEST_DATABASE)

    assert TEST_DATABASE in frd.list_databases()

    assert any(['time_created' in doc for doc in frd.get_report_logs()])

    assert FileReportDatabase.LOG_NAME not in frd.get_available_reports()

    if not DEBUG:
        frd.drop_database()


def test_delete_file_report_db_database():
    # same as the previous test but ignoring DEBUG TO enforce the database deletion
    frd = FileReportDatabase(db_name=TEST_DATABASE)

    assert "test-database" in frd.list_databases()

    frd.drop_database()

    assert "test-database" not in frd.list_databases()


SAMPLE_DOCUMENT_KEY: str = "sample-document"
SAMPLE_DOCUMENT: Dict = {}


def sample_file_document_creation_and_insertion(
        frd: FileReportDatabase,
        identifier: str,
        is_big: bool = False
) -> TestReport:

    test_report: TestReport = frd.get_test_report(identifier=identifier)
    assert test_report.get_identifier() == identifier
    assert test_report.get_root_path() == f"{get_test_results_dir(frd.get_db_name())}{sep}{identifier}"

    # A test report is not yet available until something is saved
    assert identifier not in frd.get_available_reports()

    test_report.save_json_document(
        document_type="test document",
        document={},
        document_key=SAMPLE_DOCUMENT_KEY,
        is_big=is_big
    )
    assert identifier in frd.get_available_reports()

    return test_report


def _test_id(seq: int) -> str:
    return f"{datetime.now().strftime('%Y-%b-%d_%Hhr%M')}.{str(seq)}"


def test_create_test_report_then_save_and_retrieve_document():

    frd = FileReportDatabase(db_name=TEST_DATABASE)

    test_id = _test_id(1)

    test_report: TestReport = sample_file_document_creation_and_insertion(frd, test_id)

    document: Optional[Dict] = test_report.retrieve_document(
        document_type="test document", document_key=SAMPLE_DOCUMENT_KEY
    )
    assert document
    assert document["document_key"] == SAMPLE_DOCUMENT_KEY

    if not DEBUG:
        test_report.delete()
        assert test_id not in frd.get_available_reports()

        frd.drop_database()


def test_db_level_test_report_deletion():

    frd = FileReportDatabase(db_name=TEST_DATABASE)

    test_id = _test_id(2)

    test_report: TestReport = sample_file_document_creation_and_insertion(frd, test_id)

    frd.delete_test_report(test_report)
    assert test_id not in frd.get_available_reports()

    if not DEBUG:
        frd.drop_database()


def test_create_test_report_then_save_and_retrieve_a_big_document():

    frd = FileReportDatabase(db_name=TEST_DATABASE)

    test_id = _test_id(3)

    test_report: TestReport = sample_file_document_creation_and_insertion(frd, test_id, is_big=True)

    text_file: str = ""
    for line in test_report.stream_document(document_type="test document", document_key=SAMPLE_DOCUMENT_KEY):
        text_file += line

    assert text_file

    # Should be a JSON document
    document = json.loads(text_file)

    assert document["document_key"] == SAMPLE_DOCUMENT_KEY

    if not DEBUG:
        test_report.delete()
        assert test_id not in frd.get_available_reports()

        frd.drop_database()


def test_file_report_logging():

    trd = FileReportDatabase(db_name=TEST_DATABASE)

    test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
    test_report = trd.get_test_report(identifier=test_id)

    test_report.open_report_log()
    test_report.write_report_log("Hello World!")
    test_report.close_report_log()

    # report_logs: List[Dict] = trd.get_report_logs()
    # assert report_logs
    # assert any(['time_created' in doc for doc in report_logs])
