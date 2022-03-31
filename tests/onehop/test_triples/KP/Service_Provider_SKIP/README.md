# Service Provider Tests

The JSON files assume that these APIs will be queried through BTE's TRAPI endpoint for querying individual SmartAPIs (accessible through the URLs provided). 

### Notes:
- Tests are also described as queries that can be made directly to the API, in the additional README files:
    - [MyGene](mygene_README.md)
    - [MyChem](mychem_README.md)
    - [MyDisease](mydisease_README.md)
    - [Ontology_Lookup_Service](Ontology_Lookup_Service_README.md)
    - [OpenTarget](OpenTarget_README.md)

- Notice that many API endpoints do not handle curies (ID prefixes) or predicates. The format of these queries is specified by the x-bte-annotated endpoint in the SmartAPI registry file. 
- Predicates may change over time, as we change our biolink predicate choices and as the Biolink Model predicates change