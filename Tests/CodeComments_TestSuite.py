import unittest, os, sys, logging
from Tests.test_CodeComments_class import TestLineClass
from Tests.test_CodeComments_class import TestCodeClass
from Tests.test_CodeComments_class import TestCodeBreakage
from Tests.test_CodeComments_Filenaming import TestNaming


def suite():

    suite = unittest.TestSuite()#
    suite.addTest(TestLineClass)
    #suite.addTest(TestLineClass('Tests critical class functionality.'))
    #suite.addTest(TestCodeClass('Tests code file type handling.'))
    #suite.addTest(TestCodeBreakage('Used to keep track of known points of failure.'))
    suite.addTest(TestNaming('Tests the naming and saving features.'))
    return suite


if __name__ == '__main__':
    #suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestNaming)
    unittest.TextTestRunner().run(suite())
