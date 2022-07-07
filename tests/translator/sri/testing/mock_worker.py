#
# Mock Worker process script for 'processor.py' unit testing
#
from time import sleep
for pc in range(0, 101, 10):
    sleep(5)
    print("some test has PASSED [{pc:3d}%]".format(pc=pc))

# It is perilous to exit too quickly after finishing the worker task
# sleep(20)
