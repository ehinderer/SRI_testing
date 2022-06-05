"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional, Union, List, Dict, Tuple
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

SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN = re.compile(r"=+\sshort\stest\ssummary\sinfo\s=+")

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

TEST_CASE_IDENTIFIER_PATTERN = re.compile(
    r"^(?P<resource_id>[^#]+)(#(?P<edge_num>\d+))?(-(?P<test_id>.+))?$"
)


"""
TestReport is a multi-level indexed EdgeTestReport
dictionary of captured error messages, plus an error summary.
"""


# Edge entry from a resource's test data,
# annotated with test outcomes
class EdgeEntry:
    def __init__(
            self,
            # The contents of the original Edge
            # input data used to generate test cases.
            subject_category: str,
            object_category: str,
            predicate: str,
            subject_id: str,
            object_id: str
    ):
        self.data: Dict[
            # Controlled vocabulary 'field name' for Edge metadata and
            # error outcomes (the latter tagged with field name  'tests'?)
            str,
            Union[
                # For simple text Edge metadata, the value here is a string from the
                # original contents of the given Edge record from the input data file
                str,
                # if the above 'field name' is 'tests' then a 
                # dictionary of test results (i.e. error messages)
                # is provided here, indexed by unit test identifiers (e.g. by_subject)
                # or by the generic 'input' designation of error source.
                Dict[
                    # unit test specific tag, i.e. by_subject, etc.
                    # or the generic pretest 'input' validation tag
                    str,
                    Dict[
                        # error dictionary keys are in 
                        # ["PASSED", "FAILED", "SKIPPED", "WARNING"]
                        str,
                        # List of error messages (or empty list, if simply 'PASSED')
                        List[str]
                    ]
                ]
            ]
        ] = {
            "subject_category": subject_category,
            "object_category": object_category,
            "predicate": predicate,
            "subject": subject_id,
            "object": object_id,
            "tests": dict()
        }

    def get_data(self) -> Dict[str, Union[str, Dict[str, Dict[str, List[str]]]]]:
        return self.data

    def add_test_result(self, test_label: str, outcome: str, message: str):
        assert outcome in ["PASSED", "FAILED", "SKIPPED", "WARNING"]
        if not test_label:
            test_label = "input"
        if test_label not in self.data["tests"]:
            self.data["tests"][test_label] = dict()
        if outcome not in self.data["tests"][test_label]:
            self.data["tests"][test_label][outcome] = list()
        self.data["tests"][test_label][outcome].append(message)


class ResourceEntry:
    
    def __init__(self, component: str, resource_id):
        assert component in ["KP", "ARA"]
        self.component = component
        
        self.resource_id = resource_id

        # Ordered list of test data Edge entries with test reports,
        # numerically indexed by their order of appearance
        # in the input data file being tested
        self.edges: List[Optional[EdgeEntry]] = list()

    def get_edge_entry(
            self,
            current_edge_number: int
    ) -> EdgeEntry:

        # TODO: Stub implementation... Not really sure yet how best
        #       to set or access this Edge metadata, specified in
        #       the conftest.py, before the Pytest. Probably simply
        #       need to look persist it globally then look it up!
        if len(self.edges) <= current_edge_number:
            while len(self.edges) <= current_edge_number:
                self.edges.append(None)   # probably won't normally stay None, but...
            edge_entry: EdgeEntry = EdgeEntry(
                subject_category="UNKNOWN",
                object_category="UNKNOWN",
                predicate="UNKNOWN",
                subject_id="UNKNOWN",
                object_id="UNKNOWN",
            )
            self.edges[current_edge_number] = edge_entry

        return self.edges[current_edge_number]

    def add_test_result(
            self,
            edge_number: int,
            test_label: str,
            outcome: str,
            message: str
    ):
        edge_entry: EdgeEntry = self.get_edge_entry(edge_number)
        edge_entry.add_test_result(test_label, outcome, message)


