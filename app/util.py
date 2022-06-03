"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional, Union, List, Dict
from os import path
import time
from uuid import UUID

import re

from tests import TEST_DATA_DIR
from translator.sri.testing.processor import CMD_DELIMITER, WorkerProcess
from tests.onehop import ONEHOP_TEST_DIRECTORY

import logging
logger = logging.getLogger()

#
# Application-specific parameters
#
DEFAULT_WORKER_TIMEOUT = 120  # 2 minutes for small PyTests?

SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN = re.compile(rf"=+\sshort\stest\ssummary\sinfo\s=+(\r?\n)")

#
# Examples:
# "PASSED test_onehops.py::test_trapi_aras[Test_ARA.json_Test KP_0-by_subject]"
# "SKIPPED [11] test_onehops.py:32: "
# "FAILED test_onehops.py::tes
# t_trapi_aras[Test_ARA.json_Test KP_0-by_subject]"
PASSED_SKIPPED_FAILED_PATTERN = re.compile(
    r"^(?P<outcome>PASSED|SKIPPED|FAILED)\s(\[\d+]\s)?test_onehops.py:(\d+)?:" +
    r"(test_trapi_(?P<component>kp|ara)s|\s)?(\[(?P<case>[^]]+)])?(?P<tail>.+)?$"
)

PYTEST_SUMMARY_PATTERN = re.compile(
    r"^=+(\s(?P<passed>\d+)\spassed,?)?(\s(?P<failed>\d+)\sfailed,?)?"
    r"(\s(?P<skipped>\d+)\sskipped,?)?(\s(?P<warning>\d+)\swarning)?.+$"
)

"""
TestReport is a multi-level indexed
dictionary of captured error messages,
(including a summary count).
"""
SRITestReport = Dict[
        str,  # component in ["INPUT", "KP", "ARA", "SUMMARY"]
        Dict[
            str,  # outcome in ["PASSED", "FAILED", "SKIPPED", "WARNING"]
            Union[
                str,   # summary counts
                Dict[  # test case error messages
                    str,  # case identifier
                    List[str]
                ]
            ]
        ]
    ]


def add_report_slot(report: SRITestReport, component: str, outcome: str, case: str):
    if component not in report:
        report[component] = dict()
    if outcome not in report[component]:
        report[component][outcome] = dict()
    if case not in report[component][outcome]:
        report[component][outcome][case] = list()


def parse_result(raw_report: str) -> SRITestReport:
    """
    Extract summary of Pytest output as SRI Testing report.

    :param raw_report: str, raw Pytest stdout content from test run with the -r option.

    :return: TestReport, a structured summary of OneHopTestHarness test outcomes
    """
    if not raw_report:
        return dict()

    part = SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.split(raw_report)
    if len(part) > 1:
        output = part[-1].strip()
    else:
        output = part[0].strip()

    # This splits the test section of interest
    # into lines, to facilitate further processing
    top_level = output.replace('\r', '')
    top_level = top_level.split('\n')

    report: SRITestReport = dict()
    current_component = current_outcome = current_case = "UNKNOWN"
    for line in top_level:
        line = line.strip()  # spurious leading and trailing whitespace removed
        if not line:
            continue  # ignore blank lines
        psp = PYTEST_SUMMARY_PATTERN.match(line)
        if psp:
            # PyTest summary line encountered?
            # Extract and send it back in the report.
            p_num = psp["passed"]
            f_num = psp["failed"]
            s_num = psp["skipped"]
            w_num = psp["warning"]
            if "SUMMARY" not in report:
                report["SUMMARY"] = {
                    "PASSED":  p_num if p_num else "0",
                    "FAILED":  f_num if f_num else "0",
                    "SKIPPED": s_num if s_num else "0",
                    "WARNING": w_num if w_num else "0"
                }
        else:
            # all other lines are assumed to be specific PyTest unit test outcomes
            psf = PASSED_SKIPPED_FAILED_PATTERN.match(line)
            if psf:
                outcome: str = psf["outcome"]
                if outcome != current_outcome:
                    current_outcome = outcome

                component: Optional[str] = psf["component"]
                if not component:
                    component = "INPUT"
                if component != current_component:
                    current_component = component.upper()

                case: Optional[str] = psf["case"]
                if case != current_case:
                    current_case = case

                add_report_slot(report, current_component, current_outcome, current_case)

                tail: Optional[str] = psf["tail"]
                if tail:
                    tail = tail.strip()  # strip off spurious blanks on the ends
                    report[current_component][current_outcome][current_case].append(tail)
            else:
                add_report_slot(report, current_component, current_outcome, current_case)
                report[current_component][current_outcome][current_case].append(line)

    return report


class OneHopTestHarness:

    # Caching of processes indexed by session_id (UUID as string)
    _session_id_2_testrun: Dict = dict()
    
    def __init__(self, timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT):
        self._command_line: Optional[str] = None
        self._process: Optional[WorkerProcess] = None
        self._session_id: Optional[UUID] = None
        self._result: Optional[str] = None
        self._report: Optional[SRITestReport] = None
        self._timeout: Optional[int] = timeout

    def get_worker(self) -> Optional[WorkerProcess]:
        return self._process

    def get_result(self) -> Optional[str]:
        return self._result

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
                                 f"pytest -rA --tb=line -vv --log-cli-level=ERROR test_onehops.py"
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
    
    def get_testrun_report(self) -> Optional[Union[str, SRITestReport]]:
        """
        Generates and caches a OneHopTestHarness test report the first time this method is called.

        :return: Optional[Union[str, TestReport]], structured Pytest report from the OneHopTest of
                 target KPs & ARAs, or a single string global error message, or None (if still unavailable)
        """
        if not self._report:
            if self._session_id:
                self._result = self._process.get_output(self._session_id)
                if self._result:
                    # ts stores the time in seconds
                    ts = time.time()
                    sample_file_path = path.join(TEST_DATA_DIR, f"sample_pytest_report_{ts}.txt")
                    with open(sample_file_path, "w") as sf:
                        sf.write(self._result)

                    self._report = parse_result(self._result)
            else:
                if self._result:
                    self._report = [self._result]  # likely a simple raw error message from a global error
                else:
                    # totally opaque OneHopTestHarness test run failure?
                    self._report = [f"Worker process failed to execute command line '{self._command_line}'?"]
            # TODO: at this point, we might wish to persist the generated reports
            #       onto the local hard disk system, indexed by the session_id
        return self._report
    
    @classmethod
    def get_report(cls, session_id_str: str) -> Optional[Union[str, SRITestReport]]:
        """
        Looks up the OneHopTestHarness for the specified 'session_id_str'
        then returns its (possibly just-in-time generated or cached) test report.

        :param session_id_str: str, UUID session_id of the OneHopTestHarness running the test

        :return: Optional[Union[str, TestReport]], structured Pytest report from the OneHopTest of
                 target KPs & ARAs, or a single string global error message, or None (if still unavailable)
        """
        assert session_id_str  # should not be empty
        
        if session_id_str not in cls._session_id_2_testrun:
            return f"Unknown Worker Process 'session_id': {session_id_str}"
        
        testrun = cls._session_id_2_testrun[session_id_str]
        
        return testrun.get_testrun_report()
