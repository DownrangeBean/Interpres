import unittest, os, sys, logging
from Tests.test_WordDocx_IODataCorrelation import TestTextExtraction
from Tests.test_WordDocx_Filenaming import TestNaming
import Definitions

#logging.basicConfig(level=logging.ERROR, format=' %(asctime)s -  %(levelname)s  -  %(message)s')


def suite():
    test_directory = os.path.join(Definitions.ROOT_DIR, 'Testout', 'Word')
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
