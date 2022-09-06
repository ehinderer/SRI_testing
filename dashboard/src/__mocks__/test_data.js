export const PYTEST_REPORT = {
    "id": "2023-13-32_24-61-61",
    "KP": {
        "test-kp-1": [
            {
                "idx": 0,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "inverse_by_new_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "by_object": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)' or all test case S-P-O triples from resource test location."
                        ]
                    },
                    "raise_object_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    }
                }
            },
            {
                "idx": 1,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "inverse_by_new_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 2,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "inverse_by_new_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 3,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "inverse_by_new_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 4,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "inverse_by_new_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    }
                }
            },
            {
                "idx": 5,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "inverse_by_new_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    }
                }
            }
        ],
        "test-kp-2": [
            {
                "idx": 0,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "inverse_by_new_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "by_object": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_subject_entity": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_object_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(UBERON:0005453$biolink:AnatomicalEntity)--[biolink:subclass_of]->(UBERON:0035769$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    }
                }
            },
            {
                "idx": 1,
                "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
                "predicate": "biolink:part_of",
                "subject": "PANTHER.FAMILY:PTHR34921",
                "object": "PANTHER.FAMILY:PTHR34921",
                "tests": {
                    "by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "inverse_by_new_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "by_object": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(GO:0005789$biolink:CellularComponent)--[biolink:subclass_of]->(UBERON:0000061$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    },
                    "raise_object_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(GO:0005789$biolink:CellularComponent)--[biolink:subclass_of]->(UBERON:0000061$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    }
                }
            }
        ]
    },
    "ARA": {
        "aragorn|test-kp-1": [
            {
                "idx": 0,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "by_object": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)' or all test case S-P-O triples from resource test location."
                        ]
                    },
                    "raise_object_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "PASSED": [
                            ""
                        ]
                    }
                }
            },
            {
                "idx": 1,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:NotABiolinkCategory)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'subject' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 2,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:NotABiolinkCategory)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: 'object' category 'biolink:NotABiolinkCategory' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 3,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:invalid_predicate]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: predicate 'biolink:invalid_predicate' is unknown?"
                        ]
                    }
                }
            },
            {
                "idx": 4,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(FOO:1234$biolink:GeneFamily)--[biolink:part_of]->(PANTHER.FAMILY:PTHR34921$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'subject' identifier 'FOO:1234' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    }
                }
            },
            {
                "idx": 5,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "by_object": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_object_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1$biolink:GeneFamily)--[biolink:part_of]->(BAR:6789$biolink:GeneFamily)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: namespace prefix of 'object' identifier 'BAR:6789' is unmapped to 'biolink:GeneFamily'?"
                        ]
                    }
                }
            }
        ],
        "aragorn|test-kp-2": [
            {
                "idx": 0,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "FAILED": [
                            "",
                            "TRAPI 1.2.0 query request"
                        ]
                    },
                    "by_object": {
                        "FAILED": [
                            "",
                            "Edge:"
                        ]
                    },
                    "raise_subject_entity": {
                        "FAILED": [
                            "",
                            "TRAPI 1.2.0 query request"
                        ]
                    },
                    "raise_object_by_subject": {
                        "FAILED": [
                            "",
                            "TRAPI 1.2.0 query request"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(UBERON:0005453$biolink:AnatomicalEntity)--[biolink:subclass_of]->(UBERON:0035769$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    }
                }
            },
            {
                "idx": 1,
                "subject_category": "UNKNOWN",
                "object_category": "UNKNOWN",
                "predicate": "UNKNOWN",
                "subject": "UNKNOWN",
                "object": "UNKNOWN",
                "tests": {
                    "by_subject": {
                        "FAILED": [
                            "",
                            "TRAPI 1.2.0 query request"
                        ]
                    },
                    "by_object": {
                        "PASSED": [
                            ""
                        ]
                    },
                    "raise_subject_entity": {
                        "SKIPPED": [
                            "test case S-P-O triple '(GO:0005789$biolink:CellularComponent)--[biolink:subclass_of]->(UBERON:0000061$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    },
                    "raise_object_by_subject": {
                        "FAILED": [
                            "",
                            "TRAPI 1.2.0 query request"
                        ]
                    },
                    "raise_predicate_by_subject": {
                        "SKIPPED": [
                            "test case S-P-O triple '(GO:0005789$biolink:CellularComponent)--[biolink:subclass_of]->(UBERON:0000061$biolink:AnatomicalEntity)' or all test case S-P-O triples from resource test location."
                        ]
                    }
                }
            }
        ]
    },
    "SUMMARY": {
        "FAILED": "6",
        "PASSED": "19",
        "SKIPPED": "63"
    }
}

