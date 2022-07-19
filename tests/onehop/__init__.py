"""
One Hop Test Harness
"""
from sys import stderr
from os import sep
from os.path import dirname, abspath

ONEHOP_TEST_DIRECTORY = abspath(dirname(__file__))
print(f"OneHop Test Directory: {ONEHOP_TEST_DIRECTORY}", file=stderr)

TEST_RESULTS_DIR = f"{ONEHOP_TEST_DIRECTORY}{sep}test_results"
print(f"OneHop Test Results Directory: {TEST_RESULTS_DIR}", file=stderr)
