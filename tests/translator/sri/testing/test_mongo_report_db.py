from sys import stderr
from os.path import sep
from datetime import datetime

from pymongo.errors import ConnectionFailure

from tests.onehop import TEST_RESULTS_DIR
from translator.sri.testing.report_db import MongoReportDatabase, TestReport

# For early testing of the Unit test, test data is not deleted when DEBUG is True;
# however, this interferes with idempotency of the tests (i.e. data must be manually deleted from the test database)
DEBUG: bool = True


def test_mongo_report_db_connection():
    try:
        mrd = MongoReportDatabase(db_name="test-database")

        assert "test-database" in mrd.list_databases()

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
        mrd = MongoReportDatabase(db_name="test-database")

        assert "test-database" in mrd.list_databases()

        mrd.drop_database()

        assert "test-database" not in mrd.list_databases()

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


def sample_mongodb_document_creation_and_insertion(mrd: MongoReportDatabase, identifier: str) -> TestReport:

    test_report: TestReport = mrd.get_test_report(identifier=identifier)
    assert test_report.get_identifier() == identifier
    assert test_report.get_root_path() == f"{TEST_RESULTS_DIR}{sep}{identifier}"

    # A test report is not yet available until something is saved
    assert identifier not in mrd.get_available_reports()

    test_report.save_json_document(document_type="test", document={}, document_key="sample-document", is_big=False)
    assert identifier in mrd.get_available_reports()

    return test_report


def test_create_test_report_and_save_json_document():
    try:
        mrd = MongoReportDatabase(db_name="test-database")

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        test_report: TestReport = sample_mongodb_document_creation_and_insertion(mrd, test_id)

        if not DEBUG:
            test_report.delete()
            assert test_id not in mrd.get_available_reports()

            mrd.drop_database()

    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_db_level_test_report_deletion(db_name="test-database"):

    try:
        mrd = MongoReportDatabase()

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")
        test_report: TestReport = sample_mongodb_document_creation_and_insertion(mrd, test_id)

        mrd.delete_test_report(test_report)
        assert test_id not in mrd.get_available_reports()

        if not DEBUG:
            mrd.drop_database()

    except ConnectionFailure:
        assert False, "This test document insertion should succeed if a suitable Mongodb instance is running?!"


def test_save_json_document():
    try:
        tdb = MongoReportDatabase()

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")

        report = tdb.get_test_report(identifier=test_id)

        assert report
        assert report.get_identifier() == test_id
        assert report.get_root_path() == f"{TEST_RESULTS_DIR}{sep}{test_id}"

        # tdb.save_json_document(
        #     report=self._test_report,
        #     document_type=document_type,
        #     document=document,
        #     document_key=document_key,
        #     is_big=is_big
        # )

    except ConnectionFailure:
        assert False, "This test document insertion should succeed if a suitable Mongodb instance is running?!"
