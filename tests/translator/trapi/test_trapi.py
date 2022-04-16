"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
from typing import Optional

import pytest

from translator.sri.testing import set_global_environment
from translator.trapi import get_trapi_version


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


# check_provenance(ara_case, ara_response), triggers assert exceptions
@pytest.mark.parametrize(
    "query",
    [
        # (URIRef("http://purl.obolibrary.org/obo/GO_0007267"), "biological_process"),
        # (URIRef("http://purl.obolibrary.org/obo/GO_0019899"), "molecular_function"),
        # (URIRef("http://purl.obolibrary.org/obo/GO_0005739"), "cellular_component"),
    ]
)
def test_check_provenance(query):
    try:
        pass
    except AssertionError:
        pass
