"""
Biolink Model related support code for the tests
"""
import re
from typing import Optional

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