export const MOCK_REGISTRY = {
    "total": 3,
    "hits": [
        {
            "info": {
                "title": "Unit Test Knowledge Provider 1",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:test-kp-1",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Knowledge Provider 2",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:test-kp-2",
                    "team": "Ranking Agent",
                    "biolink-version": "2.4.8"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_2.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Automatic Relay Agent",
                "version": "0.0.1",
                "x-translator": {
                    "infores": "infores:aragorn",
                    "component": "ARA",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
                }
            }
        }
    ]
}


export const MOLEPRO_REPORT = {
  "test_run_id": "2022-08-23_21-13-40",
  "summary": {
    "0": {
      "test_data": {
        "subject_category": "biolink:ChemicalSubstance",
        "object_category": "biolink:Disease",
        "predicate": "biolink:treats",
        "subject": "CHEBI:3002",
        "object": "MESH:D001249"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:3002$biolink:ChemicalSubstance)--[biolink:treats]->(MESH:D001249$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        }
      }
    },
    "1": {
      "test_data": {
        "subject_category": "biolink:ChemicalSubstance",
        "object_category": "biolink:ChemicalSubstance",
        "predicate": "biolink:has_metabolite",
        "subject": "CHEBI:16914",
        "object": "CHEMBL.COMPOUND:CHEMBL3544526"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:16914$biolink:ChemicalSubstance)--[biolink:has_metabolite]->(CHEMBL.COMPOUND:CHEMBL3544526$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        }
      }
    },
    "2": {
      "test_data": {
        "subject_category": "biolink:ChemicalSubstance",
        "object_category": "biolink:Assay",
        "predicate": "biolink:has_evidence",
        "subject": "CHEBI:52717",
        "object": "CHEMBL.ASSAY:CHEMBL768300"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:has_evidence]->(CHEMBL.ASSAY:CHEMBL768300$biolink:Assay)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:has_evidence' is unknown? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:Assay' is unknown?"
          ]
        }
      }
    },
    "3": {
      "test_data": {
        "subject_category": "biolink:ChemicalSubstance",
        "object_category": "biolink:ChemicalSubstance",
        "predicate": "biolink:correlated_with",
        "subject": "CHEBI:52717",
        "object": "CHEBI:90942"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:52717$biolink:ChemicalSubstance)--[biolink:correlated_with]->(CHEBI:90942$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        }
      }
    },
    "4": {
      "test_data": {
        "subject_category": "biolink:ChemicalSubstance",
        "object_category": "biolink:Disease",
        "predicate": "biolink:related_to",
        "subject": "CHEBI:4167",
        "object": "OMIM:125853"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(CHEBI:4167$biolink:ChemicalSubstance)--[biolink:related_to]->(OMIM:125853$biolink:Disease)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input subject Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'?"
          ]
        }
      }
    },
    "5": {
      "test_data": {
        "subject_category": "biolink:Disease",
        "object_category": "biolink:ChemicalSubstance",
        "predicate": "biolink:treated_by",
        "subject": "MONDO:0004981",
        "object": "CHEBI:4551"
      },
      "results": {
        "by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        },
        "inverse_by_new_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        },
        "by_object": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        },
        "raise_subject_entity": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        },
        "raise_object_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        },
        "raise_predicate_by_subject": {
          "outcome": "skipped",
          "errors": [
            "test case S-P-O triple '(MONDO:0004981$biolink:Disease)--[biolink:treated_by]->(CHEBI:4551$biolink:ChemicalSubstance)', since it is not Biolink Model compliant: BLM Version 2.2.16 Error in Input Edge: Input object Biolink class 'biolink:ChemicalSubstance' is deprecated: This class is deprecated in favor of 'small molecule.'? and BLM Version 2.2.16 Error in Input Edge: Input predicate 'biolink:treated_by' is non-canonical?"
          ]
        }
      }
    },
    "document_key": "KP/molepro/resource_summary"
  }
}
