import Definitions
import unittest
import os
import sys
import shutil

test_directory = Definitions.TEST_OUT_DIR
if not os.path.isdir(test_directory):
    os.mkdir(test_directory, 0o777)
else:
    shutil.rmtree(test_directory)

loader = unittest.defaultTestLoader
suite = loader.discover(Definitions.ROOT_DIR)
print(suite.__dict__)
runner = unittest.TextTestRunner(failfast=True)
runner.run(suite)
