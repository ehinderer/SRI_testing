"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional

import logging
from uuid import UUID

from translator.sri.testing.processor import CMD_DELIMITER, run_command
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()

#
# Application-specific parameters
#
DEFAULT_WORKER_TIMEOUT = 120  # 2 minutes for small PyTests?

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


class OneHopTestHarness:

    def __init__(self, timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT):
        self.session_id: Optional[UUID] = None
        self.result: Optional[str] = None
        self.report: Optional[str] = None
        self.timeout: Optional[int] = timeout

    def get_session_id(self):
        return self.session_id

    def get_report(self):
        return self.report

    def run(
            self,
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

        logger.debug(f"OneHopTestHarness.run() command line: {command_line}")

        self.session_id, self.result = run_command(command_line, self.timeout)

        if self.session_id:
            if self.result:
                self.report = _parse_result(self.result)
        else:
            if self.result:
                self.report = self.result  # likely a simple raw error message
            else:
                self.report = f"Worker process failed to execute command line '{command_line}'?"

        return self.report
