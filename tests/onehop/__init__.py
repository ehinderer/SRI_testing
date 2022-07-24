"""
One Hop Test Harness
"""
from sys import stderr
from os import sep
from os.path import dirname, abspath

ONEHOP_TEST_DIRECTORY = abspath(dirname(__file__))
print(f"OneHop Test Directory: {ONEHOP_TEST_DIRECTORY}", file=stderr)

TEST_RESULTS_DB = "test_results"
# print(f"OneHop Test Results Database: {TEST_RESULTS_DB}", file=stderr)


def get_test_results_dir(db_name: str = TEST_RESULTS_DB) -> str:
    db_name = db_name if db_name else TEST_RESULTS_DB
    return f"{ONEHOP_TEST_DIRECTORY}{sep}{db_name}"


TEST_RESULTS_DIR = get_test_results_dir()
# print(f"OneHop Test Results Directory: {TEST_RESULTS_DIR}", file=stderr)
