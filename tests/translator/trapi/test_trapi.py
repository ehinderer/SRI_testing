"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
from typing import Optional

import pytest

from translator.sri.testing import set_global_environment
from translator.trapi import get_trapi_version, check_provenance


def test_set_default_global_environment():
    set_global_environment()
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.2")


def test_set_specific_trapi_versioned_global_environment():
    set_global_environment()
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.2")


# check_provenance(ara_case, ara_response), triggers AssertError exceptions
@pytest.mark.parametrize(
    "query",
    [
        ("ara_case", "ara_response", True),   # set 3rd argument to 'True' if the check_provenance should pass
        ("ara_case", "ara_response", False),  # set 3rd argument to 'False' if the check_provenance should fail
    ]
)
def test_check_provenance(query):
    try:
        check_provenance(query[0], query[1])

    except AssertionError:

        assert not query[2], "check_provenance() should pass!"

    assert query[2], "check_provenance() should fail!"
