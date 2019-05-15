import os
import logging


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if os.getenv('TEMP'):
    TEST_DIR = os.path.join(os.getenv('TEMP'),'Interpres', 'Tests')
else:
    TEST_DIR = os.path.join(ROOT_DIR, "Tests")
TEST_OUT_DIR = os.path.join(TEST_DIR, 'Tests_out')

VERBOSITY = logging.ERROR

