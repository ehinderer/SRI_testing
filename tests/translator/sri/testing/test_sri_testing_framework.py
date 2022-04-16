"""
Unit tests for the generic (shared) components of the SRI Testing Framework
"""
from typing import Optional
import logging
import pytest


from bmt import Toolkit

from translator.sri.testing import check_biolink_model_compliance, set_global_environment, get_toolkit

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_set_default_global_environment():
    set_global_environment()
    tk: Optional[Toolkit] = get_toolkit()
    assert tk
    model_version = tk.get_model_version()
    logger.debug(f"test_set_default_global_environment(): Biolink Model version is: '{str(model_version)}'")
    assert model_version == Toolkit().get_model_version()


def test_set_specific_biolink_versioned_global_environment():
    set_global_environment(biolink_version="2.2.16")
    tk: Optional[Toolkit] = get_toolkit()
    assert tk
    assert tk.get_model_version() == "2.2.16"


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:subclass_of',
                'subject': 'UBERON:0005453',
                'object': 'UBERON:0035769'
            },
            "",
            []
        )
    ]
)
def test_check_biolink_model_compliance(query):
    # check_biolink_model_compliance(edge: Dict[str, str]) -> Tuple[str, Optional[List[str]]]
    model_version, errors = check_biolink_model_compliance(query[0])  # query[0] == edge: Dict[str, str]
    assert model_version == query[1]
    assert errors == query[2]
