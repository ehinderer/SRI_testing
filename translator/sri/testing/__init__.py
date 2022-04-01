import re
from typing import Optional

from bmt import Toolkit
from translator.trapi import set_trapi_version

"""
Biolink Model related support code for the tests
"""

# Biolink Release number should be a well-formed Semantic Version)
semver_pattern = re.compile(r"^\d+\.\d+\.\d+$")


def get_biolink_model_schema(biolink_release: Optional[str] = None) -> Optional[str]:
    """
    Get Biolink Model Schema
    """
    if biolink_release:
        if not semver_pattern.fullmatch(biolink_release):
            raise TypeError(
                "The 'biolink_release' argument '"
                + biolink_release
                + "' is not a properly formatted 'major.minor.patch' semantic version?"
            )
        schema = f"https://raw.githubusercontent.com/biolink/biolink-model/{biolink_release}/biolink-model.yaml"
        return schema
    else:
        return None


_bmt_toolkit: Optional[Toolkit] = None


def get_toolkit() -> Optional[Toolkit]:
    global _bmt_toolkit
    if not _bmt_toolkit:
        raise RuntimeError("Biolink Model Toolkit is not initialized?!?")
    return _bmt_toolkit


def set_global_environment(biolink_version, trapi_version):
    # Note here that we let BMT control which version of Biolink we are using,
    # unless the value for which is overridden on the CLI
    global _bmt_toolkit

    # Toolkit takes a couple of seconds to initialize,
    # so don't want it initialized per-test; however,
    # TODO: if we eventually need per-test settings, maybe we should cache various versions locally
    #       (see https://github.com/biolink/kgx/blob/master/kgx/utils/kgx_utils.py#L304).
    if biolink_version:
        biolink_schema = get_biolink_model_schema()
        _bmt_toolkit = Toolkit(biolink_schema)
    else:
        _bmt_toolkit = Toolkit()

    # The TRAPI version is set to a hard coded default
    # if not set by a non-empty trapi_version here
    set_trapi_version(trapi_version)
