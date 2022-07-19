from sys import stderr
from os.path import sep
from datetime import datetime

from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from tests.onehop import TEST_RESULTS_DIR
from translator.sri.testing.report_db import MongoReportDatabase

DEBUG: bool = True


def test_report_db_connection():
    try:
        MongoReportDatabase()
        print(
            "\nThe test_report_db_connection() connection has succeeded *as expected*... " +
            "The Test is a success!", file=stderr
        )
    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_fake_report_db_connection():
    try:
        MongoReportDatabase(
            user="nobody",
            password="nonsense",
            host="neverneverland"
        )
        assert False, "This nonsense test connection should always fail!"
    except ConnectionFailure:
        print(
            "\nThe test_fake_report_db_connection() fake connection has failed *as expected*... " +
            "The Test itself is a success!", file=stderr
        )
        assert True


def sample_mongodb_document_insertion(tdb: MongoReportDatabase):
    sample_item = {
        "component": "SRI",
        "activity": "testing"
    }

    test_bin: Collection = tdb.get_current_collection()

    result = test_bin.insert_one(sample_item)
    assert result
    assert result.inserted_id

    items = test_bin.find({'component': "SRI"})
    assert items
    assert any([item[u'_id'] == result.inserted_id and item[u'component'] == "SRI" for item in items])

    if not DEBUG:
        test_bin.delete_one(result.inserted_id)


def test_insert_test_entry():
    try:
        tdb = MongoReportDatabase()

        sample_mongodb_document_insertion(tdb)

    except ConnectionFailure:
        assert False, "This test document insertion should succeed if a suitable Mongodb instance is running?!"


def test_get_test_report_and_insertion():

    try:
        tdb = MongoReportDatabase()

        test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")

        report = tdb.get_test_report(identifier=test_id)

        assert report
        assert report.get_identifier() == test_id
        assert report.get_root_path() == f"{TEST_RESULTS_DIR}{sep}{test_id}"

        sample_mongodb_document_insertion(tdb)

        assert test_id in tdb.get_available_reports()

        tdb.delete_test_report(report)

        assert test_id not in tdb.get_available_reports()

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


