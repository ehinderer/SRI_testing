# One-hop Tests

This suite tests our ability to retrieve given triples, which we know exist, from their KPs under a variety of transformations, both directly, and via ARAs.

The tests are generated from the files in `test_triples/KP`.  For each KP, it is queried for the triples contained in its associated json file.  Then, ARAs are
queried for those triples according to the annotations in `test_triples/ARA` denoting from which KPs each ARA receives information.

- [Configuring the Tests](#configuring-the-tests)
    - [KP Instructions](#kp-instructions)
    - [ARA Instructions](#ara-instructions)
- [Running the Tests](#running-the-tests)
    - [Running only the KP tests](#running-only-the-kp-tests)
    - [Running only the ARA tests](#running-only-the-ara-tests)

## Configuring the Tests

### KP Instructions

For each KP, we need a file with one triple of each type that the KP can provide.  For instance, `test_triples/KP/Test_KP/Automat_Human_GOA.json` contains the following json:

```
{
    "url": "https://automat.renci.org/ontological-hierarchy/1.2",
    "TRAPI": true,
    "edges": [
        {
            "subject_category": "biolink:AnatomicalEntity",
            "object_category": "biolink:AnatomicalEntity",
            "predicate": "biolink:subclass_of",
            "subject": "UBERON:0005453",
            "object": "UBERON:0035769"
        },
        {
            "subject_category": "biolink:CellularComponent",
            "object_category": "biolink:AnatomicalEntity",
            "predicate": "biolink:subclass_of",
            "subject": "GO:0005789",
            "object": "UBERON:0000061"
        },
        {
            "subject_category": "biolink:PhenotypicFeature",
            "object_category": "biolink:Disease",
            "predicate": "biolink:subclass_of",
            "subject": "EFO:1001927",
            "object": "MONDO:0005093"
        }
    ]
}
```

This KP provides three kinds of edges: AnatomicalEntity-subclass_of->AnatomicalEntity, CellularComponent-subclass_of->AnatomicalEntity, and PhenotypicFeature-subclass_of->Disease. For each of these kinds of edges, we have an entry in the file with a specific subject and object, and from these, we can create a variety of tests.

To aid KPs in creating these json files, we have generated templates in `templates/KP` using the predicates endpoint or smartAPI Registry MetaKG entries, which contains the edge types.
Note that the templates are built from KP metadata and are a good starting place, but they are not necessarily a perfect match to the desired test triples.
In particular, if a template contains an entry for two edges, where one edge can be fully calculated given the other, then there is no reason to include 
test data for the derived edge.  For instance, there is no need to include test data for an edge in one direction, and its inverse in the other direction. Here
we will be assuming (and testing) the ability of the KP to handle inverted edges whether they are specified or not.  Similarly, if a KP has
"increases_expression_of" edges, there is no need to include "affects_expression_of" in the test triples, unless there is data that is only known at the
more general level.  If, say, there are triples where all that is known is an "affects_expression_of" predicate, then that should be included.

So the steps for a KP:

1. copy a template json from `templates` into a distinctly named file in a suitable (KP-specific) subfolder location inside `test_triples/KP`
2. filter out logically derivable template entries
3. fill in the subject and object entries for each triple with a real identifiers that should be retrievable from the KP

Note: you can selectively disable ('skip') specific test files or whole subfolders of such files by appending *_SKIP* to the specific file or subfolder name. 

### ARA Instructions

For each ARA, we want to ensure that it is able to extract information correctly from the KPs.  To do this, we need to know which KPs each ARA interacts with.  We have generated template ARA json files under `templates/ARA` that contains annotations linking the ARA to all KPs.  For instance (under _tests/onehop/test_triples/ARA/Test_ARA/ARAGORN.json_):

```
{
    "url": "https://aragorn.renci.org/1.2",
    "TRAPI": true,
    "KPs": [
        "Automat Panther",
        "Automat Ontological Hierarchy"
    ]
}
```

In order to correctly link ARAs to KPs, ARAs will need to:

1. Copy the ARA template from `templates` into a distinctly named file, in a suitable (ARA-specific) subfolder location inside `test_triples/ARA`
2. Edit the copied file to remove KPs that the ARA does not access.

Note: as with the KP template files, you can selectively disable ('skip') specific ARA test files or whole subfolders of such files by appending *_SKIP* to the specific file or subfolder name. 

## Running the Tests

Tests are implemented with pytest.  To run all tests, simply run:

```
pytest test_onehops.py
```

But this takes quite some time, so frequently you will want to limit the tests run.

### Running only the KP tests

To run only KP tests:
```
pytest test_onehops.py::test_trapi_kps
```

To run KP Tests, but only using one triple from each KP:
```
pytest test_onehops.py::test_trapi_kps --one
```

To restrict test triples to those from a given directory or file:
```
pytest test_onehops.py::test_trapi_kps --triple_source=<triple_source>
```
e.g.
```
pytest test_onehops.py::test_trapi_kps --triple_source=test_triples/KP/Ranking_Agent
```
or
```
pytest test_onehops.py::test_trapi_kps --triple_source=test_triples/KP/Ranking_Agent/Automat_CTD.json
```

### Running only the ARA tests

To run only ARA tests (testing all ARAs for all KPs)
```
pytest test_onehops.py::test_trapi_aras
```

Options for restricting test triples for KPs also work for ARAs.  To test a single triple from the Automat CTD against all ARAs that use that KP:
```
pytest test_onehops.py::test_trapi_aras --one --triple_source=test_triples/KP/Ranking_Agent/Automat_CTD.json
```

The ARAs can also be restricted to a particular json or directory, e.g.

```
pytest test_onehops.py::test_trapi_aras --one --triple_source=test_triples/KP/Ranking_Agent/Automat_CTD.json --ARA_source=test_triples/ARA/Ranking_Agent/Strider.json
```
