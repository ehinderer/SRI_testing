"""
Unit tests for the backend logic of the web services application
"""
from sys import stderr
import logging
from translator.sri.testing.processor import run_test_harness
from app.util import run_onehop_test_harness

logger = logging.getLogger()


def test_run_test_harness():
    process_id = run_test_harness(command="echo 'Hello Translator!'")
    assert process_id
    print(f"test_run_test_harness() worker process_id: {process_id}", flush=True, file=stderr)


def test_run_onehop_test_harness():
    process_id = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
    )
    assert process_id
    print(f"test_run_onehop_test_harness() worker process_id: {process_id}", flush=True, file=stderr)
