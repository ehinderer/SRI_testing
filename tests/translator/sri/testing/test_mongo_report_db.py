import json
from typing import Dict, Optional
from sys import stderr
from os.path import sep
from datetime import datetime

from pymongo.errors import ConnectionFailure

from tests.onehop import get_test_results_dir
from translator.sri.testing.report_db import MongoReportDatabase, TestReport

# For early testing of the Unit test, test data is not deleted when DEBUG is True;
# however, this interferes with idempotency of the tests (i.e. data must be manually deleted from the test database)
DEBUG: bool = False

TEST_DATABASE = "test-database"


def test_mongo_report_db_connection():
    try:
        mrd = MongoReportDatabase(db_name=TEST_DATABASE)

        assert TEST_DATABASE in mrd.list_databases()

        assert any(['time_created' in doc for doc in mrd.get_logs()])

        assert MongoReportDatabase.LOG_NAME not in mrd.get_available_reports()

        if not DEBUG:
            mrd.drop_database()

        print(
            "\nThe test_mongo_report_db_connection() connection has succeeded *as expected*... " +
            "The Test is a success!", file=stderr
        )
    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_delete_mongo_report_db_database():
    # same as the previous test but ignoring DEBUG TO enforce the database deletion
    try:
        mrd = MongoReportDatabase(db_name=TEST_DATABASE)

        assert TEST_DATABASE in mrd.list_databases()

        mrd.drop_database()

        assert TEST_DATABASE not in mrd.list_databases()

        print(
            "\nThe test_mongo_report_db_connection() connection has succeeded *as expected*... " +
            "The Test is a success!", file=stderr
        )
    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_fake_mongo_report_db_connection():
    try:
        MongoReportDatabase(
            user="nobody",
            password="nonsense",
            host="neverneverland"
        )
        assert False, "This nonsense test connection should always fail!"
    except ConnectionFailure:
        print(
            "\nThe test_fake_mongo_report_db_connection() fake connection has failed *as expected*... " +
            "The Test itself is a success!", file=stderr
        )
        assert True


SAMPLE_DOCUMENT_KEY: str = "sample-document"
SAMPLE_DOCUMENT: Dict = {}


def sample_mongodb_document_creation_and_insertion(
        mrd: MongoReportDatabase,
        identifier: str,
        is_big: bool = False
) -> TestReport:

    test_report: TestReport = mrd.get_test_report(identifier=identifier)
    assert test_report.get_identifier() == identifier

    test_results_dir = get_test_results_dir(mrd.get_db_name())
    assert test_report.get_root_path() == f"{test_results_dir}{sep}{identifier}"

    # A test report is not yet available until something is saved
    assert identifier not in mrd.get_available_reports()

    test_report.save_json_document(
        document_type="test document",
        document={},
        document_key=SAMPLE_DOCUMENT_KEY,
        is_big=is_big
    )
    assert identifier in mrd.get_available_reports()

    return test_report


def test_create_test_report_then_save_and_retrieve_document():
    try:
        mrd = MongoReportDatabase(db_name=TEST_DATABASE)

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        test_report: TestReport = sample_mongodb_document_creation_and_insertion(mrd, test_id)

        document: Optional[Dict] = test_report.retrieve_document(
            document_type="test document", document_key=SAMPLE_DOCUMENT_KEY
        )
        assert document
        assert document["document_key"] == SAMPLE_DOCUMENT_KEY

        if not DEBUG:
            test_report.delete()
            assert test_id not in mrd.get_available_reports()

            mrd.drop_database()

    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_db_level_test_report_deletion():

    try:
        mrd = MongoReportDatabase(db_name=TEST_DATABASE)

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        test_report: TestReport = sample_mongodb_document_creation_and_insertion(mrd, test_id)

        mrd.delete_test_report(test_report)
        assert test_id not in mrd.get_available_reports()

        if not DEBUG:
            mrd.drop_database()

    except ConnectionFailure:
        assert False, "This test document insertion should succeed if a suitable Mongodb instance is running?!"


def test_create_test_report_then_save_and_retrieve_a_big_document():
    try:
        mrd = MongoReportDatabase(db_name=TEST_DATABASE)

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        test_report: TestReport = sample_mongodb_document_creation_and_insertion(mrd, test_id, is_big=True)

        text_file: str = ""
        for line in test_report.stream_document(document_type="test document", document_key=SAMPLE_DOCUMENT_KEY):
            text_file += line

        assert text_file

        # Should be a JSON document
        document = json.loads(text_file)

        assert document["document_key"] == SAMPLE_DOCUMENT_KEY

        if not DEBUG:
            test_report.delete()
            assert test_id not in mrd.get_available_reports()

            mrd.drop_database()

    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"
