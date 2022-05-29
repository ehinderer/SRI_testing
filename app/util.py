"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional, List, Dict

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

    # Caching of processes indexed by session_id (UUID as string)
    _session_id_2_testrun: Dict = dict()
    
    def __init__(self, timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT):
        self._command_line: Optional[str] = None
        self._process: Optional[WorkerProcess] = None
        self._session_id: Optional[UUID] = None
        self._result: Optional[str] = None
        self._report: List[str] = list()
        self._timeout: Optional[int] = timeout

    def get_worker(self) -> Optional[WorkerProcess]:
        return self._process

    def set_result(self, result: Optional[str]):
        self._result = result

    def get_result(self) -> Optional[str]:
        return self._result

    def set_report(self, report: List[str]):
        self._report = report

    def get_session_id(self) -> Optional[str]:
        if self._session_id:
            return str(self._session_id)
        else:
            return None

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

        :param one: bool, Only use first edge from each KP file (default: False if omitted).

        :return: str, UUID session identifier for this testing run
        """
        session_id_string: Optional[str]

        if self._session_id:
            # Enforcing idempotency: this OneHopTestHarness run is already initialized
            session_id_string = self.get_session_id()
            if session_id_string in self._session_id_2_testrun:
                logger.warning(
                    "This OneHopTestHarness test run is already running! " +
                    f"Try accessing the report with UUID '{session_id_string}'")
            else:
                logger.error(f"This OneHopTestHarness test run has an unmapped or expired UUID '{session_id_string}'")
        else:
            self._command_line = f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} " + \
                                 f"pytest -rA --tb=line --log-cli-level=ERROR test_onehops.py"
            self._command_line += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
            self._command_line += f" --Biolink_Version={biolink_version}" if biolink_version else ""
            self._command_line += f" --triple_source={triple_source}" if triple_source else ""
            self._command_line += f" --ARA_source={ara_source}" if ara_source else ""
            self._command_line += " --one" if one else ""

            logger.debug(f"OneHopTestHarness.run() command line: {self._command_line}")
            self._process = WorkerProcess(self._timeout)
            self._session_id = self._process.run_command(self._command_line)

            session_id_string = self.get_session_id()
            self._session_id_2_testrun[session_id_string] = self

        return session_id_string
    
    def get_testrun_report(self):
        # generate and cache the report the first time this method is called
        if not self._report:
            if self._session_id:
                self._result = self._process.get_output(self._session_id)
                if self._result:
                    self._report = _parse_result(self._result)
            else:
                if self._result:
                    self._report = [self._result]  # likely a simple raw error message
                else:
                    self._report = [f"Worker process failed to execute command line '{self._command_line}'?"]

            # TODO: it would be nice to also directly report back the *actual*
            #       versions of TRAPI and Biolink Model used in the testing,
            #       but this may be technically tricky at the moment.
        return self._report
    
    @classmethod
    def get_report(cls, session_id_str: str) -> List[str]:
        """

        :param session_id_str: str, UUID session_id of the OneHopTestHarness running the test
        :return: List[str], line-by-line Pytest report from the OneHopTest of target KPs & ARAs
        """
        assert session_id_str  # should not be empty
        
        if session_id_str not in cls._session_id_2_testrun:
            return [f"Unknown Worker Process 'session_id': {session_id_str}"]
        
        testrun = cls._session_id_2_testrun[session_id_str]
        
        return testrun.get_testrun_report()
