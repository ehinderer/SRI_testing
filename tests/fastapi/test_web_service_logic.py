"""
Unit tests for the backend logic of the web services application
"""
from app.util import run_test_harness


def test_run_test_harness():
    session_id = run_test_harness(
        trapi_version=None,
        biolink_version=None,
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    assert session_id
