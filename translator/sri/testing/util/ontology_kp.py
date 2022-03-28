"""
Ontology KP interface
"""
import requests

ONTOLOGY_KP_TRAPI_SERVER = "https://ontology-kp.apps.renci.org/query"

def post(url, message, params=None):
    """
    :param url
    :param message
    :param params
    """
    if params is None:
        response = requests.post(url, json=message)
    else:
        response = requests.post(url, json=message, params=params)
    if not response.status_code == 200:
        print('error:', response.status_code)
        return {}
    return response.json()


def convert_to_preferred(curie, allowed_list):
    """
    :param curie
    :param allowed_list
    """
    j = {'curies': [curie]}
    result = post('https://nodenormalization-sri.renci.org/get_normalized_nodes', j)
    new_ids = [v['identifier'] for v in result[curie]['equivalent_identifiers']]
    for nid in new_ids:
        if nid.split(':')[0] in allowed_list:
            return nid
    return None


def get_ontology_ancestors(curie, btype):
    """
    :param curie:
    :param btype:
    """
    m = {
        "message": {
            "query_graph": {
                "nodes": {
                    "a": {
                        "ids": [curie]
                    },
                    "b": {
                        "categories": [btype]
                    }
                },
                "edges": {
                    "ab": {
                        "subject": "a",
                        "object": "b",
                        "predicates": ["biolink:subclass_of"]
                    }
                }
            }
        }
    }
    response = post(ONTOLOGY_KP_TRAPI_SERVER, m)
    original_prefix = curie.split(':')[0]
    ancestors = []
    for result in response['message']['results']:
        parent_id = result['node_bindings']['b'][0]['id']
        if parent_id == curie:
            # everything is a sublcass of itself
            continue
        if not parent_id.startswith(original_prefix):
            # Don't give me UPHENO:000001 if I asked for a parent of HP:000012312
            continue
        # good enough
        ancestors.append(parent_id)
    return ancestors


def get_ontology_parent(curie, btype):
    """
    :param btype
    :param curie
    """
    # Here's a bunch of ancestors
    ancestors = get_ontology_ancestors(curie, btype)

    if not ancestors:
        return None

    # Now, to get the one closest to the input, we see
    # how many ancestors each ancestor has.  Largest number == lowest down
    ancestor_count = []
    for anc in ancestors:
        second_ancestors = get_ontology_ancestors(anc, btype)
        if not second_ancestors:
            continue
        ancestor_count.append((len(second_ancestors), anc))
    if ancestor_count:
        ancestor_count.sort()
        return ancestor_count[-1][1]
    else:
        return None


def get_parent(curie, entity_type):
    """
    :param curie:
    :param entity_type
    """
    # not every entity type can be parented, and not every prefix can be used
    preferred_prefixes = {'CHEBI', 'HP', 'MONDO', 'UBERON', 'CL', 'EFO', 'NCIT'}
    input_prefix = curie.split(':')[0]
    if input_prefix in preferred_prefixes:
        query_entity = curie
    else:
        query_entity = convert_to_preferred(curie, preferred_prefixes)
    if query_entity is None:
        return None
    preferred_parent = get_ontology_parent(query_entity, entity_type)
    if preferred_parent is None:
        return None
    original_parent_prefix = preferred_parent.split(':')[0]
    if original_parent_prefix == input_prefix:
        return preferred_parent
    return convert_to_preferred(preferred_parent, [input_prefix])


if __name__ == '__main__':
    # print(get_parent('PUBCHEM.COMPOUND:208898','biolink:ChemicalSubstance'))
    # print(get_parent('DRUGBANK:DB00394','biolink:ChemicalSubstance'))
    print(get_parent('CHEMBL.COMPOUND:CHEMBL2333026', 'biolink:ChemicalSubstance'))
