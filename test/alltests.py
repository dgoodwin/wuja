import unittest
import sys
import settestpath
import configureLogging

import feedParserTests
import entryTests
import notifierTests

from unittest import TestSuite

def suite():
    # Append all test suites here:
    return TestSuite((feedParserTests.suite(),
        entryTests.suite(),
        notifierTests.suite()
    ))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
