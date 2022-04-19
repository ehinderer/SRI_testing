"""
Unit tests for the generic (shared) components of the SRI Testing Framework
"""
from typing import Optional, Tuple
import logging
import pytest


from bmt import Toolkit

from translator.biolink import check_biolink_model_compliance_of_input_edge, get_toolkit, \
    check_biolink_model_compliance_of_knowledge_graph
from translator.sri.testing import set_global_environment

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_set_default_biolink_versioned_global_environment():
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
def test_check_biolink_model_compliance_of_input_edge(query: Tuple):
    set_global_environment(biolink_version=query[0])
    # check_biolink_model_compliance_of_input_edge(edge: Dict[str, str]) -> Tuple[str, Optional[List[str]]]
    model_version, errors = check_biolink_model_compliance_of_input_edge(edge=query[1])
    assert model_version == get_toolkit().get_model_version()
    assert errors[0] == query[2] if errors else True


@pytest.mark.parametrize(
    "query",
    [
        (
            "2.2.13",  # Biolink Model Version

            # Sample TRAPI Knowledge Graph
            {
                # Sample nodes
                'nodes': {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    },
                    "PUBCHEM.COMPOUND:597": {
                        "name": "cytosine",
                        "categories":[
                            "biolink:SmallMolecule"
                        ],
                        "attributes": [
                            {
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:highest_FDA_approval_status",
                            "attributes":[],
                            "original_attribute_name": "max_phase",
                            "value": "FDA Clinical Research Phase 2",
                            "value_type_id": "biolink:FDA_approval_status_enum"
                            }
                        ]
                    }
                },
                # Sample edge
                'edges': {
                   "edge_1": {
                       "subject": "NCBIGene:29974",
                       "predicate": "biolink:interacts_with",
                       "object": "PUBCHEM.COMPOUND:597",
                       "attributes": [
                           {
                               "attribute_source": "infores:hmdb",
                               "attribute_type_id": "biolink:primary_knowledge_source",
                               "attributes": [],
                               "description": "MolePro's HMDB target transformer",
                               "original_attribute_name": "biolink:primary_knowledge_source",
                               "value": "infores:hmdb",
                               "value_type_id": "biolink:InformationResource"
                           },
                           {
                               "attribute_source": "infores:hmdb",
                               "attribute_type_id": "biolink:aggregator_knowledge_source",
                               "attributes": [],
                               "description": "Molecular Data Provider",
                               "original_attribute_name": "biolink:aggregator_knowledge_source",
                               "value": "infores:molepro",
                               "value_type_id": "biolink:InformationResource"
                           }
                        ]
                    }
                }
            },
            ""
        ),
        ()
    ]
)
def test_check_biolink_model_compliance_of_knowledge_graph(query: Tuple):
    set_global_environment(biolink_version=query[0])
    # check_biolink_model_compliance_of_knowledge_graph(graph: Dict) -> Tuple[str, Optional[List[str]]]:
    model_version, errors = check_biolink_model_compliance_of_knowledge_graph(graph=query[1])
    assert model_version == get_toolkit().get_model_version()
    assert errors[0] == query[2] if errors else True
