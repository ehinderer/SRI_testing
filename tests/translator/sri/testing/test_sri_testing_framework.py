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
            "2.2.13",  # Biolink Model Version
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:subclass_of',
                'subject': 'UBERON:0005453',
                'object': 'UBERON:0035769'
            },
            ""
        ),
        (
            "2.2.13",
            {
                'subject_category': 'biolink:NotACategory',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:subclass_of',
                'subject': 'UBERON:0005453',
                'object': 'UBERON:0035769'
            },
            "Unknown subject category: 'biolink:NotACategory'"
        ),
        (
            "2.2.13",
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:NotACategory',
                'predicate': 'biolink:subclass_of',
                'subject': 'UBERON:0005453',
                'object': 'UBERON:0035769'
            },
            "Unknown object category: 'biolink:NotACategory'"
        ),
        (
            "2.2.13",
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:not_a_predicate',
                'subject': 'UBERON:0005453',
                'object': 'UBERON:0035769'
            },
            "Unknown predicate: 'biolink:not_a_predicate'"
        ),
        (
            "2.2.13",
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:subclass_of',
                'subject': 'FOO:0005453',
                'object': 'UBERON:0035769'
            },
            "Subject 'FOO:0005453' prefix unmapped to 'biolink:AnatomicalEntity'"
        ),
        (
            "2.2.13",
            {
                'subject_category': 'biolink:AnatomicalEntity',
                'object_category': 'biolink:AnatomicalEntity',
                'predicate': 'biolink:subclass_of',
                'subject': 'UBERON:0005453',
                'object': 'BAR:0035769'
            },
            "Object 'BAR:0035769' prefix unmapped to 'biolink:AnatomicalEntity'"
        ),
        (
            "1.8.2",
            {
                'subject_category': 'biolink:ChemicalSubstance',
                'object_category': 'biolink:Protein',
                'predicate': 'biolink:entity_negatively_regulates_entity',
                'subject': 'DRUGBANK:DB00945',
                'object': 'UniProtKB:P23219'
            },
            ""
        )

    ]
)
def test_check_biolink_model_compliance(query):
    set_global_environment(biolink_version=query[0])
    # check_biolink_model_compliance(edge: Dict[str, str]) -> Tuple[str, Optional[List[str]]]
    model_version, errors = check_biolink_model_compliance(query[1])  # query[1] == edge: Dict[str, str]
    assert model_version == get_toolkit().get_model_version()
    assert errors[0] == query[2] if errors else True
