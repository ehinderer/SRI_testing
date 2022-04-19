# Shared Translator Modules

This package contains various utility modules supporting specific subtypes of SRI Testing:

- [translator.biolink](biolink): Biolink Model compliance testing
    - [report_missing_predicates.py](./biolink/report_missing_predicates.py): a utility script for reporting predicates missing from the Biolink Model.
- [translator.trapi](trapi): Translator Reasoner Application Programming Interface interfacing code.
- [translator.sri.testing](sri/testing): script for creating test data templates; utility method for initializing globally shared parameters (default Biolink Model and TRAPI versions used for tests); and Jupyter Notebook to facilitate access to Translator SmartAPI TRAPI entries for KPs and ARAs.
    - [translator.sri.testing.util](sri/testing/util): modules for ontology knowledge provider interfacing.