class SRITestReport:

    def __init__(self):
        self.report: Dict[
            # component in ["KP", "ARA", "SUMMARY"] 
            # Components formerly tagged as "INPUT" should now be
            # assigned as coming in either from a KP or ARA
            # (as discerned by looking up the resource by identifier)
            str,  
            Dict[  # "component"
                # if dictionary key == "SUMMARY", then
                #    dictionary keys are in ["PASSED", "FAILED", "SKIPPED", "WARNING"]
                # else
                #    dictionary keys are the identifier of the resource
                #    being tested (of the KP or ARA), either the
                #    test_data_location URL, or just a local test file name
                str,
                Union[
                    # if SUMMARY, then
                    #   summary count values as strings
                    str,
                    # else the details about the KP or ARA
                    # resource deferenced by the above identifier
                    ResourceEntry
                ]
            ]
        ] = dict()

        # Simple multi-level Python object representing the report
        self._output: Optional[Dict] = None

    def get_resource_entry(
            self,
            component: str,
            resource_id: str
    ) -> ResourceEntry:
        
        assert component in ["KP", "ARA"]
        if component not in self.report:
            self.report[component] = dict()
            
        # Identifier of the Resource being tested (of the KP or ARA),
        # either the test_data_location URL, or a local test file name
        if resource_id not in self.report[component]:
            # Ordered list of reports for test data Edges,
            # numerically index by their order of appearance
            # in the input data file being tested
            self.report[component][resource_id] = ResourceEntry(component, resource_id)
            
        return self.report[component][resource_id]

    @staticmethod
    def parse_test_case_identifier(case: str) -> Tuple[str, int, str]:
        """
        Parse the test case identifier into its component parts:
        (KP/ARA) resource_id, edge_num, unit_test_id.

        A typical identifier may look something like this:

        Some_ARA|Some_KP#0-by_subject

        which consists of the following parts:

        resource_id:  Some_ARA|Some_KP
        edge_num:     0
        test_id:      by_subject

        :param case: composite identifier. as generated in conftest unit test setup
        :type: str
        :return: resource_id, edge_num, test_id
        :rtype: Tuple[str, str, str]
        """
        m = TEST_CASE_IDENTIFIER_PATTERN.match(case)
        if m:
            resource_id = m["resource_id"] if m["resource_id"] else case
            edge_num = int(m["edge_num"]) if m["edge_num"] else -1
            test_id = m["test_id"] if m["test_id"] else "input"
        else:
            resource_id = case
            edge_num = -1
            test_id = "input"

        return resource_id, edge_num, test_id

    def add_summary(self, p_num: str, f_num: str, s_num: str, w_num: str):
        """
        Add a summary record to the report.
        :param p_num: number of PASSED tests
        :type: str
        :param f_num:  number of FAILED tests
        :type: str
        :param s_num: number of SKIPPED tests
        :type: str
        :param w_num: number of test WARNING messages
        :type: str
        """
        if "SUMMARY" not in self.report:
            self.report["SUMMARY"] = {
                "PASSED": p_num if p_num else "0",
                "FAILED": f_num if f_num else "0",
                "SKIPPED": s_num if s_num else "0",
                "WARNING": w_num if w_num else "0"
            }

    def output(self, refresh: bool = False) -> Optional[Dict]:
        """
        Dump a simple Python object representation of the SRITestingReport.

        :param refresh: boolean flag, if True, then force a rebuilding of the
                        output object from the internal SRITestingReport representation.
        :type: bool
        :return: multi-level Python object representing the report.
        :rtype: Dict
        """
        if not self._output or refresh:
            self._output = dict()

            for component in ["KP", "ARA", "SUMMARY"]:
                self._output[component] = dict()
                if component == "SUMMARY":
                    for outcome in ["PASSED", "FAILED", "SKIPPED", "WARNING"]:
                        self._output["SUMMARY"][outcome] = self.report["SUMMARY"][outcome]
                else:
                    for resource_id, resource_entry in self.report[component].items():
                        self._output[component][resource_id]: List[Dict] = list()
                        for edge in resource_entry.edges:
                            # skip all empty EdgeEntry instances...
                            if not edge:
                                continue
                            self._output[component][resource_id].append(edge.get_data())

        return self._output


def get_component_by_resource(resource_id: str) -> Optional[str]:
    # TODO: Fix this! The resource component type is actually known
    #       during conftest.py Pytest pre-processing so look it up!
    return "KP"   # mock implementation


def parse_result(raw_report: str) -> Optional[SRITestReport]:
    """
    Extract summary of Pytest output as SRI Testing report.

    :param raw_report: str, raw Pytest stdout content from test run with the -r option.

    :return: TestReport, a structured summary of OneHopTestHarness test outcomes
    """
    if not raw_report:
        return None

    part = SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.split(raw_report)
    if len(part) > 1:
        output = part[-1].strip()
    else:
        output = part[0].strip()

    # This splits the test section of interest
    # into lines, to facilitate further processing
    top_level = output.replace('\r', '')
    top_level = top_level.split('\n')

    report: SRITestReport = SRITestReport()
    current_component = current_outcome = current_case = current_resource_id = current_test_id = "UNKNOWN"
    current_edge_number = -1
    for line in top_level:
        line = line.strip()  # spurious leading and trailing whitespace removed
        if not line:
            continue  # ignore blank lines
        psp = PYTEST_SUMMARY_PATTERN.match(line)
        if psp:
            # PyTest summary line encountered.
            report.add_summary(
                psp["passed"],
                psp["failed"],
                psp["skipped"],
                psp["warning"]
            )

        else:
            # all other lines are assumed to be PyTest unit test outcomes
            psf = PASSED_SKIPPED_FAILED_PATTERN.match(line)
            if psf:
                outcome: str = psf["outcome"]
                if outcome != current_outcome:
                    current_outcome = outcome

                case: Optional[str] = psf["case"]
                if case != current_case:
                    current_case = case
                    current_resource_id, current_edge_number, current_test_id = \
                        report.parse_test_case_identifier(current_case)

                component: Optional[str] = psf["component"]
                if not component:
                    component = get_component_by_resource(current_resource_id)
                if component != current_component:
                    current_component = component.upper()

                resource_entry: ResourceEntry = report.get_resource_entry(current_component, current_resource_id)

                tail: Optional[str] = psf["tail"]
                if tail:
                    # strip off spurious blanks in the tail message
                    tail = tail.strip()
                    resource_entry.add_test_result(current_edge_number, current_test_id, outcome, tail)
            else:
                resource_entry: ResourceEntry = report.get_resource_entry(current_component, current_resource_id)
                resource_entry.add_test_result(current_edge_number, current_test_id, current_outcome, line)

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
    
    def get_testrun_report(self) -> Optional[Union[str, Dict]]:
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
        return self._report.output()
    
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
