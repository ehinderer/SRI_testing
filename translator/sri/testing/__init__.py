from translator.biolink import set_biolink_model_toolkit
from translator.trapi import set_trapi_version


def set_global_environment(biolink_version=None, trapi_version=None):
    set_biolink_model_toolkit(biolink_version)
    set_trapi_version(trapi_version)
