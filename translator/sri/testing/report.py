"""
SRI Testing Report utility functions.
"""
from os import makedirs
from typing import Optional, Dict, Tuple

import re

from uuid import UUID, uuid4

from translator.sri.testing.processor import CMD_DELIMITER, WorkerProcess
from tests.onehop import ONEHOP_TEST_DIRECTORY

import logging
logger = logging.getLogger()

#
# Application-specific parameters
#
DEFAULT_WORKER_TIMEOUT = 120  # 2 minutes for small PyTests?

#
# June 2022 - new reporting strategy, based on cached Pytest exported summary and details files
#


TEST_RESULTS_DIR = "test_results"

UNIT_TEST_NAME_PATTERN = re.compile(
    r"^test_onehops.py:(\d+)?:(test_trapi_(?P<component>kp|ara)s|\s)(\[(?P<case>[^]]+)])"
)
TEST_CASE_PATTERN = re.compile(
    r"^(?P<resource_id>[^#]+)(#(?P<edge_num>\d+))?(-(?P<test_id>.+))?$"
)


def parse_unit_test_name(unit_test_key: str) -> Tuple[str, str, str, int, str, str]:
    """
    Reformat (test run key) source identifier into a well-behaved test file name.
    :param unit_test_key: original full unit test label
    :param status: test outcome (i.e. PASSED, FAILED, SKIPPED)

    :return: Tuple[ component, ara_id, kp_id, int(edge_num), test_id, edge_details_file_path]
    """
    unit_test_name = unit_test_key.split('/')[-1]

    psf = UNIT_TEST_NAME_PATTERN.match(unit_test_name)
    if psf:
        component = psf["component"]
        if component:
            component = component.upper()
            case = psf["case"]
            if case:
                tci = TEST_CASE_PATTERN.match(case)
                if tci:
                    resource_id = tci["resource_id"]
                    if resource_id:
                        rpart = resource_id.split("|")
                        if len(rpart) > 1:
                            ara_id = rpart[0]
                            kp_id = rpart[1]
                        else:
                            ara_id = None
                            kp_id = rpart[0]
                        edge_num = tci["edge_num"]
                        if edge_num:
                            test_id = tci["test_id"] if tci["test_id"] else "input"

                            # test details file path
                            edge_details_file_path: str = component
                            edge_details_file_path += f"/{ara_id}" if ara_id else ""
                            edge_details_file_path += f"/{kp_id}/{kp_id}-{edge_num}"

                            return component, ara_id, kp_id, int(edge_num), test_id, edge_details_file_path

    raise RuntimeError(f"parse_unit_test_name() '{unit_test_key}' has unknown format?")


def unit_test_report_filepath(test_run_id: str, unit_test_file_path: str) -> str:
    """
    Generate a report file path for a specific unit test result, compiled from descriptive components.

    :param test_run_id: str, caller-defined test run ("session") identifier, e.g. UUID string or 'test_results'
    :param unit_test_file_path: str, normalized unit test file path, something like
                                     "KP/Test_KP_1/1/inverse_by_new_subject_FAILED.json"

    :return: str, (posix) unit test file path
    """
    assert test_run_id, f"unit_test_report_filepath() empty 'test_run_id'"
    assert unit_test_file_path, f"unit_test_report_filepath() empty 'unit_test_file_path'"

    path_parts = [TEST_RESULTS_DIR, test_run_id] + unit_test_file_path.split('/')

    unit_test_dir_path = '/'.join(path_parts[:-1])
    try:
        makedirs(f"{unit_test_dir_path}", exist_ok=True)
    except OSError as ose:
        pass

    unit_test_file_path = '/'.join(path_parts)
    unit_test_file_path = f"{unit_test_file_path}.json"

    return unit_test_file_path


class TestRunReport:

    def __init__(self, session_id: str):
        self._session_id = session_id

    def _output(self, report_type: str, report_file: str):
        report_file_path = f"test_results/{self._session_id}/{report_file}.json"
        report: Optional[str] = None
        try:
            with open(report_file_path, 'r') as report_file:
                report = report_file.read()
        except OSError as ose:
            logger.warning(f"{report_type} file '{report_file_path}' not (yet) accessible: {str(ose)}?")
        return report

    def get_summary(self) -> Optional[str]:
        return self._output(report_type="Summary", report_file="onehops_test_summary")

    def get_details(self, unit_test_id: str) -> Optional[str]:
        return self._output(report_type="Details", report_file=unit_test_id)


class OneHopTestHarness:
    # Caching of processes indexed by session_id (UUID as string)
    _session_id_2_testrun: Dict = dict()

    def __init__(self, timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT):

        # each test harness run has its own unique session identifier
        self._session_id: UUID = uuid4()

        self._command_line: Optional[str] = None
        self._process: Optional[WorkerProcess] = None

        # Deprecated internal variables
        # self._result: Optional[str] = None
        # self._report: Optional[SRITestReport] = None

        self._timeout: Optional[int] = timeout

    def get_worker(self) -> Optional[WorkerProcess]:
        return self._process

    # def get_result(self) -> Optional[str]:
    #     return self._result

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
            ara_source: Optional[str] = None,
            one: bool = False,
            log: Optional[str] = None
    ):
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

        :param log: Optional[str], desired Python logger level label (default: None, implying default logger)

        :return: None
        """
        session_id_string: str = str(self._session_id)

        self._command_line = f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} " + \
                             f"pytest --tb=line -vv"
        self._command_line += f" --log-cli-level={log}" if log else ""
        self._command_line += f" test_onehops.py"
        self._command_line += f" --session_id={session_id_string}"
        self._command_line += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
        self._command_line += f" --Biolink_Version={biolink_version}" if biolink_version else ""
        self._command_line += f" --triple_source={triple_source}" if triple_source else ""
        self._command_line += f" --ARA_source={ara_source}" if ara_source else ""
        self._command_line += " --one" if one else ""

        logger.debug(f"OneHopTestHarness.run() command line: {self._command_line}")

        self._process = WorkerProcess(self._timeout)
        self._process.run_command(self._command_line)
        self._session_id_2_testrun[session_id_string] = self

    @classmethod
    def get_summary(cls, session_id: str) -> Optional[str]:
        """
        Looks up the OneHopTestHarness for the specified 'session_id_str'
        then returns its (possibly just-in-time generated or cached) test report.

        :param session_id: str, UUID session_id of the OneHopTestHarness running the test

        :return: Optional[Union[str, SRITestSummary]], list of available SRI Testing unit test results
        """
        assert session_id, "Null or empty Session Identifier?"

        return TestRunReport(session_id).get_summary()

    @classmethod
    def get_details(cls, session_id: str, unit_test_id: str) -> Optional[str]:
        """
        Looks up the OneHopTestHarness for the specified 'session_id_str'
        then returns its (possibly just-in-time generated or cached) test report.

        :param session_id: str, UUID session_id of the OneHopTestHarness running the test
        :param unit_test_id: str, identifier of unit test for which details are needed

        :return: Optional[str], structured JSON report from the OneHops testing of target KPs & ARAs,
                 or an exceptional error message, or None (if the details are not (yet) available)
        """
        assert session_id, "Null or empty Session Identifier?"
        assert unit_test_id, "Null or empty Unit Test Identifier?"

        return TestRunReport(session_id).get_details(unit_test_id)
