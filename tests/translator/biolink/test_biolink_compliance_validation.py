"""
Unit tests for the generic (shared) components of the SRI Testing Framework
"""
import sys
from typing import Optional, Tuple
from pprint import PrettyPrinter
import logging
import pytest

from bmt import Toolkit

from translator.biolink import check_biolink_model_compliance_of_input_edge, get_toolkit, \
    check_biolink_model_compliance_of_knowledge_graph
from translator.sri.testing import set_global_environment

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

pp = PrettyPrinter(indent=4)


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


# TODO: we may wish to externalize the sample knowledge graphs
#       for testing here instead of embedding them in this file?
@pytest.mark.parametrize(
    "query",
    [
        (
            "2.2.13",  # Biolink Model Version

            # Query 0: Sample full TRAPI Knowledge Graph
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
                        "categories": [
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
        (
            "2.2.13",
            # Query 1: Empty graph - caught by missing 'nodes' key
            {},
            "No nodes found in the knowledge graph?"
        ),
        (
            "2.2.13",
            # Query 2: Empty nodes dictionary
            {
                "nodes": dict()
            },
            "No nodes found in the knowledge graph?"
        ),
        (
            "2.2.13",
            # Query 3: Empty edges - caught by missing 'edges' dictionary
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    }
                }
            },
            "No edges found in the knowledge graph?"
        ),
        (
            "2.2.13",
            # Query 4 Empty edges dictionary
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    }
                },
                "edges": dict()
            },
            "No edges found in the knowledge graph?"
        ),
        (
            "2.2.13",
            # Query 5: 'categories' tag value is ill-formed: should be a list
            {
                "nodes": {
                    "NCBIGene:29974": dict()
                },
                "edges": {
                   "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:interacts_with",
                        "object": "NCBIGene:29974",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "Node 'NCBIGene:29974' is missing its 'categories'?"
        ),
        (
            "2.2.13",
            # Query 6: 'categories' tag value is ill-formed: should be a list
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": "biolink:Gene"
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:interacts_with",
                        "object": "NCBIGene:29974",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "The value of node 'NCBIGene:29974' categories should be a List?"
        ),
        (
            "2.2.13",
            # Query 7: invalid category specified
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Nonsense_Category"
                       ]
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:interacts_with",
                        "object": "NCBIGene:29974",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "'biolink:Nonsense_Category' for node 'NCBIGene:29974' is not a recognized Biolink Model category?"
        ),
        (
            "2.2.13",
            # Query 8: invalid node CURIE prefix namespace, for specified category
            {
                "nodes": {
                    "FOO:1234": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "FOO:1234",
                        "predicate": "biolink:interacts_with",
                        "object": "FOO:1234",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "Node 'FOO:1234' prefix unmapped to category 'biolink:Gene'?"
        ),
        (
            "2.2.13",
            # Query 9: missing or empty subject, predicate, object values
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    }
                },
                "edges": {
                    "edge_1": {
                        # "subject": "",
                        "predicate": "biolink:interacts_with",
                        "object": "NCBIGene:29974",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            # ditto for predicate and object... but identical code pattern thus we only test the subject id here
            "Edge 'None--biolink:interacts_with->NCBIGene:29974' has a missing or empty subject slot?"
        ),
        (
            "2.2.13",
            # Query 10: subject id is missing from the nodes catalog
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    },
                    "PUBCHEM.COMPOUND:597": {
                        "name": "cytosine",
                        "categories": [
                            "biolink:SmallMolecule"
                        ],
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:12345",
                        "predicate": "biolink:interacts_with",
                        "object": "PUBCHEM.COMPOUND:597",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "Edge subject id 'NCBIGene:12345' is missing from the nodes catalog?"
        ),
        (
            "2.2.13",
            # Query 11: predicate is unknown
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    },
                    "PUBCHEM.COMPOUND:597": {
                        "name": "cytosine",
                        "categories": [
                            "biolink:SmallMolecule"
                        ],
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:unknown_predicate",
                        "object": "PUBCHEM.COMPOUND:597",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "'biolink:unknown_predicate' is an unknown Biolink Model predicate"
        ),
        (
            "2.2.13",
            # Query 12: object id is missing from the nodes catalog
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    },
                    "PUBCHEM.COMPOUND:597": {
                        "name": "cytosine",
                        "categories": [
                            "biolink:SmallMolecule"
                        ],
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:interacts_with",
                        "object": "PUBCHEM.COMPOUND:678",
                        "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "Edge object id 'PUBCHEM.COMPOUND:678' is missing from the nodes catalog?"
        ),
        (
            "2.2.13",
            # Query 13: object id is missing from the nodes catalog
            {
                "nodes": {
                    "NCBIGene:29974": {
                       "categories": [
                           "biolink:Gene"
                       ]
                    },
                    "PUBCHEM.COMPOUND:597": {
                        "name": "cytosine",
                        "categories": [
                            "biolink:SmallMolecule"
                        ],
                    }
                },
                "edges": {
                    "edge_1": {
                        "subject": "NCBIGene:29974",
                        "predicate": "biolink:interacts_with",
                        "object": "PUBCHEM.COMPOUND:597",
                        # "attributes": [{"attribute_type_id": "fake-attribute-id"}]
                    }
                }
            },
            "Edge 'NCBIGene:29974--biolink:interacts_with->PUBCHEM.COMPOUND:597' has a missing or empty attributes?"
        )
    ]
)
def test_check_biolink_model_compliance_of_knowledge_graph(query: Tuple):
    set_global_environment(biolink_version=query[0])
    # check_biolink_model_compliance_of_knowledge_graph(graph: Dict) -> Tuple[str, Optional[List[str]]]:
    model_version, errors = check_biolink_model_compliance_of_knowledge_graph(graph=query[1])
    assert model_version == get_toolkit().get_model_version()
    print(f"Errors:\n{pp.pformat(errors)}\n", file=sys.stderr, flush=True)
    assert query[2] in errors if errors else True
