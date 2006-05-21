import unittest
import sys
import settestpath

import feedParserTests

def suite():
    # Append all test suites here:
    return unittest.TestSuite((feedParserTests.suite(),))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
