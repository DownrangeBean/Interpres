import unittest, os, sys, logging
from Tests.test_WordDocx_IODataCorrelation import TestTextExtraction
from Tests.test_WordDocx_Filenaming import TestNaming
import Interpres_Globals
from Util.Logging import get_logger

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)


def suite():
    test_directory = os.path.join(Interpres_Globals.ROOT_DIR, 'Testout', 'Word')
    if not os.path.isdir(test_directory):
        os.mkdir(test_directory, 0o777)
    else:
        for f in os.listdir(test_directory):
            try:
                os.remove(os.path.join(test_directory, f))
            except(PermissionError):
                sys.exit('Please close test file: ' + f)
    suite = unittest.TestSuite()
    suite.addTest(TestTextExtraction('tests the strings being collected and translated'))
    suite.addTest(TestNaming('Tests the naming saving and methods features'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
