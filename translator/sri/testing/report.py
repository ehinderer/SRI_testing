"""
SRI Testing Report utility functions.
"""
from typing import Optional, Dict, Tuple, List

from os import makedirs, listdir
from os.path import normpath
from datetime import datetime
import re

import orjson

# TODO: should orjson be used instead of json below?
import json

from translator.sri.testing.processor import CMD_DELIMITER, WorkerProcess
from tests.onehop import ONEHOP_TEST_DIRECTORY

import logging

logger = logging.getLogger()

#
# Application-specific parameters
#
DEFAULT_WORKER_TIMEOUT = 120  # 2 minutes for small PyTests?

#
# June/July 2022 - new reporting strategy, based on an exported
# summary, edge details and unit test TRAPI JSON files
#


TEST_RESULTS_DIR = "test_results"

UNIT_TEST_NAME_PATTERN = re.compile(
    r"^test_onehops.py:(\d+)?:(test_trapi_(?P<component>kp|ara)s|\s)(\[(?P<case>[^]]+)])"
)
TEST_CASE_PATTERN = re.compile(
    r"^(?P<resource_id>[^#]+)(#(?P<edge_num>\d+))?(-(?P<test_id>.+))?$"
)

PERCENTAGE_COMPLETION_SUFFIX_PATTERN = re.compile(r"(\[\s*(?P<percentage_completion>\d+)%])?$")


def build_edge_details_file_path(component: str, ara_id: Optional[str], kp_id: str, edge_num: str):
    """
    Returns the file path to an edge details related file.

    :param component:
    :param ara_id:
    :param kp_id:
    :param edge_num:
    :return:
    """
    file_path: str = component
    file_path += f"/{ara_id}" if ara_id else ""
    file_path += f"/{kp_id}/{kp_id}-{edge_num}"
    return file_path


