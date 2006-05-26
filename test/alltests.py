import unittest
import sys
import settestpath

import feedParserTests
import entryTests

from unittest import TestSuite

def suite():
    # Append all test suites here:
    return TestSuite((feedParserTests.suite(), entryTests.suite()))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
