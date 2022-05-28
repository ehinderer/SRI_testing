"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional, List

import logging
from uuid import UUID

from translator.sri.testing.processor import CMD_DELIMITER, WorkerProcess
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()

#
# Application-specific parameters
#
DEFAULT_WORKER_TIMEOUT = 120  # 2 minutes for small PyTests?

_STRI = '='*27 + ' short test summary info ' + '='*28 + '\n'


def _parse_result(raw_report: str) -> List[str]:
    """
    Extract summary of Pytest output as SRI Testing report.
    TODO: raw passthrough method needs to be further refined(?)
    :param raw_report: str, raw Pytest output
    :return: str, short summary of test outcome (mostly errors)
    """
    if not raw_report:
        return ["Empty report?"]
    part = raw_report.split(_STRI)
    if len(part) > 1:
        report = part[-1].strip()
    else:
        report = part[0].strip()
    return report.split("\n")


class OneHopTestHarness:

    def __init__(self, timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT):
        self._session_id: Optional[UUID] = None
        self._result: Optional[str] = None
        self._report: List[str] = list()
        self._timeout: Optional[int] = timeout

    def get_session_id(self) -> str:
        return str(self._session_id)

    def get_report(self) -> List[str]:
        return self._report

    def run(
            self,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            triple_source: Optional[str] = None,
            ara_source:  Optional[str] = None,
            one: bool = False
    ) -> List[str]:
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

        :param one: bool, Only use first edge from each KP file (default: False if omitted).

        :return: str, session identifier for this testing run
        """

        command_line: str = f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} " + \
                            f"pytest -rA --tb=line --log-cli-level=ERROR test_onehops.py"
        command_line += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
        command_line += f" --Biolink_Version={biolink_version}" if biolink_version else ""
        command_line += f" --triple_source={triple_source}" if triple_source else ""
        command_line += f" --ARA_source={ara_source}" if ara_source else ""
        command_line += " --one" if one else ""

        logger.debug(f"OneHopTestHarness.run() command line: {command_line}")
        wp = WorkerProcess(self._timeout)
        self._session_id = wp.run_command(command_line)

        if self._session_id:
            self._result = wp.get_output(self._session_id)
            if self._result:
                self._report = _parse_result(self._result)
        else:
            if self._result:
                self._report = [self._result]  # likely a simple raw error message
            else:
                self._report = [f"Worker process failed to execute command line '{command_line}'?"]

        # TODO: it would be nice to also report the *actual* TRAPI
        #       and Biolink Model versions used in the testing,
        #       but this may technically be tricky at this code level.
        return self._report