def parse_unit_test_name(unit_test_key: str) -> Tuple[str, str, str, int, str, str]:
    """
    Reformat (test run key) source identifier into a well-behaved test file name.
    :param unit_test_key: original full unit test label

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

                            return (
                                component,
                                ara_id,
                                kp_id,
                                int(edge_num),
                                test_id,
                                build_edge_details_file_path(component, ara_id, kp_id, edge_num)
                            )

    raise RuntimeError(f"parse_unit_test_name() '{unit_test_key}' has unknown format?")


def _get_details_file_path(component: str, resource_id: str, edge_num: str) -> str:
    """
    Web-wrapped version of the translator.sri.testing.report.get_edge_details_file_path() method.

    :param component:
    :param resource_id:
    :param edge_num:
    :return:
    """
    rid_part: List[str] = resource_id.split("-")
    if len(rid_part) > 1:
        ara_id = rid_part[0]
        kp_id = rid_part[1]
    else:
        ara_id = None
        kp_id = rid_part[0]

    edge_details_file_path: str = build_edge_details_file_path(component, ara_id, kp_id, edge_num)

    return edge_details_file_path


def _retrieve_document(report_type: str, report_file_path: str) -> Optional[str]:

    document: Optional[str] = None
    try:
        with open(report_file_path, 'r') as report_file:
            document = report_file.read()
    except OSError as ose:
        logger.warning(f"{report_type} file '{report_file_path}' not (yet) accessible: {str(ose)}?")

    return document


class OneHopTestHarness:

    @staticmethod
    def _generate_test_run_id() -> str:
        return datetime.now().strftime("%Y-%b-%d_%Hhr%M")

    # Caching of processes, indexed by test_run_id (timestamp identifier as string)
    _test_run_id_2_worker_process: Dict[str, Dict] = dict()

    def __init__(self, test_run_id: Optional[str] = None):
        """
        OneHopTestHarness constructor.

        :param Optional[str]: Optional[str], known timestamp test run identifier; internally created if 'None'
        """
        # each test harness run has its own unique timestamp identifier
        self._test_run_id: str

        self._command_line: Optional[str] = None
        self._process: Optional[WorkerProcess] = None
        self._timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT
        if test_run_id is not None:
            # should be an existing test run?
            self._test_run_id = test_run_id
            self._reload_run_parameters()
        else:
            # new test run? no run parameters to reload?
            self._test_run_id = self._generate_test_run_id()
            self._test_run_id_2_worker_process[self._test_run_id] = {
                "command_line": None,
                "worker_process": None,
                "timeout": self._timeout,
                "percentage_completion": 0
            }
        self.test_run_root_path: Optional[str] = None

    def get_test_run_id(self) -> Optional[str]:
        if self._test_run_id:
            return str(self._test_run_id)
        else:
            return None

    def run(
            self,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            triple_source: Optional[str] = None,
            ara_source: Optional[str] = None,
            one: bool = False,
            log: Optional[str] = None,
            timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT
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

        :param timeout: Optional[int], worker process timeout in seconds (defaults to about 120 seconds

        :return: None
        """
        # possible override of timeout here?
        self._timeout = timeout if timeout else self._timeout

        self._command_line = f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} " + \
                             f"pytest --tb=line -vv"
        self._command_line += f" --log-cli-level={log}" if log else ""
        self._command_line += f" test_onehops.py"
        self._command_line += f" --test_run_id={str(self._test_run_id)}"
        self._command_line += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
        self._command_line += f" --Biolink_Version={biolink_version}" if biolink_version else ""
        self._command_line += f" --triple_source={triple_source}" if triple_source else ""
        self._command_line += f" --ARA_source={ara_source}" if ara_source else ""
        self._command_line += " --one" if one else ""

        logger.debug(f"OneHopTestHarness.run() command line: {self._command_line}")

        self._process = WorkerProcess(self._timeout)

        self._process.run_command(self._command_line)

        # Cache run parameters for later access as necessary
        self._test_run_id_2_worker_process[self._test_run_id] = {
            "command_line": self._command_line,
            "worker_process": self._process,
            "timeout": self._timeout,
            
            # Percentage Completion needs to be updated later?
            "percentage_completion": 0
        }

    def get_worker(self) -> Optional[WorkerProcess]:
        return self._process

    def _set_percentage_completion(self, value: int):
        if self._test_run_id in self._test_run_id_2_worker_process:
            self._test_run_id_2_worker_process[self._test_run_id]["percentage_completion"] = value
        else:
            raise RuntimeError(
                f"_set_percentage_completion(): Unknown Worker Process for test run '{str(self._test_run_id)}'?"
            )
    
    def _get_percentage_completion(self) -> int:
        if self._test_run_id in self._test_run_id_2_worker_process and \
                "percentage_completion" in self._test_run_id_2_worker_process[self._test_run_id]:
            return self._test_run_id_2_worker_process[self._test_run_id]["percentage_completion"]
        else:
            raise RuntimeError(
                f"_get_percentage_completion(): Unknown Worker Process for test run '{str(self._test_run_id)}'?"
            )
    
    def _reload_run_parameters(self):
        if self._test_run_id in self._test_run_id_2_worker_process:
            run_parameters: Dict = self._test_run_id_2_worker_process[self._test_run_id]
            self._command_line = run_parameters["command_line"]
            self._process = run_parameters["worker_process"]
            self._timeout = run_parameters["timeout"]
            self._percentage_completion = run_parameters["percentage_completion"]
        else:
            raise RuntimeError(
                f"_reload_run_parameters(): Unknown Worker Process for test run '{str(self._test_run_id)}'?"
            )

    @classmethod
    def get_test_run_list(cls) -> List[str]:
        """
        :return: list of test run identifiers of completed test runs
        """
        test_results_directory = normpath(f"{ONEHOP_TEST_DIRECTORY}/test_results")
        test_run_list = listdir(test_results_directory)
        return test_run_list

    def get_status(self) -> int:
        """
        If available, returns the percentage completion of the currently active OneHopTestHarness run.

        :return: int, 0..100 indicating the percentage completion of the test run., -1 if test run not running?
        """
        if self._get_percentage_completion() < 100:
            for line in self._process.get_output(timeout=10):
                pc = PERCENTAGE_COMPLETION_SUFFIX_PATTERN.search(line)
                if pc and pc.group():
                    self._set_percentage_completion(int(pc["percentage_completion"]))

        return self._get_percentage_completion()

    def _absolute_report_file_path(self, report_file_path: str) -> str:
        absolute_file_path = normpath(f"{ONEHOP_TEST_DIRECTORY}/test_results/{self._test_run_id}/{report_file_path}")
        return absolute_file_path

    def get_summary(self) -> Optional[Dict]:
        """
        If available, returns a test result summary for the most recent OneHopTestHarness run.

        :return: Optional[str], JSON structured document summary of unit test results. 'None' if not (yet) available.
        """
        report_file_path = self._absolute_report_file_path("test_summary.json")

        document: Optional[str] = _retrieve_document(report_type="Summary", report_file_path=report_file_path)

        summary: Optional[Dict] = None
        if document:
            summary = orjson.loads(document)

        return summary

    def get_details(
            self,
            component: str,
            resource_id: str,
            edge_num: str,
    ) -> Optional[Dict]:
        """
        Returns test result details for given resource component and edge identities.

        :param component: str, Translator component being tested: 'ARA' or 'KP'
        :param resource_id: str, identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP')
                            or a hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                            (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
        :param edge_num: str, target input 'edge_num' edge number, as indexed as an edge of the JSON test run summary.

        :return: Optional[Dict], JSON structured document of test details for a specified test edge of a
                                 KP or ARA resource, or 'None' if the details are not (yet) available.
        """
        edge_details_file_path: str = _get_details_file_path(component, resource_id, edge_num)

        report_file_path = self._absolute_report_file_path(f"{edge_details_file_path}.json")

        document: Optional[str] = _retrieve_document(report_type="Details", report_file_path=report_file_path)

        details: Optional[Dict] = None
        if document:
            details = orjson.loads(document)

        return details

    def get_response_file_path(
            self,
            component: str,
            resource_id: str,
            edge_num: str,
            test_id: str,
    ) -> str:
        """
        Returns the TRAPI Response file path for given resource component, edge and unit test identities.

        :param component: str, Translator component being tested: 'ARA' or 'KP'
        :param resource_id: str, identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP')
                                 or a hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                            (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
        :param edge_num: str, target input 'edge_num' edge number, as indexed as an edge of the JSON test run summary.
        :param test_id: str, target unit test identifier, one of the values noted in the
                             edge leaf nodes of the JSON test run summary (e.g. 'by_subject', etc.).

        :return: str, TRAPI Response text data file path (generated, but not tested here for file existence)
        """
        edge_details_file_path: str = _get_details_file_path(component, resource_id, edge_num)

        response_file_path = self._absolute_report_file_path(f"{edge_details_file_path}-{test_id}-response.json")

        return response_file_path

    def _set_test_run_root_path(self):
        # subdirectory for local run output data
        self.test_run_root_path = f"{TEST_RESULTS_DIR}/{self._test_run_id}"
        makedirs(self.test_run_root_path, exist_ok=True)

    def _get_test_run_root_path(self) -> str:
        if not self.test_run_root_path:
            self._set_test_run_root_path()
        return self.test_run_root_path

    def save_test_run_summary(self, test_summary: Dict):
        """
        Persist summary of test run.

        :param test_summary:
        :return:
        """
        # Write out the whole List[str] of unit test identifiers, into one JSON summary file
        summary_filepath = f"{self._get_test_run_root_path()}/test_summary.json"
        with open(summary_filepath, 'w') as summary_file:
            json.dump(test_summary, summary_file, indent=4)

    def _unit_test_report_filepath(self, edge_details_file_path: str) -> str:
        """
        Generate a report file path for a specific unit test result, compiled from descriptive components.

        :return: str, (posix) unit test file path to root name of report file path (*without* file extension)
        """
        path_parts = [TEST_RESULTS_DIR, self._test_run_id] + edge_details_file_path.split('/')

        unit_test_dir_path = '/'.join(path_parts[:-1])
        try:
            makedirs(f"{unit_test_dir_path}", exist_ok=True)
        except OSError as ose:
            logger.warning(f"unit_test_report_filepath() makedirs exception: {str(ose)}")

        unit_test_file_path = '/'.join(path_parts)

        return unit_test_file_path

    @staticmethod
    def save_edge_details(
            test_details_file_path: str,
            edge_details_file_path: str,
            case_details: Dict
    ):
        """
        Persist test run details for a given test data edge.

        :param test_details_file_path:
        :param edge_details_file_path:
        :param case_details:
        :return:
        """
        with open(f"{test_details_file_path}.json", 'w') as details_file:
            test_details = case_details[edge_details_file_path]
            json.dump(test_details, details_file, indent=4)

    @staticmethod
    def save_unit_test_trapi_io(
            test_details_file_path: str,
            edge_details_file_path: str,
            case_response: Dict
    ):
        """
        Persist TRAPI request input and response output JSON
        for all failed unit tests of a given test data edge.

        :param test_details_file_path: 'file' path to the details for a single resource
        :param edge_details_file_path: 'file' path to the details for a single edge
        :param case_response: catalog of TRAPI request/response JSON from failed tests
        :return:
        """
        for test_id in case_response[edge_details_file_path]:
            with open(f"{test_details_file_path}-{test_id}-response.json", 'w') as response_file:
                response: Dict = case_response[edge_details_file_path][test_id]
                json.dump(response, response_file, indent=4)

    def save(self, test_summary: Dict, case_details: Dict, case_response: Dict):

        self._set_test_run_root_path()

        for edge_details_file_path in case_details:
            # Print out the test case details

            test_details_file_path = self._unit_test_report_filepath(edge_details_file_path)

            # Save Details from a given edge test data use case
            self.save_edge_details(test_details_file_path, edge_details_file_path, case_details)

            # Save TRAPI Request/Response IO details for unit tests from a given edge test data use case
            self.save_unit_test_trapi_io(test_details_file_path, edge_details_file_path, case_response)

        # Save Test Run Summary
        self.save_test_run_summary(test_summary)
