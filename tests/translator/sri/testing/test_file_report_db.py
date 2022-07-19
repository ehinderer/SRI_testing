from sys import stderr
from os.path import sep
from datetime import datetime
from typing import Dict

import pytest

from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from tests.onehop import TEST_RESULTS_DIR
from translator.sri.testing.report_db import FileReportDatabase

DEBUG: bool = True


def sample_mongodb_document_insertion(tdb: FileReportDatabase):
    sample_item = {
        "component": "SRI",
        "activity": "testing"
    }
    raise NotImplementedError("Implement me!")
    # test_bin: Collection = tdb.get_current_collection()
    #
    # result = test_bin.insert_one(sample_item)
    # assert result
    # assert result.inserted_id
    #
    # items = test_bin.find({'component': "SRI"})
    # assert items
    # assert any([item[u'_id'] == result.inserted_id and item[u'component'] == "SRI" for item in items])
    #
    # if not DEBUG:
    #     test_bin.delete_one(result.inserted_id)


def test_insert_test_entry():
    tdb = FileReportDatabase()
    sample_mongodb_document_insertion(tdb)


def test_get_test_report_and_insertion():

    tdb = FileReportDatabase()

    test_id = datetime.now().strftime("%Y-%b-%d_%Hhr%M")

    report = tdb.get_test_report(identifier=test_id)

    assert report
    assert report.get_identifier() == test_id
    assert report.get_root_path() == f"{TEST_RESULTS_DIR}{sep}{test_id}"

    sample_mongodb_document_insertion(tdb)

    assert test_id in tdb.get_available_reports()
