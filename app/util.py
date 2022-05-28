"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional

import logging

from translator.sri.testing.processor import CMD_DELIMITER, run_command
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()


STRI = '='*27 + ' short test summary info ' + '='*27


def _parse_result(raw_report: str) -> str:
    """
    Extract summary of Pytest output as SRI Testing report.
    TODO: raw passthrough method needs to be further refined(?)
    :param raw_report: str, raw Pytest output
    :return: str, short summary of test outcome (mostly errors)
    """
    if not raw_report:
        return ""
    part = raw_report.split(STRI)
    if len(part) > 1:
        return part[-1]
    else:
        return part[0]


def run_onehop_test_harness(
    trapi_version: Optional[str] = None,
    biolink_version: Optional[str] = None,
    triple_source: Optional[str] = None,
    ara_source:  Optional[str] = None,
    one: bool = False
) -> Optional[str]:
    """
    Run the SRT Testing test harness as a worker process.

    :param trapi_version: Optional[str], TRAPI version assumed for test run (default: None)

    :param biolink_version: Optional[str], Biolink Model version used in test run (default: None)

    :param triple_source: Optional[str], 'REGISTRY', directory or file from which to retrieve triples
                                         (Default: 'REGISTRY', which triggers the use of metadata, in KP entries
                                          from the Translator SmartAPI Registry, to configure the tests).

    :param ara_source: Optional[str], 'REGISTRY', directory or file from which to retrieve ARA Config.
                                         (Default: 'REGISTRY', which triggers the use of metadata, in ARA entries
                                         from the Translator SmartAPI Registry, to configure the tests).

    :param one: bool, Only use first edge from each KP file (default: False).

    :return: str, session identifier for this testing run
    """

    command_line: str = f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} pytest -rA test_onehops.py"
    command_line += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
    command_line += f" --Biolink_Version={biolink_version}" if biolink_version else ""
    command_line += f" --triple_source={triple_source}" if triple_source else ""
    command_line += f" --ARA_source={ara_source}" if ara_source else ""
    command_line += " --one" if one else ""

    logger.debug(f"run_onehop_test_harness() cmd: {command_line}")

    session_id, result = run_command(command_line)

    report: Optional[str] = None
    if session_id:
        if result:
            report = _parse_result(result)
    else:
        if result:
            report = result  # likely a raw error message
        else:
            report = f"Command line {command_line} failed to execute?"

    return report
