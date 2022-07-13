import pytest

from translator.sri.testing.report_db import TestReportDatabase
from pymongo.errors import ConnectionFailure

DEBUG: bool = True


def test_report_db_connection():
    try:
        TestReportDatabase()
    except ConnectionFailure:
        assert False, "This test connection should succeed if a suitable Mongodb instance is running?!"


def test_false_report_db_connection():
    try:
        TestReportDatabase(
            user="nobody",
            password="nonsense",
            host="neverneverland"
        )
        assert False, "This nonsense test connection should always fail!"
    except ConnectionFailure:
        assert True


def test_insert_test_entry():
    try:
        tdb = TestReportDatabase()

        test_item = {
            "component": "SRI",
            "activity": "testing"
        }

        result = tdb.get_collection().insert_one(test_item)

        assert result
        assert result.inserted_id

        if not DEBUG:
            tdb.get_collection().delete_one(result.inserted_id)

    except ConnectionFailure:
        assert False, "This test document insertion should succeed if a suitable Mongodb instance is running?!"
