
import sys
import time
import unittest
import locomotive

import locomotive_tests

'''
This file is used to execute all of the unit tests.
Each of the test files in the tests/ directory becomes a test "suite"
which is assembled ino the alltests suite.
'''

if __name__ == "__main__":
    app_suite = unittest.makeSuite(locomotive_tests.app_test.AppTest, 'test')
    ca_suite  = unittest.makeSuite(locomotive_tests.category_associations_test.CategoryAssociationTest, 'test')
    fi_suite  = unittest.makeSuite(locomotive_tests.rss_item_test.RssItemTest, 'test')
    alltests  = unittest.TestSuite((app_suite, ca_suite, fi_suite))
    runner    = unittest.TextTestRunner()
    runner.run(alltests)
